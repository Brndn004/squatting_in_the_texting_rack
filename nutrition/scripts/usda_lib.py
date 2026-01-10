"""USDA Food Data Central library module.

Business logic for searching and retrieving USDA FoodData Central data.
This module contains pure functions without user interaction.
"""

import json
import os
import typing
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

import requests


class UsdaApiKeyError(Exception):
    """Exception raised when USDA API key is not found in environment."""
    pass

# Constants
_API_KEY_ENV_VAR = "USDA_API_KEY"
_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
_SEARCH_ENDPOINT = f"{_BASE_URL}/foods/search"
_DETAILS_ENDPOINT = f"{_BASE_URL}/food"
_DEFAULT_PAGE_SIZE = 20
_JSON_INDENT = 4


def get_api_key() -> str:
    """Get USDA API key from environment variable.

    Returns:
        USDA API key string.

    Raises:
        UsdaApiKeyError: If API key is not found in environment.
    """
    api_key = os.getenv(_API_KEY_ENV_VAR)
    if not api_key:
        error_message = (
            f"USDA API key not found. Please set the {_API_KEY_ENV_VAR} "
            "environment variable.\n\n"
            f"To set it, add this line to your ~/.zshrc file:\n"
            f"export {_API_KEY_ENV_VAR}=your_api_key_here\n\n"
            f"Then reload your shell configuration:\n"
            f"source ~/.zshrc"
        )
        raise UsdaApiKeyError(error_message)
    return api_key


def _get_ingredients_dir() -> Path:
    """Get the ingredients directory path.

    Returns:
        Path to the ingredients directory.
    """
    return Path(__file__).parent.parent / "ingredients"


def _get_logs_dir() -> Path:
    """Get the logs directory path.

    Returns:
        Path to the logs directory.
    """
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


def _format_api_call_for_logging(url: str, params: typing.Dict[str, typing.Any]) -> str:
    """Format API call for logging, masking the API key.
    
    Args:
        url: API endpoint URL.
        params: Request parameters.
        
    Returns:
        Formatted string showing the API call.
    """
    # Create a copy of params with masked API key
    masked_params = params.copy()
    if "api_key" in masked_params:
        masked_params["api_key"] = "***MASKED***"
    
    # Build the full URL with parameters
    param_string = urlencode(masked_params)
    full_url = f"{url}?{param_string}"
    
    return full_url


