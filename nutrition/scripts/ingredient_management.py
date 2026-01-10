#!/usr/bin/env python3
"""Manage ingredients in the local database.

Interactive REPL for searching and deleting ingredients.
"""

import json
import logging
import sys
import typing

import ingredient_management_lib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def display_results(matches: typing.List[typing.Tuple[int, str, int]]) -> None:
    """Display search results to the user.

    Args:
        matches: List of (score, description, fdc_id) tuples.
    """
    if not matches:
        print("No matching ingredients found.")
        return
    
    print(f"\nFound {len(matches)} matching ingredient(s):\n")
    
    for i, (score, description, fdc_id) in enumerate(matches, 1):
        # Show relevance indicator
        if score == 3:
            indicator = "★"
        elif score == 2:
            indicator = "→"
        else:
            indicator = "•"
        
        print(f"{i}. {indicator} [{fdc_id}] {description}")
        print(f"   File: {fdc_id}.json")


def get_selected_ingredient(
    matches: typing.List[typing.Tuple[int, str, int]], selection: str
) -> typing.Optional[typing.Tuple[str, int]]:
    """Get the selected ingredient from matches.

    Args:
        matches: List of (score, description, fdc_id) tuples.
        selection: User input (should be a number).

    Returns:
        Tuple of (description, fdc_id) if valid selection, None otherwise.
    """
    try:
        index = int(selection.strip()) - 1
        if 0 <= index < len(matches):
            _, description, fdc_id = matches[index]
            return (description, fdc_id)
        else:
            print(f"Invalid selection. Please enter a number between 1 and {len(matches)}.")
            return None
    except ValueError:
        print(f"Invalid input. Please enter a number.")
        return None




def _print_usage() -> None:
    """Print usage instructions."""
    print("\nIngredient Management")
    print("=" * 50)
    print("Usage:")
    print("  - Enter an ingredient name to search")
    print("  - Enter a number to select an ingredient")
    print("  - Type 'delete' to delete the selected ingredient")
    print("  - Press Ctrl+C to exit")
    print("=" * 50 + "\n")


def main() -> None:
    """Main entry point for the script."""
    # Load lookup database
    try:
        lookup_data = ingredient_management_lib.load_lookup_database()
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.error(str(e))
        sys.exit(1)

    if not lookup_data:
        logger.warning("Lookup database is empty. Run usda_lookup.py to add ingredients.")
        sys.exit(0)

    # Print usage instructions
    _print_usage()

    # REPL loop
    current_matches: typing.List[typing.Tuple[int, str, int]] = []
    selected_ingredient: typing.Optional[typing.Tuple[str, int]] = None

    try:
        while True:
            try:
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                
                # Handle delete command
                if user_input.lower() == "delete":
                    if selected_ingredient is None:
                        print("No ingredient selected. Search and select an ingredient first.")
                        continue
                    
                    description, fdc_id = selected_ingredient
                    print(f"\nDeleting: [{fdc_id}] {description}")
                    
                    try:
                        ingredient_management_lib.delete_ingredient(description, fdc_id)
                        print("✓ Successfully deleted.")
                        # Reload lookup database after deletion
                        try:
                            lookup_data = ingredient_management_lib.load_lookup_database()
                        except (FileNotFoundError, OSError):
                            logger.error("Failed to reload lookup database")
                            sys.exit(1)
                        # Clear selection and matches
                        selected_ingredient = None
                        current_matches = []
                    except (FileNotFoundError, OSError) as e:
                        print(f"✗ Deletion failed: {e}")
                    print()
                    continue
                
                # Try to parse as a number (selection)
                try:
                    selection_num = int(user_input)
                    if not current_matches:
                        print("No search results available. Search for an ingredient first.")
                        continue
                    
                    selected = get_selected_ingredient(current_matches, user_input)
                    if selected:
                        selected_ingredient = selected
                        description, fdc_id = selected
                        print(f"\n✓ Selected: [{fdc_id}] {description}")
                        print("Type 'delete' to delete this ingredient.\n")
                    continue
                except ValueError:
                    pass  # Not a number, treat as search query
                
                # Treat as search query
                matches = ingredient_management_lib.rank_matches(user_input, lookup_data)
                current_matches = matches
                selected_ingredient = None  # Clear selection on new search
                
                display_results(matches)
                
                if matches:
                    print("\nEnter a number to select an ingredient, or search again.")
                print()
                
            except EOFError:
                # Handle Ctrl+D
                print("\n")
                break
                
    except KeyboardInterrupt:
        print("\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

