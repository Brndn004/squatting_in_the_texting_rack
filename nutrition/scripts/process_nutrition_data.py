#!/usr/bin/env python3
"""Process all nutrition data: update tags, validate recipes, calculate nutrition.

This script runs the complete processing pipeline:
1. Updates tags database from RecipeTag enum
2. Validates all recipes use valid tags
3. Calculates nutrition facts and macros for all recipes
4. Calculates nutrition facts and macros for all meals

This ensures all data is up-to-date and consistent.
"""

import logging
import sys
from pathlib import Path

import calculate_meal_nutrition
import calculate_recipe_nutrition
import tag_management
import validate_recipes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _update_tags() -> bool:
    """Update tags database from RecipeTag enum.
    
    Returns:
        True if successful, False otherwise.
    """
    try:
        logger.info("=" * 60)
        logger.info("Step 1: Updating tags database")
        logger.info("=" * 60)
        tag_management._update_tags_database()
        return True
    except Exception as e:
        logger.error(f"Failed to update tags: {e}")
        return False


def _validate_all_recipes() -> bool:
    """Validate all recipes use valid tags.
    
    Returns:
        True if all recipes are valid, False otherwise.
    """
    try:
        logger.info("")
        logger.info("=" * 60)
        logger.info("Step 2: Validating recipes")
        logger.info("=" * 60)
        return validate_recipes._validate_all_recipes()
    except Exception as e:
        logger.error(f"Failed to validate recipes: {e}")
        return False


def _calculate_recipe_nutrition() -> bool:
    """Calculate nutrition facts and macros for all recipes.
    
    Returns:
        True if successful, False otherwise.
    """
    try:
        logger.info("")
        logger.info("=" * 60)
        logger.info("Step 3: Calculating recipe nutrition")
        logger.info("=" * 60)
        calculate_recipe_nutrition._update_all_recipes()
        return True
    except Exception as e:
        logger.error(f"Failed to calculate recipe nutrition: {e}")
        return False


def _calculate_meal_nutrition() -> bool:
    """Calculate nutrition facts and macros for all meals.
    
    Returns:
        True if successful, False otherwise.
    """
    try:
        logger.info("")
        logger.info("=" * 60)
        logger.info("Step 4: Calculating meal nutrition")
        logger.info("=" * 60)
        calculate_meal_nutrition._update_all_meals()
        return True
    except Exception as e:
        logger.error(f"Failed to calculate meal nutrition: {e}")
        return False


def main() -> None:
    """Main entry point for processing all nutrition data."""
    logger.info("Processing all nutrition data...")
    logger.info("")
    
    success = True
    
    # Step 1: Update tags database
    if not _update_tags():
        logger.error("Tag update failed. Stopping.")
        sys.exit(1)
    
    # Step 2: Validate recipes
    if not _validate_all_recipes():
        logger.error("Recipe validation failed. Stopping.")
        sys.exit(1)
    
    # Step 3: Calculate recipe nutrition
    if not _calculate_recipe_nutrition():
        logger.error("Recipe nutrition calculation failed. Stopping.")
        sys.exit(1)
    
    # Step 4: Calculate meal nutrition
    if not _calculate_meal_nutrition():
        logger.error("Meal nutrition calculation failed. Stopping.")
        sys.exit(1)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✓ All processing complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