def _save_error_log(
    url: str,
    params: typing.Dict[str, typing.Any],
    response: typing.Optional[requests.Response],
    error: Exception,
    operation: str
) -> Path:
    """Save error log to file.
    
    Args:
        url: API endpoint URL.
        params: Request parameters.
        response: Response object (if available).
        error: Exception that occurred.
        operation: Description of the operation (e.g., "search", "get_details").
        
    Returns:
        Path to the saved log file.
    """
    logs_dir = _get_logs_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create log entry
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "url": url,
        "params": {k: ("***MASKED***" if k == "api_key" else v) for k, v in params.items()},
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    # Add response data if available
    if response is not None:
        log_data["response_status_code"] = response.status_code
        log_data["response_headers"] = dict(response.headers)
        try:
            log_data["response_body"] = response.text
        except Exception:
            log_data["response_body"] = "Unable to read response body"
    else:
        log_data["response_status_code"] = None
        log_data["response_body"] = None
    
    # Save to file
    log_filename = f"usda_api_error_{operation}_{timestamp}.json"
    log_filepath = logs_dir / log_filename
    
    with open(log_filepath, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    return log_filepath


def _get_data_type_priority(data_type: str) -> int:
    """Get priority score for data type sorting.

    Lower numbers = higher priority.

    Args:
        data_type: USDA data type string.

    Returns:
        Priority score (0-4).
    """
    priority_map = {
        "Foundation": 0,
        "Survey (FNDDS)": 1,
        "SR Legacy": 2,
        "Experimental": 3,
        "Branded": 4,
    }
    return priority_map.get(data_type, 99)


def search_ingredient(
    query: str, api_key: str, data_types: typing.Optional[typing.List[str]] = None
) -> typing.Dict[str, typing.Any]:
    """Search for ingredients matching the query.

    Args:
        query: Search term for ingredient name.
        api_key: USDA API key.
        data_types: Optional list of data types to filter. If None, searches all types.

    Returns:
        JSON response containing search results.

    Raises:
        requests.RequestException: If the API request fails.
    """
    params = {
        "api_key": api_key,
        "query": query,
        "pageSize": _DEFAULT_PAGE_SIZE,
    }
    
    if data_types:
        params["dataType"] = data_types

    response = None
    try:
        response = requests.get(_SEARCH_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        api_call = _format_api_call_for_logging(_SEARCH_ENDPOINT, params)
        print(f"Failed to search for '{query}': {e}")
        print(f"API call: {api_call}")
        
        # Save error log
        log_filepath = _save_error_log(_SEARCH_ENDPOINT, params, response, e, "search")
        print(f"Error log saved to: {log_filepath}")
        
        raise


def search_ingredient_prioritized(query: str, api_key: str) -> typing.Dict[str, typing.Any]:
    """Search for ingredients with priority ordering.

    Tries multiple search strategies to find Foundation foods:
    1. Search priority types (Foundation/Survey/SR Legacy) with original query
    2. Try alternative query variations (reversed word order, single word)
    3. Search all types and filter client-side
    4. Fall back to Branded if no priority results

    Args:
        query: Search term for ingredient name.
        api_key: USDA API key.

    Returns:
        JSON response containing search results, with foods sorted by priority.
    """
    priority_types = ["Foundation", "Survey (FNDDS)", "SR Legacy"]
    
    # Strategy 1: Search priority types with original query
    print(f"Searching priority data types: {', '.join(priority_types)}")
    try:
        results = search_ingredient(query, api_key, data_types=priority_types)
        foods = results.get("foods", [])
        total_hits = results.get("totalHits", 0)
        
        if foods or total_hits > 0:
            print(
                f"Found {len(foods)} result(s) in priority data types "
                f"(total available: {total_hits})"
            )
            return results
    except requests.RequestException as e:
        print(f"Priority search failed: {e}")
    
    # Strategy 2: Try alternative query variations for priority types
    query_words = query.split()
    if len(query_words) > 1:
        # Try reversed word order (e.g., "milk whole" instead of "whole milk")
        alt_query = " ".join(reversed(query_words))
        print(f"Trying alternative query: '{alt_query}'")
        try:
            results = search_ingredient(alt_query, api_key, data_types=priority_types)
            foods = results.get("foods", [])
            if foods:
                print(f"Found {len(foods)} result(s) with alternative query")
                return results
        except requests.RequestException:
            pass
        
        # Try just the main word (e.g., "milk" from "whole milk")
        # Filter client-side for words containing "whole"
        main_word = query_words[-1] if len(query_words) > 1 else query_words[0]
        print(f"Trying simplified query: '{main_word}'")
        try:
            results = search_ingredient(main_word, api_key, data_types=priority_types)
            foods = results.get("foods", [])
            if foods:
                # Filter for foods containing all query words
                query_lower = query.lower()
                filtered_foods = [
                    f for f in foods
                    if all(word.lower() in f.get("description", "").lower() 
                           for word in query_words)
                ]
                if filtered_foods:
                    print(
                        f"Found {len(filtered_foods)} result(s) with simplified query"
                    )
                    results["foods"] = filtered_foods
                    return results
        except requests.RequestException:
            pass
    
    # Strategy 3: Search all types and filter client-side
    print("Searching all data types...")
    try:
        results = search_ingredient(query, api_key, data_types=None)
        foods = results.get("foods", [])
        
        if not foods:
            print("No results found")
            return results
        
        # Filter and prioritize: Foundation > Survey > SR Legacy > Experimental > Branded
        priority_foods = [
            f for f in foods 
            if f.get("dataType") in priority_types
        ]
        branded_foods = [
            f for f in foods 
            if f.get("dataType") == "Branded"
        ]
        other_foods = [
            f for f in foods 
            if f.get("dataType") not in priority_types + ["Branded"]
        ]
        
        # Reconstruct results with priority foods first
        sorted_foods = priority_foods + other_foods + branded_foods
        
        if priority_foods:
            print(
                f"Found {len(priority_foods)} priority result(s) "
                f"(Foundation/Survey/SR Legacy) out of {len(foods)} total"
            )
        elif branded_foods:
            print(
                f"Found {len(branded_foods)} Branded result(s) "
                f"(no priority types found)"
            )
        
        # Update the results with sorted foods
        results["foods"] = sorted_foods
        return results
        
    except requests.RequestException as e:
        print(f"Search failed: {e}")
        raise


def get_food_details(fdc_id: int, api_key: str) -> typing.Dict[str, typing.Any]:
    """Get full details for a specific FDC ID.

    Args:
        fdc_id: FoodData Central ID.
        api_key: USDA API key.

    Returns:
        JSON response containing full food details.

    Raises:
        requests.RequestException: If the API request fails.
    """
    url = f"{_DETAILS_ENDPOINT}/{fdc_id}"
    params = {
        "api_key": api_key,
        "format": "full",
    }

    response = None
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        api_call = _format_api_call_for_logging(url, params)
        print(f"Failed to fetch details for FDC ID {fdc_id}: {e}")
        print(f"API call: {api_call}")
        
        # Save error log
        log_filepath = _save_error_log(url, params, response, e, f"get_details_fdc_{fdc_id}")
        print(f"Error log saved to: {log_filepath}")
        
        raise


def sort_foods_by_priority(foods: typing.List[typing.Dict[str, typing.Any]]) -> typing.List[typing.Dict[str, typing.Any]]:
    """Sort foods by data type priority.

    Args:
        foods: List of food items from search results.

    Returns:
        Sorted list of food items.
    """
    return sorted(
        foods,
        key=lambda f: (
            _get_data_type_priority(f.get("dataType", "")),
            f.get("description", ""),
        ),
    )


def save_ingredient_file(food_data: typing.Dict[str, typing.Any], filepath: Path) -> None:
    """Save food data to a JSON file.

    Args:
        food_data: Food data dictionary to save.
        filepath: Path where the file should be saved.

    Raises:
        OSError: If file cannot be written.
    """
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(food_data, f, indent=_JSON_INDENT, ensure_ascii=False)
        print(f"Saved to: {filepath}")
    except OSError as e:
        print(f"Failed to save file to {filepath}: {e}")
        raise


def update_reverse_lookup(fdc_id: int, description: str) -> None:
    """Update the reverse-lookup database with a new ingredient.

    Args:
        fdc_id: FoodData Central ID.
        description: Ingredient description/name.
    """
    lookup_file = _get_ingredients_dir() / "ingredient_lookup.json"
    
    # Load existing lookup data
    lookup_data = {}
    if lookup_file.exists():
        try:
            with open(lookup_file, "r", encoding="utf-8") as f:
                lookup_data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Failed to load lookup database: {e}")
    
    # Add or update entry
    lookup_data[description] = fdc_id
    
    # Save updated lookup data
    try:
        with open(lookup_file, "w", encoding="utf-8") as f:
            json.dump(lookup_data, f, indent=2, ensure_ascii=False)
        print(f"Updated reverse-lookup database: {description} -> {fdc_id}")
    except OSError as e:
        print(f"Failed to update lookup database: {e}")

