"""Ingredient management library module.

Business logic for managing local ingredient database.
This module contains pure functions without user interaction.
"""

import json
import typing
from pathlib import Path


def _get_ingredients_dir() -> Path:
    """Get the ingredients directory path.

    Returns:
        Path to the ingredients directory.
    """
    return Path(__file__).parent.parent / "ingredients"


def load_lookup_database() -> typing.Dict[str, int]:
    """Load the reverse-lookup database.

    Returns:
        Dictionary mapping ingredient descriptions to FDC IDs.

    Raises:
        FileNotFoundError: If lookup database doesn't exist.
        json.JSONDecodeError: If lookup database is invalid JSON.
        OSError: If file cannot be read.
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
        print(f"Invalid JSON in lookup database: {e}")
        raise
    except OSError as e:
        print(f"Failed to read lookup database: {e}")
        raise


def save_lookup_database(lookup_data: typing.Dict[str, int]) -> None:
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
        print(f"Failed to save lookup database: {e}")
        raise


def rank_matches(query: str, lookup_data: typing.Dict[str, int]) -> typing.List[typing.Tuple[int, str, int]]:
    """Rank ingredient matches by relevance.

    Args:
        query: Search query (will be lowercased internally).
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


def delete_ingredient(description: str, fdc_id: int) -> None:
    """Delete an ingredient from the database.

    Deletes the ingredient JSON file and removes the entry from the lookup database.

    Args:
        description: Ingredient description.
        fdc_id: FoodData Central ID.

    Raises:
        OSError: If file deletion fails or lookup database cannot be updated.
        FileNotFoundError: If lookup database doesn't exist.
        json.JSONDecodeError: If lookup database is invalid JSON.
    """
    ingredients_dir = _get_ingredients_dir()
    
    # Delete JSON file
    json_file = ingredients_dir / f"{fdc_id}.json"
    if json_file.exists():
        try:
            json_file.unlink()
            print(f"Deleted file: {json_file}")
        except OSError as e:
            print(f"Failed to delete file {json_file}: {e}")
            raise
    else:
        print(f"File not found: {json_file}")
    
    # Remove from lookup database
    lookup_data = load_lookup_database()
    if description in lookup_data:
        del lookup_data[description]
        save_lookup_database(lookup_data)
        print(f"Removed from lookup database: {description}")
    else:
        print(f"Entry not found in lookup database: {description}")

