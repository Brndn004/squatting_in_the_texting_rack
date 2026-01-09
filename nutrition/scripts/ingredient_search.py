#!/usr/bin/env python3
"""Search reverse-lookup database for ingredients by name.

Searches the ingredient_lookup.json database for ingredients matching
a query string and returns ranked results with FDC IDs.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple

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


def _load_lookup_database() -> Dict[str, int]:
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


def _rank_matches(query: str, lookup_data: Dict[str, int]) -> List[Tuple[int, str, int]]:
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


def display_results(matches: List[Tuple[int, str, int]]) -> None:
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


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Search ingredient database by name"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Ingredient name to search for",
    )
    args = parser.parse_args()

    # Load lookup database
    try:
        lookup_data = _load_lookup_database()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(str(e))
        sys.exit(1)

    if not lookup_data:
        logger.warning("Lookup database is empty. Run usda_lookup.py to add ingredients.")
        sys.exit(0)

    # Search and rank matches
    matches = _rank_matches(args.query, lookup_data)

    # Display results
    display_results(matches)


if __name__ == "__main__":
    main()

