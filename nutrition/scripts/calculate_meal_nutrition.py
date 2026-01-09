#!/usr/bin/env python3
"""Calculate and update meal nutrition facts from recipes.

Reads all meal JSON files, calculates nutrition facts by:
1. Loading each recipe referenced in the meal
2. Scaling recipe nutrition facts by servings
3. Summing all nutrients across all recipes
4. Updating the meal's nutrition_facts field
"""

import json
import logging
import sys
import typing
from pathlib import Path

import calculate_recipe_nutrition

# Constants
_MEALS_DIR = Path(__file__).parent.parent / "meals"
_RECIPES_DIR = Path(__file__).parent.parent / "recipes"
_JSON_INDENT = 2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _get_meals_dir() -> Path:
    """Get the path to the meals directory."""
    return _MEALS_DIR


def _get_recipes_dir() -> Path:
    """Get the path to the recipes directory."""
    return _RECIPES_DIR


def _load_recipe(recipe_name: str) -> typing.Dict[str, typing.Any]:
    """Load recipe JSON file by name.

    Args:
        recipe_name: Recipe filename without .json extension (e.g., "warm_milk").

    Returns:
        Recipe data dictionary.

    Raises:
        FileNotFoundError: If recipe file doesn't exist.
        json.JSONDecodeError: If recipe file is invalid JSON.
    """
    recipe_file = _get_recipes_dir() / f"{recipe_name}.json"
    if not recipe_file.exists():
        raise FileNotFoundError(f"Recipe file not found: {recipe_file}")

    with open(recipe_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _calculate_recipe_nutrients(
    recipe_data: typing.Dict[str, typing.Any], meal_servings: float
) -> typing.Dict[str, float]:
    """Calculate nutrients for a given number of servings of a recipe.

    The recipe's nutrition_facts represent per-serving nutrition. We simply
    multiply by the number of servings requested.

    Args:
        recipe_data: Recipe JSON data dictionary.
        meal_servings: Number of servings requested in the meal (must be > 0).

    Returns:
        Dictionary mapping nutrient names to amounts (scaled by servings).
    """
    if meal_servings <= 0:
        raise ValueError(f"Servings must be greater than zero, got {meal_servings}")

    nutrition_facts = recipe_data.get("nutrition_facts", {})
    if not isinstance(nutrition_facts, dict):
        return {}

    # Scale: meal_servings * per_serving_nutrition_facts
    scaled_nutrients = {}
    for nutrient_name, amount in nutrition_facts.items():
        if isinstance(amount, (int, float)):
            scaled_nutrients[nutrient_name] = amount * meal_servings
        else:
            logger.warning(
                f"Non-numeric nutrient amount for {nutrient_name}: {amount}"
            )

    return scaled_nutrients


def _sum_nutrients(nutrient_lists: typing.List[typing.Dict[str, float]]) -> typing.Dict[str, float]:
    """Sum nutrients across multiple recipe contributions.

    Args:
        nutrient_lists: List of nutrient dictionaries to sum.

    Returns:
        Dictionary with summed nutrients.
    """
    summed = {}
    for nutrients in nutrient_lists:
        for nutrient_name, amount in nutrients.items():
            summed[nutrient_name] = summed.get(nutrient_name, 0.0) + amount
    return summed


def _calculate_meal_nutrition(meal: typing.Dict[str, typing.Any]) -> typing.Dict[str, float]:
    """Calculate nutrition facts for a meal.

    Args:
        meal: Meal dictionary with recipes list.

    Returns:
        Dictionary mapping nutrient names to total amounts.

    Raises:
        FileNotFoundError: If any recipe file is missing.
        ValueError: If any recipe servings is invalid.
    """
    recipes = meal.get("recipes", [])
    if not recipes:
        logger.warning("Meal has no recipes")
        return {}

    all_recipe_nutrients = []

    for recipe_entry in recipes:
        recipe_name = recipe_entry.get("recipe")
        servings = recipe_entry.get("servings", 1.0)

        if not recipe_name:
            raise ValueError(f"Recipe entry missing recipe name: {recipe_entry}")

        if not isinstance(servings, (int, float)) or servings <= 0:
            raise ValueError(
                f"Invalid servings '{servings}' for recipe '{recipe_name}'. "
                "Servings must be a positive number."
            )

        # Load recipe data
        try:
            recipe_data = _load_recipe(recipe_name)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Recipe '{recipe_name}' not found: {e}")

        # Calculate nutrients for this recipe
        recipe_nutrients = _calculate_recipe_nutrients(recipe_data, servings)
        all_recipe_nutrients.append(recipe_nutrients)

        logger.debug(
            f"Recipe {recipe_name}: {servings} servings, "
            f"{len(recipe_nutrients)} nutrients"
        )

    # Sum all nutrients
    total_nutrients = _sum_nutrients(all_recipe_nutrients)
    return total_nutrients


def _update_meal_nutrition(meal_path: Path) -> bool:
    """Update nutrition facts for a single meal file.

    Args:
        meal_path: Path to meal JSON file.

    Returns:
        True if meal was updated, False if skipped or error.
    """
    try:
        with open(meal_path, "r", encoding="utf-8") as f:
            meal = json.load(f)

        if not isinstance(meal, dict):
            logger.warning(f"Meal file is not a valid JSON object: {meal_path}")
            return False

        # Calculate nutrition facts
        nutrition_facts = _calculate_meal_nutrition(meal)

        # Update meal
        meal["nutrition_facts"] = nutrition_facts

        # Save updated meal
        with open(meal_path, "w", encoding="utf-8") as f:
            json.dump(meal, f, indent=_JSON_INDENT, ensure_ascii=False)
            f.write("\n")

        logger.info(f"✓ Updated {meal_path.name}: {len(nutrition_facts)} nutrients")
        return True

    except (FileNotFoundError, ValueError) as e:
        logger.error(f"✗ {meal_path.name}: {e}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"✗ {meal_path.name}: Invalid JSON: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ {meal_path.name}: Unexpected error: {e}")
        return False


def _update_all_meals() -> None:
    """Update nutrition facts for all meal files."""
    # First, ensure all recipes are up-to-date
    logger.info("Updating recipe nutrition facts first...")
    calculate_recipe_nutrition._update_all_recipes()

    meals_dir = _get_meals_dir()
    if not meals_dir.exists():
        logger.warning(f"Meals directory not found: {meals_dir}")
        return

    meal_files = list(meals_dir.glob("*.json"))
    if not meal_files:
        logger.info("No meal files found.")
        return

    logger.info(f"Updating nutrition facts for {len(meal_files)} meals...")

    updated_count = 0
    for meal_file in meal_files:
        if _update_meal_nutrition(meal_file):
            updated_count += 1

    logger.info(f"Successfully updated {updated_count}/{len(meal_files)} meals.")


def main() -> None:
    """Main entry point for meal nutrition calculation."""
    try:
        _update_all_meals()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

