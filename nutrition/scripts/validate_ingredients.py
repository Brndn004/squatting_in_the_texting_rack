#!/usr/bin/env python3
"""Validate ingredient files.

Validates that all ingredient JSON files:
- Have energy (kcal) data required for recipe nutrition calculations
"""

import json
import logging
import sys
from pathlib import Path

# Constants
_INGREDIENTS_DIR = Path(__file__).parent.parent / "ingredients"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _get_ingredients_dir() -> Path:
    """Get the path to the ingredients directory."""
    return _INGREDIENTS_DIR


def _has_energy_kcal(ingredient_data: dict) -> bool:
    """Check if ingredient has energy (kcal) data.
    
    Accepts any of the following energy entries:
    - "Energy" with unit "kcal"
    - "Energy (Atwater General Factors)" with unit "kcal"
    - "Energy (Atwater Specific Factors)" with unit "kcal"
    
    Args:
        ingredient_data: Ingredient JSON data dictionary.
        
    Returns:
        True if ingredient has energy (kcal) data, False otherwise.
    """
    food_nutrients = ingredient_data.get("foodNutrients", [])
    
    for food_nutrient in food_nutrients:
        nutrient_info = food_nutrient.get("nutrient", {})
        nutrient_name = nutrient_info.get("name", "")
        unit_name = nutrient_info.get("unitName", "")
        
        # Check for any Energy entry with unit "kcal"
        if unit_name == "kcal" and (
            nutrient_name == "Energy" or
            nutrient_name == "Energy (Atwater General Factors)" or
            nutrient_name == "Energy (Atwater Specific Factors)"
        ):
            return True
    
    return False


def _validate_ingredient_energy(ingredient_path: Path) -> bool:
    """Validate that an ingredient file has energy (kcal) data.

    Args:
        ingredient_path: Path to ingredient JSON file.

    Returns:
        True if ingredient has energy (kcal) data, False otherwise.
    """
    try:
        with open(ingredient_path, "r", encoding="utf-8") as f:
            ingredient_data = json.load(f)

        if not isinstance(ingredient_data, dict):
            logger.warning(f"Ingredient file is not a valid JSON object: {ingredient_path}")
            return False

        return _has_energy_kcal(ingredient_data)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse ingredient file {ingredient_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error reading {ingredient_path}: {e}")
        return False


def _validate_all_ingredients() -> bool:
    """Validate all ingredient files.

    Returns:
        True if all ingredients are valid, False otherwise.
    """
    ingredients_dir = _get_ingredients_dir()
    if not ingredients_dir.exists():
        logger.warning(f"Ingredients directory not found: {ingredients_dir}")
        return True

    all_valid = True
    ingredient_files = list(ingredients_dir.glob("*.json"))
    
    # Exclude ingredient_lookup.json from validation
    ingredient_files = [f for f in ingredient_files if f.name != "ingredient_lookup.json"]

    if not ingredient_files:
        logger.info("No ingredient files found.")
        return True

    logger.info(f"Validating {len(ingredient_files)} ingredient files...")

    missing_energy = []
    for ingredient_file in ingredient_files:
        if not _validate_ingredient_energy(ingredient_file):
            # Extract FDC ID from filename
            fdc_id = ingredient_file.stem
            try:
                # Try to get ingredient name from the file
                with open(ingredient_file, "r", encoding="utf-8") as f:
                    ingredient_data = json.load(f)
                    ingredient_name = ingredient_data.get("description", "Unknown")
            except Exception:
                ingredient_name = "Unknown"
            
            missing_energy.append((fdc_id, ingredient_name))
            all_valid = False

    if missing_energy:
        missing_list = [f"[{fdc_id}] {name}" for fdc_id, name in missing_energy]
        logger.error(
            f"✗ {len(missing_energy)} ingredient(s) missing energy (kcal) data:\n"
            + "\n".join(f"  - {item}" for item in missing_list)
        )
    else:
        logger.debug(f"✓ All {len(ingredient_files)} ingredients have energy (kcal) data")

    return all_valid


def main() -> None:
    """Main entry point for ingredient validation."""
    try:
        if _validate_all_ingredients():
            logger.info("All ingredients are valid.")
            logger.info("  ✓ All ingredients have energy (kcal) data required for nutrition calculations.")
            sys.exit(0)
        else:
            logger.error("Some ingredients are missing energy (kcal) data.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()

