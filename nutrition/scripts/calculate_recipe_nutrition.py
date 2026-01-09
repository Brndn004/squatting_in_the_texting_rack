#!/usr/bin/env python3
"""Calculate and update recipe nutrition facts from ingredients.

Reads all recipe JSON files, calculates nutrition facts by:
1. Loading each ingredient by FDC ID
2. Converting recipe amounts to grams using measure_converter
3. Scaling ingredient nutrients based on gram weight
4. Summing all nutrients across all ingredients
5. Updating the recipe's nutrition_facts field
"""

import json
import logging
import re
import sys
import typing
from pathlib import Path

import measure_converter

# Constants
_RECIPES_DIR = Path(__file__).parent.parent / "recipes"
_INGREDIENTS_DIR = Path(__file__).parent.parent / "ingredients"
_JSON_INDENT = 2

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


def _parse_amount(amount_str: str) -> tuple[float, measure_converter.MeasureUnit]:
    """Parse amount string into quantity and unit.

    Args:
        amount_str: String like "1 Cup", "0.25 Tsp", "2 Tbsp"

    Returns:
        Tuple of (quantity, MeasureUnit).

    Raises:
        ValueError: If amount string format is invalid.
    """
    # Pattern: optional decimal number, whitespace, unit name
    match = re.match(r"^(\d+\.?\d*)\s+(.+)$", amount_str.strip())
    if not match:
        raise ValueError(
            f"Invalid amount format: '{amount_str}'. Expected format: '1 Cup', '0.25 Tsp', etc."
        )

    quantity_str = match.group(1)
    unit_str = match.group(2)

    try:
        quantity = float(quantity_str)
    except ValueError:
        raise ValueError(f"Invalid quantity '{quantity_str}' in amount '{amount_str}'")

    # Find matching MeasureUnit
    unit = None
    for measure_unit in measure_converter.MeasureUnit:
        if measure_unit.value == unit_str:
            unit = measure_unit
            break

    if unit is None:
        valid_units = ", ".join(measure_converter.MeasureUnit.values())
        raise ValueError(
            f"Invalid unit '{unit_str}' in amount '{amount_str}'. "
            f"Valid units: {valid_units}"
        )

    return (quantity, unit)


