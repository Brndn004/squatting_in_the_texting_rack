#!/usr/bin/env python3
"""Manage ingredients in the local database.

Interactive REPL for searching and deleting ingredients.
"""

import json
import logging
import sys
import typing
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _get_ingredients_dir() -> Path:
    """Get the ingredients directory path.

    Returns:
        Path to the ingredients directory.
    """
    return Path(__file__).parent.parent / "ingredients"


def _load_lookup_database() -> typing.Dict[str, int]:
    """Load the reverse-lookup database.

    Returns:
        Dictionary mapping ingredient descriptions to FDC IDs.

    Raises:
        FileNotFoundError: If lookup database doesn't exist.
        json.JSONDecodeError: If lookup database is invalid JSON.
    """
    lookup_file = _get_ingredients_dir() / "ingredient_lookup.json"
    
    if not lookup_file.exists():
        raise FileNotFoundError(
            f"Lookup database not found at {lookup_file}. "
            "Run usda_lookup.py to add ingredients first."
        )
    
    try:
        with open(lookup_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in lookup database: {e}")
        raise


def _save_lookup_database(lookup_data: typing.Dict[str, int]) -> None:
    """Save the reverse-lookup database.

    Args:
        lookup_data: Dictionary mapping ingredient descriptions to FDC IDs.

    Raises:
        OSError: If file cannot be written.
    """
    lookup_file = _get_ingredients_dir() / "ingredient_lookup.json"
    
    try:
        with open(lookup_file, "w", encoding="utf-8") as f:
            json.dump(lookup_data, f, indent=2, ensure_ascii=False)
    except OSError as e:
        logger.error(f"Failed to save lookup database: {e}")
        raise


def _rank_matches(query: str, lookup_data: typing.Dict[str, int]) -> typing.List[typing.Tuple[int, str, int]]:
    """Rank ingredient matches by relevance.

    Args:
        query: Search query (lowercased).
        lookup_data: Dictionary mapping descriptions to FDC IDs.

    Returns:
        List of tuples (score, description, fdc_id) sorted by score (highest first).
        Score: 3 = exact match, 2 = starts with, 1 = contains, 0 = no match.
    """
    query_lower = query.lower()
    matches = []
    
    for description, fdc_id in lookup_data.items():
        desc_lower = description.lower()
        score = 0
        
        if desc_lower == query_lower:
            score = 3  # Exact match
        elif desc_lower.startswith(query_lower):
            score = 2  # Starts with query
        elif query_lower in desc_lower:
            score = 1  # Contains query
        
        if score > 0:
            matches.append((score, description, fdc_id))
    
    # Sort by score (descending), then by description (ascending)
    matches.sort(key=lambda x: (-x[0], x[1]))
    return matches


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


def delete_ingredient(description: str, fdc_id: int) -> bool:
    """Delete an ingredient from the database.

    Args:
        description: Ingredient description.
        fdc_id: FoodData Central ID.

    Returns:
        True if deletion was successful, False otherwise.
    """
    ingredients_dir = _get_ingredients_dir()
    
    # Delete JSON file
    json_file = ingredients_dir / f"{fdc_id}.json"
    if json_file.exists():
        try:
            json_file.unlink()
            logger.info(f"Deleted file: {json_file}")
        except OSError as e:
            logger.error(f"Failed to delete file {json_file}: {e}")
            return False
    else:
        logger.warning(f"File not found: {json_file}")
    
    # Remove from lookup database
    try:
        lookup_data = _load_lookup_database()
        if description in lookup_data:
            del lookup_data[description]
            _save_lookup_database(lookup_data)
            logger.info(f"Removed from lookup database: {description}")
        else:
            logger.warning(f"Entry not found in lookup database: {description}")
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to update lookup database: {e}")
        return False
    
    return True


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
        lookup_data = _load_lookup_database()
    except (FileNotFoundError, json.JSONDecodeError) as e:
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
                    
                    if delete_ingredient(description, fdc_id):
                        print("✓ Successfully deleted.")
                        # Reload lookup database after deletion
                        lookup_data = _load_lookup_database()
                        # Clear selection and matches
                        selected_ingredient = None
                        current_matches = []
                    else:
                        print("✗ Deletion failed.")
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
                matches = _rank_matches(user_input, lookup_data)
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

