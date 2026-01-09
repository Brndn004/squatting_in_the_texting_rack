#!/usr/bin/env python3
"""USDA Food Data Central lookup script.

Searches for Foundation ingredients in the USDA FoodData Central database
and saves full nutrition data as JSON files.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Constants
_API_KEY_ENV_VAR = "USDA_API_KEY"
_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
_SEARCH_ENDPOINT = f"{_BASE_URL}/foods/search"
_DETAILS_ENDPOINT = f"{_BASE_URL}/food"
_DEFAULT_PAGE_SIZE = 20
_JSON_INDENT = 4

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _get_api_key() -> str:
    """Get USDA API key from environment variable.

    Returns:
        USDA API key string.

    Raises:
        SystemExit: If API key is not found in environment.
    """
    api_key = os.getenv(_API_KEY_ENV_VAR)
    if not api_key:
        logger.error(
            f"USDA API key not found. Please set the {_API_KEY_ENV_VAR} "
            "environment variable."
        )
        logger.info(
            f"\nTo set it, add this line to your ~/.zshrc file:\n"
            f"export {_API_KEY_ENV_VAR}=your_api_key_here\n"
            f"\nThen reload your shell configuration:\n"
            f"source ~/.zshrc"
        )
        sys.exit(1)
    return api_key


def _get_ingredients_dir() -> Path:
    """Get the ingredients directory path.

    Returns:
        Path to the ingredients directory.
    """
    return Path(__file__).parent.parent / "ingredients"


def search_ingredient(
    query: str, api_key: str, data_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Search for ingredients matching the query.

    Args:
        query: Search term for ingredient name.
        api_key: USDA API key.
        data_types: Optional list of data types to filter. If None, searches all types.

    Returns:
        JSON response containing search results.

    Raises:
        requests.HTTPError: If the API request fails.
    """
    params = {
        "api_key": api_key,
        "query": query,
        "pageSize": _DEFAULT_PAGE_SIZE,
    }
    
    if data_types:
        params["dataType"] = data_types

    try:
        response = requests.get(_SEARCH_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to search for '{query}': {e}")
        raise


def search_ingredient_prioritized(query: str, api_key: str) -> Dict[str, Any]:
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
    logger.info(f"Searching priority data types: {', '.join(priority_types)}")
    try:
        results = search_ingredient(query, api_key, data_types=priority_types)
        foods = results.get("foods", [])
        total_hits = results.get("totalHits", 0)
        
        if foods or total_hits > 0:
            logger.info(
                f"Found {len(foods)} result(s) in priority data types "
                f"(total available: {total_hits})"
            )
            return results
    except requests.RequestException as e:
        logger.warning(f"Priority search failed: {e}")
    
    # Strategy 2: Try alternative query variations for priority types
    query_words = query.split()
    if len(query_words) > 1:
        # Try reversed word order (e.g., "milk whole" instead of "whole milk")
        alt_query = " ".join(reversed(query_words))
        logger.info(f"Trying alternative query: '{alt_query}'")
        try:
            results = search_ingredient(alt_query, api_key, data_types=priority_types)
            foods = results.get("foods", [])
            if foods:
                logger.info(f"Found {len(foods)} result(s) with alternative query")
                return results
        except requests.RequestException:
            pass
        
        # Try just the main word (e.g., "milk" from "whole milk")
        # Filter client-side for words containing "whole"
        main_word = query_words[-1] if len(query_words) > 1 else query_words[0]
        logger.info(f"Trying simplified query: '{main_word}'")
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
                    logger.info(
                        f"Found {len(filtered_foods)} result(s) with simplified query"
                    )
                    results["foods"] = filtered_foods
                    return results
        except requests.RequestException:
            pass
    
    # Strategy 3: Search all types and filter client-side
    logger.info("Searching all data types...")
    try:
        results = search_ingredient(query, api_key, data_types=None)
        foods = results.get("foods", [])
        
        if not foods:
            logger.info("No results found")
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
            logger.info(
                f"Found {len(priority_foods)} priority result(s) "
                f"(Foundation/Survey/SR Legacy) out of {len(foods)} total"
            )
        elif branded_foods:
            logger.info(
                f"Found {len(branded_foods)} Branded result(s) "
                f"(no priority types found)"
            )
        
        # Update the results with sorted foods
        results["foods"] = sorted_foods
        return results
        
    except requests.RequestException as e:
        logger.error(f"Search failed: {e}")
        raise


def get_food_details(fdc_id: int, api_key: str) -> Dict[str, Any]:
    """Get full details for a specific FDC ID.

    Args:
        fdc_id: FoodData Central ID.
        api_key: USDA API key.

    Returns:
        JSON response containing full food details.

    Raises:
        requests.HTTPError: If the API request fails.
    """
    url = f"{_DETAILS_ENDPOINT}/{fdc_id}"
    params = {
        "api_key": api_key,
        "format": "full",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch details for FDC ID {fdc_id}: {e}")
        raise


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


def _sort_foods_by_priority(foods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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


def display_search_results(foods: List[Dict[str, Any]]) -> None:
    """Display search results to the user.

    Args:
        foods: List of food items from search results.
    """
    logger.info(f"\nFound {len(foods)} results:\n")
    for i, food in enumerate(foods, 1):
        fdc_id = food.get("fdcId", "N/A")
        description = food.get("description", "N/A")
        data_type = food.get("dataType", "N/A")
        print(f"{i}. [{fdc_id}] {description} ({data_type})")


def get_user_selection(foods: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Prompt user to select an ingredient from search results.

    Args:
        foods: List of food items to choose from.

    Returns:
        Selected food item dictionary.

    Raises:
        KeyboardInterrupt: If user cancels the selection.
    """
    while True:
        try:
            choice = input(f"\nSelect ingredient (1-{len(foods)}): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(foods):
                return foods[index]
            logger.warning(f"Please enter a number between 1 and {len(foods)}")
        except ValueError:
            logger.warning("Please enter a valid number")
        except KeyboardInterrupt:
            logger.info("\nCancelled.")
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
            logger.warning(f"Failed to load lookup database: {e}")
    
    # Add or update entry
    lookup_data[description] = fdc_id
    
    # Save updated lookup data
    try:
        with open(lookup_file, "w", encoding="utf-8") as f:
            json.dump(lookup_data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Updated reverse-lookup database: {description} -> {fdc_id}")
    except OSError as e:
        logger.warning(f"Failed to update lookup database: {e}")


def save_ingredient_file(food_data: Dict[str, Any], filepath: Path) -> None:
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
        logger.info(f"Saved to: {filepath}")
    except OSError as e:
        logger.error(f"Failed to save file to {filepath}: {e}")
        raise


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Search and download USDA Foundation ingredient data"
    )
    parser.add_argument(
        "ingredient",
        nargs="+",
        type=str,
        help="Name of the ingredient to search for (can be multiple words)",
    )
    args = parser.parse_args()

    # Get API key from environment
    try:
        api_key = _get_api_key()
    except SystemExit:
        sys.exit(1)

    query = " ".join(args.ingredient)
    logger.info(f"Searching for '{query}' in USDA FoodData Central...")

    # Search for ingredients with priority ordering
    try:
        search_results = search_ingredient_prioritized(query, api_key)
    except requests.RequestException:
        sys.exit(1)

    foods = search_results.get("foods", [])

    if not foods:
        logger.error(f"No foods found for '{query}'")
        sys.exit(1)

    # Sort foods by data type priority
    foods = _sort_foods_by_priority(foods)

    # Display results
    display_search_results(foods)

    # Get user selection
    try:
        selected = get_user_selection(foods)
    except KeyboardInterrupt:
        sys.exit(0)

    fdc_id = selected.get("fdcId")
    description = selected.get("description", "")

    if not fdc_id:
        logger.error("Selected food item missing FDC ID")
        sys.exit(1)

    logger.info(f"\nFetching full details for FDC ID {fdc_id}...")

    # Get full details
    try:
        food_data = get_food_details(fdc_id, api_key)
    except requests.RequestException:
        sys.exit(1)

    # Generate filename
    filename = f"{fdc_id}.json"
    filepath = _get_ingredients_dir() / filename

    # Save as pretty-printed JSON
    try:
        save_ingredient_file(food_data, filepath)
    except OSError:
        sys.exit(1)

    # Update reverse-lookup database
    update_reverse_lookup(fdc_id, description)

    logger.info(f"Description: {description}")


if __name__ == "__main__":
    main()
