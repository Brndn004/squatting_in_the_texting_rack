#!/usr/bin/env python3
"""MCP server for USDA Food Data Central ingredient lookup.

Provides tools for searching, retrieving, and saving USDA ingredient data.
"""

from pathlib import Path
from typing import Any

import json
import requests

from mcp.server import fastmcp

import calculate_meal_nutrition as meal_nutrition_module
import calculate_recipe_nutrition
import ingredient_management_lib
import recipe_tags
import tag_management
import usda_lib
import validate_ingredients
import validate_recipes

# Initialize FastMCP server
mcp = fastmcp.FastMCP("USDA Ingredient Lookup")


def _dict_to_json_string(d: dict[str, Any]) -> str:
    """Convert a dictionary to a JSON string."""
    return json.dumps(d)


@mcp.tool(
    description=(
        "Search for ingredients in the USDA FoodData Central database by name. "
        "This tool prioritizes Foundation, Survey (FNDDS), and SR Legacy data types "
        "over Branded products. Returns a list of matching foods with FDC IDs, "
        "descriptions, and data types. Use this tool when you need to find an ingredient "
        "by its common name (e.g., 'milk', 'chicken breast', 'whole wheat flour'). "
        "The response includes a 'foods' array with fdcId, description, and dataType "
        "for each match, plus a 'totalHits' count. Check the 'status' key in the "
        "returned JSON to determine if the search was successful."
    )
)
async def search_ingredient(query: str) -> str:
    """Search for ingredients matching the query.

    Args:
        query: Search term for ingredient name (e.g., "whole milk", "chicken breast").

    Returns:
        JSON string containing list of matching foods with FDC IDs, descriptions, and data types.
    """
    try:
        api_key = usda_lib.get_api_key()
        # Use maximum page size (200) to get more comprehensive results
        results = usda_lib.search_ingredient_prioritized(query, api_key, page_size=200)
        foods = results.get("foods", [])
        
        # Format foods list with essential info
        food_list = []
        for food in foods:
            food_list.append({
                "fdcId": food.get("fdcId"),
                "description": food.get("description"),
                "dataType": food.get("dataType"),
            })
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "foods": food_list,
            "totalHits": results.get("totalHits", 0),
        }
        return _dict_to_json_string(result)
    except usda_lib.UsdaApiKeyError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"API key error: {e}",
        }
        return _dict_to_json_string(result)
    except requests.RequestException as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"API request failed: {e}",
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get complete nutritional and ingredient details for a specific food item "
        "by its FoodData Central (FDC) ID. This tool retrieves the full USDA data "
        "including all nutrients, food components, and metadata, and automatically "
        "saves it to nutrition/ingredients/{fdc_id}.json and updates ingredient_lookup.json. "
        "Use this tool after searching for an ingredient to get detailed nutrition information. "
        "The FDC ID can be obtained from the search_ingredient tool results. The response includes "
        "the complete food object with all available nutrition facts, food components, "
        "and descriptive information. Check the 'status' key in the returned JSON to "
        "determine if the request was successful."
    )
)
async def get_ingredient_details(fdc_id: int) -> str:
    """Get full details for a specific ingredient by FDC ID and save it automatically.

    Args:
        fdc_id: FoodData Central ID (integer, e.g., 2705385 for whole milk).

    Returns:
        JSON string containing full ingredient data including nutrition facts.
    """
    try:
        api_key = usda_lib.get_api_key()
        food_data = usda_lib.get_food_details(fdc_id, api_key)
        
        # Extract required fields for saving
        description = food_data.get("description")
        if not description:
            result = {
                "status": "failure",
                "stdout": "",
                "stderr": "food_data missing required field 'description'",
            }
            return _dict_to_json_string(result)
        
        # Generate filepath
        ingredients_dir = Path(__file__).parent.parent / "ingredients"
        filename = f"{fdc_id}.json"
        filepath = ingredients_dir / filename
        
        # Save ingredient file
        usda_lib.save_ingredient_file(food_data, filepath)
        
        # Update reverse lookup
        usda_lib.update_reverse_lookup(fdc_id, description)
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "food": food_data,
            "filepath": str(filepath),
            "description": description,
            "message": f"Ingredient saved to {filepath}",
        }
        return _dict_to_json_string(result)
    except usda_lib.UsdaApiKeyError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"API key error: {e}",
        }
        return _dict_to_json_string(result)
    except requests.RequestException as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"API request failed: {e}",
        }
        return _dict_to_json_string(result)
    except OSError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"File operation failed: {e}",
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Delete an ingredient from the local database. This tool removes the ingredient "
        "JSON file from nutrition/ingredients/{fdc_id}.json and removes the entry from "
        "ingredient_lookup.json. Use this tool when you want to remove an ingredient that "
        "was previously saved. The description and fdc_id are required parameters. The "
        "response includes a success status. Check the 'status' key in the returned JSON "
        "to determine if the deletion was successful."
    )
)
async def delete_ingredient(description: str, fdc_id: int) -> str:
    """Delete an ingredient from the local database.

    Args:
        description: Ingredient description/name.
        fdc_id: FoodData Central ID (integer).

    Returns:
        JSON string with success status.
    """
    try:
        ingredient_management_lib.delete_ingredient(description, fdc_id)
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "message": f"Successfully deleted ingredient: {description} (FDC ID: {fdc_id})",
        }
        return _dict_to_json_string(result)
    except FileNotFoundError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Lookup database not found: {e}",
        }
        return _dict_to_json_string(result)
    except OSError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"File operation failed: {e}",
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Update the tags database from the RecipeTag enum. This tool reads all tags "
        "defined in the RecipeTag enum (the source of truth) and updates the tags.json "
        "file to match. Use this tool after adding new tags to recipe_tags.py to ensure "
        "the tags database is synchronized. The response includes the number of tags "
        "updated and a success status."
    )
)
async def update_tags_database() -> str:
    """Update tags database from RecipeTag enum.

    Returns:
        JSON string with success status and number of tags updated.
    """
    try:
        # Call the internal function from tag_management module
        tag_management._update_tags_database()
        
        # Count tags in enum
        tag_count = len(list(recipe_tags.RecipeTag))
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "message": f"Successfully updated tags database with {tag_count} tags",
            "tag_count": tag_count,
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Failed to update tags database: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Calculate nutrition facts for a recipe file. This tool reads a recipe JSON file, "
        "loads all ingredient data by FDC ID, converts ingredient amounts to grams using "
        "measure conversion, scales nutrients based on gram weight, and sums all nutrients "
        "across ingredients. The result is per-serving nutrition facts (divided by serving_size). "
        "The recipe file is updated in place with the calculated nutrition_facts and macros fields. "
        "The recipe_path should be relative to the nutrition/recipes directory (e.g., 'chicken_mac_and_cheese.json') "
        "or an absolute path. Check the 'status' key in the returned JSON to determine if the "
        "calculation was successful."
    )
)
async def calculate_recipe_nutrition_tool(recipe_path: str) -> str:
    """Calculate nutrition facts for a recipe.

    Args:
        recipe_path: Path to recipe JSON file (relative to nutrition/recipes or absolute).

    Returns:
        JSON string with success status and nutrition calculation results.
    """
    try:
        # Resolve recipe path
        recipes_dir = calculate_recipe_nutrition._get_recipes_dir()
        if Path(recipe_path).is_absolute():
            recipe_file = Path(recipe_path)
        else:
            recipe_file = recipes_dir / recipe_path
        
        if not recipe_file.exists():
            result = {
                "status": "failure",
                "stdout": "",
                "stderr": f"Recipe file not found: {recipe_file}",
            }
            return _dict_to_json_string(result)
        
        # Load recipe to get current state
        with open(recipe_file, "r", encoding="utf-8") as f:
            recipe_before = json.load(f)
        
        # Calculate and update nutrition
        updated = calculate_recipe_nutrition._update_recipe_nutrition(recipe_file)
        
        if not updated:
            result = {
                "status": "failure",
                "stdout": "",
                "stderr": f"Failed to update recipe: {recipe_file.name}",
            }
            return _dict_to_json_string(result)
        
        # Load updated recipe to get results
        with open(recipe_file, "r", encoding="utf-8") as f:
            recipe_after = json.load(f)
        
        nutrition_facts = recipe_after.get("nutrition_facts", {})
        macros = recipe_after.get("macros", {})
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "message": f"Successfully calculated nutrition for {recipe_file.name}",
            "recipe_path": str(recipe_file),
            "nutrient_count": len(nutrition_facts),
            "energy_kcal": nutrition_facts.get("Energy (kcal)", 0.0),
            "macros": macros,
        }
        return _dict_to_json_string(result)
    except FileNotFoundError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"File not found: {e}",
        }
        return _dict_to_json_string(result)
    except ValueError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Validation error: {e}",
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Calculate nutrition facts for a meal file. This tool reads a meal JSON file, "
        "loads all recipe data referenced in the meal, scales recipe nutrition facts by "
        "the number of servings specified for each recipe, and sums all nutrients across "
        "all recipes in the meal. The meal file is updated in place with the calculated "
        "nutrition_facts and macros fields. The meal_path should be relative to the "
        "nutrition/meals directory (e.g., 'chicken_mac_and_cheese_meal.json') or an "
        "absolute path. Note: This will first ensure all recipes are up-to-date before "
        "calculating meal nutrition. Check the 'status' key in the returned JSON to "
        "determine if the calculation was successful."
    )
)
async def calculate_meal_nutrition(meal_path: str) -> str:
    """Calculate nutrition facts for a meal.

    Args:
        meal_path: Path to meal JSON file (relative to nutrition/meals or absolute).

    Returns:
        JSON string with success status and nutrition calculation results.
    """
    try:
        # Resolve meal path
        meals_dir = meal_nutrition_module._get_meals_dir()
        if Path(meal_path).is_absolute():
            meal_file = Path(meal_path)
        else:
            meal_file = meals_dir / meal_path
        
        if not meal_file.exists():
            result = {
                "status": "failure",
                "stdout": "",
                "stderr": f"Meal file not found: {meal_file}",
            }
            return _dict_to_json_string(result)
        
        # Load meal to get current state
        with open(meal_file, "r", encoding="utf-8") as f:
            meal_before = json.load(f)
        
        # Calculate and update nutrition
        updated = meal_nutrition_module._update_meal_nutrition(meal_file)
        
        if not updated:
            result = {
                "status": "failure",
                "stdout": "",
                "stderr": f"Failed to update meal: {meal_file.name}",
            }
            return _dict_to_json_string(result)
        
        # Load updated meal to get results
        with open(meal_file, "r", encoding="utf-8") as f:
            meal_after = json.load(f)
        
        nutrition_facts = meal_after.get("nutrition_facts", {})
        macros = meal_after.get("macros", {})
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "message": f"Successfully calculated nutrition for {meal_file.name}",
            "meal_path": str(meal_file),
            "nutrient_count": len(nutrition_facts),
            "energy_kcal": nutrition_facts.get("Energy (kcal)", 0.0),
            "macros": macros,
        }
        return _dict_to_json_string(result)
    except FileNotFoundError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"File not found: {e}",
        }
        return _dict_to_json_string(result)
    except ValueError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Validation error: {e}",
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Validate all ingredient files in the database. This tool checks that all ingredient "
        "JSON files have energy (kcal) data required for recipe nutrition calculations. "
        "Returns a list of ingredients missing energy data if any are found. Check the 'status' "
        "key in the returned JSON to determine if validation was successful. If 'status' is "
        "'success' and 'all_valid' is True, all ingredients are valid. If 'all_valid' is False, "
        "check the 'missing_energy' array for details about ingredients that need to be fixed."
    )
)
async def validate_ingredients_tool() -> str:
    """Validate all ingredient files.

    Returns:
        JSON string with validation results including list of ingredients missing energy data.
    """
    try:
        # Import the validation functions
        ingredients_dir = validate_ingredients._get_ingredients_dir()
        
        if not ingredients_dir.exists():
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": f"Ingredients directory not found: {ingredients_dir}",
                "missing_energy": [],
            }
            return _dict_to_json_string(result)
        
        ingredient_files = list(ingredients_dir.glob("*.json"))
        # Exclude ingredient_lookup.json from validation
        ingredient_files = [f for f in ingredient_files if f.name != "ingredient_lookup.json"]
        
        if not ingredient_files:
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": "No ingredient files found.",
                "missing_energy": [],
            }
            return _dict_to_json_string(result)
        
        missing_energy = []
        for ingredient_file in ingredient_files:
            if not validate_ingredients._validate_ingredient_energy(ingredient_file):
                # Extract FDC ID from filename
                fdc_id = ingredient_file.stem
                try:
                    # Try to get ingredient name from the file
                    with open(ingredient_file, "r", encoding="utf-8") as f:
                        ingredient_data = json.load(f)
                        ingredient_name = ingredient_data.get("description", "Unknown")
                except Exception:
                    ingredient_name = "Unknown"
                
                missing_energy.append({
                    "fdc_id": fdc_id,
                    "name": ingredient_name,
                })
        
        all_valid = len(missing_energy) == 0
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "all_valid": all_valid,
            "total_ingredients": len(ingredient_files),
            "missing_energy": missing_energy,
            "message": (
                f"All {len(ingredient_files)} ingredients are valid."
                if all_valid
                else f"{len(missing_energy)} ingredient(s) missing energy (kcal) data."
            ),
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error during validation: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Validate all recipe files in the database. This tool checks that all recipe JSON files "
        "use valid tags from the RecipeTag enum and reference ingredients that exist in the "
        "ingredients directory. Returns lists of invalid tags and missing ingredients if any are "
        "found. Check the 'status' key in the returned JSON to determine if validation was "
        "successful. If 'status' is 'success' and 'all_valid' is True, all recipes are valid. "
        "If 'all_valid' is False, check the 'invalid_recipes' array for details about recipes "
        "that need to be fixed."
    )
)
async def validate_recipes_tool() -> str:
    """Validate all recipe files.

    Returns:
        JSON string with validation results including lists of invalid tags and missing ingredients.
    """
    try:
        # Import the validation functions
        recipes_dir = validate_recipes._get_recipes_dir()
        
        if not recipes_dir.exists():
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": f"Recipes directory not found: {recipes_dir}",
                "invalid_recipes": [],
            }
            return _dict_to_json_string(result)
        
        recipe_files = list(recipes_dir.glob("*.json"))
        
        if not recipe_files:
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": "No recipe files found.",
                "invalid_recipes": [],
            }
            return _dict_to_json_string(result)
        
        invalid_recipes = []
        for recipe_file in recipe_files:
            recipe_issues = {
                "recipe": recipe_file.name,
                "invalid_tags": [],
                "missing_ingredients": [],
            }
            
            # Validate tags
            invalid_tags = validate_recipes._validate_recipe_tags(recipe_file)
            if invalid_tags:
                recipe_issues["invalid_tags"] = invalid_tags
            
            # Validate ingredients
            missing_ingredients = validate_recipes._validate_recipe_ingredients(recipe_file)
            if missing_ingredients:
                recipe_issues["missing_ingredients"] = [
                    {"fdc_id": fdc_id, "name": name}
                    for fdc_id, name in missing_ingredients
                ]
            
            if recipe_issues["invalid_tags"] or recipe_issues["missing_ingredients"]:
                invalid_recipes.append(recipe_issues)
        
        all_valid = len(invalid_recipes) == 0
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "all_valid": all_valid,
            "total_recipes": len(recipe_files),
            "invalid_recipes": invalid_recipes,
            "message": (
                f"All {len(recipe_files)} recipes are valid."
                if all_valid
                else f"{len(invalid_recipes)} recipe(s) contain invalid tags or missing ingredients."
            ),
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error during validation: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get instructions for adding volume/weight measurements to an ingredient. "
        "This tool returns instructions directing the agent to ask the user to use "
        "the add_volume_to_ingredient.py script when an ingredient is missing "
        "required foodPortion data. Use this tool when recipe nutrition calculation "
        "fails due to missing volume measurements for an ingredient."
    )
)
async def add_food_portion() -> str:
    """Get instructions for adding food portion measurements.
    
    Returns:
        String with instructions to ask the user to use add_volume_to_ingredient.py script.
    """
    message = (
        "To add volume/weight measurements to an ingredient, please ask the user to run "
        "the add_volume_to_ingredient.py script. The script is located at "
        "nutrition/scripts/add_volume_to_ingredient.py and requires the following arguments: "
        "FDC ID, amount (e.g., 1.0), unit (e.g., 'Cup', 'Tbsp', 'Tsp', 'Clove', 'Whole'), "
        "and grams (weight in grams for that volume amount). "
        "Example: python3 nutrition/scripts/add_volume_to_ingredient.py <fdc_id> 1.0 Cup 240.0"
    )
    return message


if __name__ == "__main__":
    mcp.run(transport="stdio")

