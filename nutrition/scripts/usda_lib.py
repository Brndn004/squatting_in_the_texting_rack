"""USDA Food Data Central library module.

Business logic for searching and retrieving USDA FoodData Central data.
This module contains pure functions without user interaction.
"""

import json
import typing
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

import requests

# Constants
_API_KEY_ENV_VAR = "USDA_API_KEY"
_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
_SEARCH_ENDPOINT = f"{_BASE_URL}/foods/search"
_DETAILS_ENDPOINT = f"{_BASE_URL}/food"
_DEFAULT_PAGE_SIZE = 20
_JSON_INDENT = 4


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

