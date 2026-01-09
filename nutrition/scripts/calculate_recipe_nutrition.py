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


def _validate_ingredient_amount(
    ingredient: typing.Dict[str, typing.Any]
) -> tuple[float, measure_converter.MeasureUnit]:
    """Validate and extract quantity and measure_unit from ingredient.

    Args:
        ingredient: Ingredient dictionary with 'quantity' (float) and 'measure_unit' (string).

    Returns:
        Tuple of (quantity, MeasureUnit).

    Raises:
        ValueError: If quantity or measure_unit is missing or invalid.
    """
    quantity = ingredient.get("quantity")
    measure_unit_str = ingredient.get("measure_unit")

    if quantity is None:
        raise ValueError(
            f"Ingredient missing 'quantity' field: {ingredient}. "
            f"Expected format: {{'fdc_id': ..., 'quantity': 1.0, 'measure_unit': 'Cup', ...}}"
        )
    
    if measure_unit_str is None:
        raise ValueError(
            f"Ingredient missing 'measure_unit' field: {ingredient}. "
            f"Expected format: {{'fdc_id': ..., 'quantity': 1.0, 'measure_unit': 'Cup', ...}}"
        )

    try:
        quantity_float = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(
            f"Invalid quantity '{quantity}' in ingredient. Must be a number. "
            f"Ingredient: {ingredient}"
        )

    if quantity_float <= 0:
        raise ValueError(
            f"Quantity must be greater than zero, got {quantity_float}. "
            f"Ingredient: {ingredient}"
        )

    # Find matching MeasureUnit - must match exactly
    unit = None
    for measure_unit in measure_converter.MeasureUnit:
        if measure_unit.value == measure_unit_str:
            unit = measure_unit
            break

    if unit is None:
        valid_units = ", ".join(sorted(measure_converter.MeasureUnit.values()))
        raise ValueError(
            f"Invalid measure_unit '{measure_unit_str}' in ingredient. "
            f"Must exactly match one of: {valid_units}. "
            f"Ingredient: {ingredient}"
        )

    return (quantity_float, unit)


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
    
    For energy, we prefer "Energy (kcal)" if available, otherwise use "Energy (Atwater General Factors) (kcal)"
    or "Energy (Atwater Specific Factors) (kcal)". Only one energy value per ingredient is included.

    Args:
        ingredient_data: Full ingredient JSON data from USDA.
        gram_weight: Weight in grams to calculate nutrients for.

    Returns:
        Dictionary mapping nutrient names to amounts.
    """
    nutrients = {}
    food_nutrients = ingredient_data.get("foodNutrients", [])
    
    # Track which energy entry we've used (prefer Energy > Atwater General > Atwater Specific)
    energy_used = None
    energy_value = None

    for food_nutrient in food_nutrients:
        nutrient_info = food_nutrient.get("nutrient", {})
        nutrient_name = nutrient_info.get("name", "")
        nutrient_amount = food_nutrient.get("amount", 0.0)
        unit_name = nutrient_info.get("unitName", "")

        if nutrient_name and nutrient_amount is not None:
            # Handle energy entries specially - only include one per ingredient
            if unit_name == "kcal" and (
                nutrient_name == "Energy" or
                nutrient_name == "Energy (Atwater General Factors)" or
                nutrient_name == "Energy (Atwater Specific Factors)"
            ):
                # Scale from per 100g to actual gram weight
                scaled_amount = (gram_weight / 100.0) * nutrient_amount
                
                # Prefer "Energy" over Atwater factors
                if nutrient_name == "Energy":
                    energy_used = "Energy"
                    energy_value = scaled_amount
                elif nutrient_name == "Energy (Atwater General Factors)" and energy_used != "Energy":
                    energy_used = "Energy (Atwater General Factors)"
                    energy_value = scaled_amount
                elif nutrient_name == "Energy (Atwater Specific Factors)" and energy_used is None:
                    energy_used = "Energy (Atwater Specific Factors)"
                    energy_value = scaled_amount
                continue
            
            # Scale from per 100g to actual gram weight
            scaled_amount = (gram_weight / 100.0) * nutrient_amount

            # Use nutrient name + unit as key to handle same nutrient with different units
            key = f"{nutrient_name} ({unit_name})"
            nutrients[key] = scaled_amount
    
    # Add the selected energy value as "Energy (kcal)"
    if energy_value is not None:
        nutrients["Energy (kcal)"] = energy_value

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

        if not fdc_id:
            raise ValueError(f"Ingredient missing fdc_id: {ingredient}")

        # Validate and extract quantity and measure_unit
        try:
            quantity, unit = _validate_ingredient_amount(ingredient)
        except ValueError as e:
            raise ValueError(f"Invalid ingredient amount: {e}")

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
            ingredient_name = ingredient.get("name", f"FDC {fdc_id}")
            raise ValueError(
                f"Cannot convert {quantity} {unit.value} for ingredient {ingredient_name} (FDC {fdc_id}): {e}"
            )

        # Calculate nutrients for this ingredient
        ingredient_nutrients = _calculate_ingredient_nutrients(
            ingredient_data, gram_weight
        )
        all_ingredient_nutrients.append(ingredient_nutrients)

        ingredient_name = ingredient.get("name", f"FDC {fdc_id}")
        logger.debug(
            f"Ingredient {ingredient_name} (FDC {fdc_id}): {quantity} {unit.value} = {gram_weight:.2f}g, "
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

        # Validate that "Energy (kcal)" exists and is complete
        # Each ingredient contributes one energy value (preferring "Energy" over Atwater factors)
        # All are stored as "Energy (kcal)" in the final nutrition facts
        energy_kcal = per_serving_nutrition.get("Energy (kcal)", 0.0)
        
        # Check which ingredients are missing any Energy entries
        missing_ingredients = []
        for ingredient in recipe.get("ingredients", []):
            fdc_id = ingredient.get("fdc_id")
            ingredient_name = ingredient.get("name", f"FDC {fdc_id}")
            quantity = ingredient.get("quantity", "?")
            measure_unit = ingredient.get("measure_unit", "?")
            amount_str = f"{quantity} {measure_unit}"
            
            try:
                ingredient_data = _load_ingredient(fdc_id)
                has_energy_kcal = False
                for nutrient in ingredient_data.get("foodNutrients", []):
                    nutrient_info = nutrient.get("nutrient", {})
                    nutrient_name = nutrient_info.get("name", "")
                    unit_name = nutrient_info.get("unitName", "")
                    # Check for any Energy entry with unit "kcal"
                    # Accept: "Energy", "Energy (Atwater General Factors)", "Energy (Atwater Specific Factors)"
                    if unit_name == "kcal" and (
                        nutrient_name == "Energy" or
                        nutrient_name == "Energy (Atwater General Factors)" or
                        nutrient_name == "Energy (Atwater Specific Factors)"
                    ):
                        has_energy_kcal = True
                        break
                
                if not has_energy_kcal:
                    missing_ingredients.append(f"{ingredient_name} (FDC {fdc_id}, {amount_str})")
            except Exception as e:
                # If we can't check, include it in the error message
                missing_ingredients.append(f"{ingredient_name} (FDC {fdc_id}, {amount_str}) - error checking: {e}")
        
        if energy_kcal == 0.0:
            if missing_ingredients:
                missing_list = "\n  - ".join(missing_ingredients)
                raise ValueError(
                    f"Recipe '{recipe_path.name}' is missing 'Energy (kcal)' data. "
                    f"The following ingredients do not have 'Energy (kcal)' entries:\n  - {missing_list}\n"
                    f"Please use ingredients that have 'Energy (kcal)' entries, or update the ingredient "
                    f"data files to include this nutrient."
                )
            else:
                raise ValueError(
                    f"Recipe '{recipe_path.name}' has no 'Energy (kcal)' data. "
                    f"Total nutrition facts calculated: {len(total_nutrition_facts)} nutrients, "
                    f"but 'Energy (kcal)' is missing."
                )
        
        # Check if total energy seems incomplete by comparing to calories from macros
        protein_g = per_serving_nutrition.get("Protein (g)", 0.0)
        carbs_g = per_serving_nutrition.get("Carbohydrate, by difference (g)", 0.0)
        fat_g = per_serving_nutrition.get("Total lipid (fat) (g)", 0.0)
        calculated_cals = (protein_g * 4) + (carbs_g * 4) + (fat_g * 9)
        
        if calculated_cals > 0 and energy_kcal < calculated_cals * 0.7:
            # Energy (kcal) is significantly less than calories from macros - likely incomplete
            if missing_ingredients:
                missing_list = "\n  - ".join(missing_ingredients)
                raise ValueError(
                    f"Recipe '{recipe_path.name}' has incomplete 'Energy (kcal)' data. "
                    f"Energy (kcal) = {energy_kcal:.1f} cal, but calories from macros = {calculated_cals:.1f} cal. "
                    f"The following ingredients are missing energy entries:\n  - {missing_list}\n"
                    f"Please use ingredients that have energy entries (Energy, Energy (Atwater General Factors), "
                    f"or Energy (Atwater Specific Factors)), or update the ingredient data files to include energy data."
                )
            else:
                raise ValueError(
                    f"Recipe '{recipe_path.name}' has incomplete 'Energy (kcal)' data. "
                    f"Energy (kcal) = {energy_kcal:.1f} cal, but calories from macros = {calculated_cals:.1f} cal. "
                    f"This suggests some ingredients are missing energy entries."
                )

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
        # These are validation/data errors - log and re-raise to stop processing
        logger.error(f"✗ {recipe_path.name}: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"✗ {recipe_path.name}: Invalid JSON: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ {recipe_path.name}: Unexpected error: {e}")
        return False


def _update_all_recipes() -> None:
    """Update nutrition facts for all recipe files.
    
    Raises:
        ValueError: If any recipe has validation errors (e.g., missing Energy (kcal) data).
        FileNotFoundError: If any ingredient file is missing.
        SystemExit: If any recipe fails to update.
    """
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
    failed_recipes = []
    
    for recipe_file in recipe_files:
        try:
            if _update_recipe_nutrition(recipe_file):
                updated_count += 1
            else:
                failed_recipes.append(recipe_file.name)
        except (FileNotFoundError, ValueError):
            # These are validation/data errors - re-raise to stop immediately
            # Error message is already logged in _update_recipe_nutrition
            raise
        except Exception as e:
            # Other errors - log and continue, but track failures
            logger.error(f"✗ {recipe_file.name}: Unexpected error: {e}")
            failed_recipes.append(recipe_file.name)

    if failed_recipes:
        raise SystemExit(
            f"Failed to update {len(failed_recipes)} recipe(s): {', '.join(failed_recipes)}. "
            f"Successfully updated {updated_count}/{len(recipe_files)} recipes."
        )
    
    logger.info(f"Successfully updated {updated_count}/{len(recipe_files)} recipes.")


def main() -> None:
    """Main entry point for recipe nutrition calculation."""
    try:
        _update_all_recipes()
    except (FileNotFoundError, ValueError) as e:
        # Validation/data errors - already logged with context, just exit
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

