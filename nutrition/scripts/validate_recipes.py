#!/usr/bin/env python3
"""Validate recipe files.

Validates that all recipe JSON files:
- Use valid tags from the RecipeTag enum
- Reference ingredients that exist in the ingredients directory
"""

import json
import logging
import sys
from pathlib import Path

import recipe_tags

# Constants
_RECIPES_DIR = Path(__file__).parent.parent / "recipes"
_INGREDIENTS_DIR = Path(__file__).parent.parent / "ingredients"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _get_recipes_dir() -> Path:
    """Get the path to the recipes directory."""
    return _RECIPES_DIR


def _get_ingredients_dir() -> Path:
    """Get the path to the ingredients directory."""
    return _INGREDIENTS_DIR


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


def _validate_recipe_ingredients(recipe_path: Path) -> list[tuple[int, str]]:
    """Validate ingredients in a recipe file.

    Checks that all ingredient fdc_ids have corresponding ingredient files.

    Args:
        recipe_path: Path to recipe JSON file.

    Returns:
        List of tuples (fdc_id, name) for missing ingredients. Empty list if all ingredients exist.
    """
    try:
        with open(recipe_path, "r", encoding="utf-8") as f:
            recipe = json.load(f)

        if not isinstance(recipe, dict):
            logger.warning(f"Recipe file is not a valid JSON object: {recipe_path}")
            return []

        ingredients = recipe.get("ingredients", [])
        if not isinstance(ingredients, list):
            logger.warning(f"Ingredients field is not a list in {recipe_path}")
            return []

        missing_ingredients = []
        ingredients_dir = _get_ingredients_dir()

        for ingredient in ingredients:
            if not isinstance(ingredient, dict):
                continue

            fdc_id = ingredient.get("fdc_id")
            if fdc_id is None:
                continue

            ingredient_name = ingredient.get("name", "Unknown")
            if not isinstance(ingredient_name, str):
                ingredient_name = str(ingredient_name)

            if not isinstance(fdc_id, int):
                try:
                    fdc_id = int(fdc_id)
                except (ValueError, TypeError):
                    missing_ingredients.append((fdc_id, ingredient_name))
                    continue

            ingredient_file = ingredients_dir / f"{fdc_id}.json"
            if not ingredient_file.exists():
                missing_ingredients.append((fdc_id, ingredient_name))

        return missing_ingredients

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
        recipe_valid = True

        # Validate tags
        invalid_tags = _validate_recipe_tags(recipe_file)
        if invalid_tags:
            logger.error(
                f"✗ {recipe_file.name}: Invalid tags: {invalid_tags}"
            )
            recipe_valid = False

        # Validate ingredients
        missing_ingredients = _validate_recipe_ingredients(recipe_file)
        if missing_ingredients:
            missing_list = [f"[{fdc_id}] {name}" for fdc_id, name in missing_ingredients]
            logger.error(
                f"✗ {recipe_file.name}: Missing ingredients: {', '.join(missing_list)}"
            )
            recipe_valid = False

        if recipe_valid:
            logger.debug(f"✓ {recipe_file.name}: Valid")
        else:
            all_valid = False

    return all_valid


def main() -> None:
    """Main entry point for recipe validation."""
    try:
        if _validate_all_recipes():
            logger.info("All recipes are valid.")
            logger.info("  ✓ Tags all exist in the RecipeTag enum.")
            logger.info("  ✓ Ingredients all exist in the ingredient database.")
            sys.exit(0)
        else:
            logger.error("Some recipes contain invalid tags or missing ingredients.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()

