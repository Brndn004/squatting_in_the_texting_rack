#!/usr/bin/env python3
"""USDA Food Data Central lookup script.

Searches for Foundation ingredients in the USDA FoodData Central database
and saves full nutrition data as JSON files.
"""

import argparse
import logging
import sys
import typing
from pathlib import Path

import requests

import usda_lib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def display_search_results(foods: typing.List[typing.Dict[str, typing.Any]]) -> None:
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


def get_user_selection(foods: typing.List[typing.Dict[str, typing.Any]]) -> typing.Dict[str, typing.Any]:
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


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Search and download USDA Foundation ingredient data"
    )
    
    # Create mutually exclusive group for search vs direct ID lookup
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--search",
        nargs="+",
        type=str,
        metavar="TERM",
        help="Search for ingredient by name (can be multiple words)",
    )
    group.add_argument(
        "--id",
        type=int,
        metavar="FDC_ID",
        help="Directly fetch ingredient by FDC ID",
    )
    
    args = parser.parse_args()

    # Get API key from environment
    try:
        api_key = usda_lib.get_api_key()
    except usda_lib.UsdaApiKeyError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Handle direct FDC ID lookup
    if args.id is not None:
        fdc_id = args.id
        logger.info(f"Fetching ingredient details for FDC ID {fdc_id}...")
        
        try:
            food_data = usda_lib.get_food_details(fdc_id, api_key)
        except requests.RequestException as e:
            print(f"Error: Failed to fetch details for FDC ID {fdc_id}: {e}")
            sys.exit(1)
        
        # Extract description from food data
        description = food_data.get("description", f"FDC ID {fdc_id}")
        
        # Generate filename
        filename = f"{fdc_id}.json"
        filepath = Path(__file__).parent.parent / "ingredients" / filename

        # Save as pretty-printed JSON
        try:
            usda_lib.save_ingredient_file(food_data, filepath)
        except OSError as e:
            print(f"Error: Failed to save file to {filepath}: {e}")
            sys.exit(1)

        # Update reverse-lookup database
        usda_lib.update_reverse_lookup(fdc_id, description)

        logger.info(f"Description: {description}")
        return

    # Handle search mode
    query = " ".join(args.search)
    logger.info(f"Searching for '{query}' in USDA FoodData Central...")

    # Search for ingredients with priority ordering
    try:
        search_results = usda_lib.search_ingredient_prioritized(query, api_key)
    except requests.RequestException as e:
        print(f"Error: Search failed: {e}")
        sys.exit(1)

    foods = search_results.get("foods", [])

    if not foods:
        logger.error(f"No foods found for '{query}'")
        sys.exit(1)

    # Sort foods by data type priority
    foods = usda_lib.sort_foods_by_priority(foods)

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
        food_data = usda_lib.get_food_details(fdc_id, api_key)
    except requests.RequestException as e:
        print(f"Error: Failed to fetch details for FDC ID {fdc_id}: {e}")
        sys.exit(1)

    # Generate filename
    filename = f"{fdc_id}.json"
    filepath = Path(__file__).parent.parent / "ingredients" / filename

    # Save as pretty-printed JSON
    try:
        usda_lib.save_ingredient_file(food_data, filepath)
    except OSError as e:
        print(f"Error: Failed to save file to {filepath}: {e}")
        sys.exit(1)

    # Update reverse-lookup database
    usda_lib.update_reverse_lookup(fdc_id, description)

    logger.info(f"Description: {description}")


if __name__ == "__main__":
    main()
