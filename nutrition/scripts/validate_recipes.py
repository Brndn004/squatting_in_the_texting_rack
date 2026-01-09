#!/usr/bin/env python3
"""Validate recipe files.

Validates that all recipe JSON files use valid tags from the RecipeTag enum.
"""

import json
import logging
import sys
from pathlib import Path

import recipe_tags

# Constants
_RECIPES_DIR = Path(__file__).parent.parent / "recipes"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _get_recipes_dir() -> Path:
    """Get the path to the recipes directory."""
    return _RECIPES_DIR


def _validate_recipe_tags(recipe_path: Path) -> list[str]:
    """Validate tags in a recipe file against RecipeTag enum.

    Args:
        recipe_path: Path to recipe JSON file.

    Returns:
        List of invalid tag strings found. Empty list if all tags are valid.
    """
    try:
        with open(recipe_path, "r", encoding="utf-8") as f:
            recipe = json.load(f)

        if not isinstance(recipe, dict):
            logger.warning(f"Recipe file is not a valid JSON object: {recipe_path}")
            return []

        tags = recipe.get("tags", [])
        if not isinstance(tags, list):
            logger.warning(f"Tags field is not a list in {recipe_path}")
            return []

        invalid_tags = []
        for tag in tags:
            if not isinstance(tag, str):
                invalid_tags.append(str(tag))
                continue
            try:
                recipe_tags.RecipeTag.from_string(tag)
            except ValueError:
                invalid_tags.append(tag)

        return invalid_tags

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse recipe file {recipe_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error reading {recipe_path}: {e}")
        return []


def _validate_all_recipes() -> bool:
    """Validate all recipe files.

    Returns:
        True if all recipes are valid, False otherwise.
    """
    recipes_dir = _get_recipes_dir()
    if not recipes_dir.exists():
        logger.warning(f"Recipes directory not found: {recipes_dir}")
        return True

    all_valid = True
    recipe_files = list(recipes_dir.glob("*.json"))

    if not recipe_files:
        logger.info("No recipe files found.")
        return True

    logger.info(f"Validating {len(recipe_files)} recipe files...")

    for recipe_file in recipe_files:
        invalid_tags = _validate_recipe_tags(recipe_file)
        if invalid_tags:
            logger.error(
                f"✗ {recipe_file.name}: Invalid tags: {invalid_tags}"
            )
            all_valid = False
        else:
            logger.debug(f"✓ {recipe_file.name}: Valid")

    return all_valid


def main() -> None:
    """Main entry point for recipe validation."""
    try:
        if _validate_all_recipes():
            logger.info("All recipes are valid.")
            sys.exit(0)
        else:
            logger.error("Some recipes contain invalid tags.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()