def _load_ingredient(fdc_id: int) -> typing.Dict[str, typing.Any]:
    """Load ingredient JSON file by FDC ID.

    Args:
        fdc_id: USDA FDC ID.

    Returns:
        Ingredient data dictionary.

    Raises:
        FileNotFoundError: If ingredient file doesn't exist.
        json.JSONDecodeError: If ingredient file is invalid JSON.
    """
    ingredient_file = _get_ingredients_dir() / f"{fdc_id}.json"
    if not ingredient_file.exists():
        raise FileNotFoundError(f"Ingredient file not found: {ingredient_file}")

    with open(ingredient_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _calculate_ingredient_nutrients(
    ingredient_data: typing.Dict[str, typing.Any], gram_weight: float
) -> typing.Dict[str, float]:
    """Calculate nutrients for a given gram weight of ingredient.

    USDA nutrients are per 100g, so we scale: (gram_weight / 100) * nutrient_amount.

    Args:
        ingredient_data: Full ingredient JSON data from USDA.
        gram_weight: Weight in grams to calculate nutrients for.

    Returns:
        Dictionary mapping nutrient names to amounts.
    """
    nutrients = {}
    food_nutrients = ingredient_data.get("foodNutrients", [])

    for food_nutrient in food_nutrients:
        nutrient_info = food_nutrient.get("nutrient", {})
        nutrient_name = nutrient_info.get("name", "")
        nutrient_amount = food_nutrient.get("amount", 0.0)
        unit_name = nutrient_info.get("unitName", "")

        if nutrient_name and nutrient_amount is not None:
            # Scale from per 100g to actual gram weight
            scaled_amount = (gram_weight / 100.0) * nutrient_amount

            # Use nutrient name + unit as key to handle same nutrient with different units
            key = f"{nutrient_name} ({unit_name})"
            nutrients[key] = scaled_amount

    return nutrients


def _sum_nutrients(nutrient_lists: typing.List[typing.Dict[str, float]]) -> typing.Dict[str, float]:
    """Sum nutrients across multiple ingredient contributions.
    
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


def _calculate_macros(nutrition_facts: typing.Dict[str, float]) -> typing.Dict[str, typing.Any]:
    """Calculate macros breakdown from nutrition facts.
    
    Args:
        nutrition_facts: Dictionary mapping nutrient names to amounts.
        
    Returns:
        Dictionary with macros information including grams and percentages.
    """
    # Extract macro values
    protein_g = nutrition_facts.get("Protein (g)", 0.0)
    carbs_g = nutrition_facts.get("Carbohydrate, by difference (g)", 0.0)
    fat_g = nutrition_facts.get("Total lipid (fat) (g)", 0.0)
    
    # Calculate calories from each macro
    # Protein: 4 cal/g, Carbs: 4 cal/g, Fat: 9 cal/g
    protein_cals = protein_g * 4
    carbs_cals = carbs_g * 4
    fat_cals = fat_g * 9
    total_cals = protein_cals + carbs_cals + fat_cals
    
    # Calculate percentages
    if total_cals > 0:
        protein_percent = round((protein_cals / total_cals) * 100, 1)
        carbs_percent = round((carbs_cals / total_cals) * 100, 1)
        fat_percent = round((fat_cals / total_cals) * 100, 1)
    else:
        protein_percent = 0.0
        carbs_percent = 0.0
        fat_percent = 0.0
    
    return {
        "protein": {
            "grams": round(protein_g, 1),
            "percent": protein_percent
        },
        "carbs": {
            "grams": round(carbs_g, 1),
            "percent": carbs_percent
        },
        "fat": {
            "grams": round(fat_g, 1),
            "percent": fat_percent
        }
    }


def _calculate_recipe_nutrition(recipe: typing.Dict[str, typing.Any]) -> typing.Dict[str, float]:
    """Calculate nutrition facts for a recipe.

    Args:
        recipe: Recipe dictionary with ingredients list.

    Returns:
        Dictionary mapping nutrient names to total amounts.

    Raises:
        FileNotFoundError: If any ingredient file is missing.
        ValueError: If any ingredient amount is invalid or can't be converted.
    """
    ingredients = recipe.get("ingredients", [])
    if not ingredients:
        logger.warning("Recipe has no ingredients")
        return {}

    all_ingredient_nutrients = []

    for ingredient in ingredients:
        fdc_id = ingredient.get("fdc_id")
        amount_str = ingredient.get("amount", "")

        if not fdc_id:
            raise ValueError(f"Ingredient missing fdc_id: {ingredient}")
        if not amount_str:
            raise ValueError(f"Ingredient missing amount: {ingredient}")

        # Parse amount
        try:
            quantity, unit = _parse_amount(amount_str)
        except ValueError as e:
            raise ValueError(f"Invalid amount '{amount_str}' for ingredient {fdc_id}: {e}")

        # Load ingredient data
        try:
            ingredient_data = _load_ingredient(fdc_id)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Ingredient {fdc_id} not found: {e}")

        # Get foodPortions
        food_portions = ingredient_data.get("foodPortions", [])
        if not food_portions:
            raise ValueError(f"Ingredient {fdc_id} has no foodPortions data")

        # Convert to grams using measure_converter
        try:
            _, gram_weight = measure_converter.find_food_portion(
                quantity, unit, food_portions
            )
        except measure_converter.MeasureMatchError as e:
            raise ValueError(
                f"Cannot convert '{amount_str}' for ingredient {fdc_id}: {e}"
            )

        # Calculate nutrients for this ingredient
        ingredient_nutrients = _calculate_ingredient_nutrients(
            ingredient_data, gram_weight
        )
        all_ingredient_nutrients.append(ingredient_nutrients)

        logger.debug(
            f"Ingredient {fdc_id}: {amount_str} = {gram_weight:.2f}g, "
            f"{len(ingredient_nutrients)} nutrients"
        )

    # Sum all nutrients
    total_nutrients = _sum_nutrients(all_ingredient_nutrients)
    return total_nutrients


def _update_recipe_nutrition(recipe_path: Path) -> bool:
    """Update nutrition facts for a single recipe file.

    Args:
        recipe_path: Path to recipe JSON file.

    Returns:
        True if recipe was updated, False if skipped or error.
    """
    try:
        with open(recipe_path, "r", encoding="utf-8") as f:
            recipe = json.load(f)

        if not isinstance(recipe, dict):
            logger.warning(f"Recipe file is not a valid JSON object: {recipe_path}")
            return False

        # Calculate total nutrition facts for the recipe
        total_nutrition_facts = _calculate_recipe_nutrition(recipe)

        # Get serving size (defaults to 1 for backward compatibility)
        serving_size = recipe.get("serving_size", 1.0)
        if not isinstance(serving_size, (int, float)) or serving_size <= 0:
            logger.warning(
                f"Recipe {recipe_path.name} has invalid serving_size '{serving_size}'. "
                "Using 1.0 as default."
            )
            serving_size = 1.0

        # Convert to per-serving nutrition
        per_serving_nutrition = {}
        for nutrient_name, total_amount in total_nutrition_facts.items():
            per_serving_nutrition[nutrient_name] = total_amount / serving_size

        # Calculate macros from per-serving nutrition
        macros = _calculate_macros(per_serving_nutrition)

        # Update recipe with per-serving nutrition and macros
        recipe["nutrition_facts"] = per_serving_nutrition
        recipe["macros"] = macros

        # Save updated recipe
        with open(recipe_path, "w", encoding="utf-8") as f:
            json.dump(recipe, f, indent=_JSON_INDENT, ensure_ascii=False)
            f.write("\n")

        logger.info(f"✓ Updated {recipe_path.name}: {len(per_serving_nutrition)} nutrients")
        return True

    except (FileNotFoundError, ValueError) as e:
        logger.error(f"✗ {recipe_path.name}: {e}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"✗ {recipe_path.name}: Invalid JSON: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ {recipe_path.name}: Unexpected error: {e}")
        return False


def _update_all_recipes() -> None:
    """Update nutrition facts for all recipe files."""
    recipes_dir = _get_recipes_dir()
    if not recipes_dir.exists():
        logger.warning(f"Recipes directory not found: {recipes_dir}")
        return

    recipe_files = list(recipes_dir.glob("*.json"))
    if not recipe_files:
        logger.info("No recipe files found.")
        return

    logger.info(f"Updating nutrition facts for {len(recipe_files)} recipes...")

    updated_count = 0
    for recipe_file in recipe_files:
        if _update_recipe_nutrition(recipe_file):
            updated_count += 1

    logger.info(f"Successfully updated {updated_count}/{len(recipe_files)} recipes.")


def main() -> None:
    """Main entry point for recipe nutrition calculation."""
    try:
        _update_all_recipes()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

