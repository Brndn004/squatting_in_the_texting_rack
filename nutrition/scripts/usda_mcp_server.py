#!/usr/bin/env python3
"""MCP server for USDA Food Data Central ingredient lookup.

Provides tools for searching, retrieving, and saving USDA ingredient data.
"""

from pathlib import Path
from typing import Any

import json
import requests

from mcp.server import fastmcp

import ingredient_management_lib
import usda_lib

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
        "including all nutrients, food components, and metadata. Use this tool after "
        "searching for an ingredient to get detailed nutrition information. The FDC ID "
        "can be obtained from the search_ingredient tool results. The response includes "
        "the complete food object with all available nutrition facts, food components, "
        "and descriptive information. Check the 'status' key in the returned JSON to "
        "determine if the request was successful."
    )
)
async def get_ingredient_details(fdc_id: int) -> str:
    """Get full details for a specific ingredient by FDC ID.

    Args:
        fdc_id: FoodData Central ID (integer, e.g., 2705385 for whole milk).

    Returns:
        JSON string containing full ingredient data including nutrition facts.
    """
    try:
        api_key = usda_lib.get_api_key()
        food_data = usda_lib.get_food_details(fdc_id, api_key)
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "food": food_data,
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
        "Save ingredient data to a local JSON file and update the reverse lookup database. "
        "This tool saves the food data object (obtained from get_ingredient_details) to "
        "nutrition/ingredients/{fdc_id}.json and adds an entry to ingredient_lookup.json. "
        "Use this tool after calling get_ingredient_details to persist ingredient data locally. "
        "Pass the 'food' object from the get_ingredient_details response as food_data. "
        "The fdc_id and description are automatically extracted from food_data. The response includes "
        "the filepath where the data was saved and the description used. Check the 'status' key "
        "in the returned JSON to determine if the save operation was successful."
    )
)
async def save_ingredient(food_data: dict[str, Any]) -> str:
    """Save ingredient data to local file and update lookup database.

    Args:
        food_data: Complete food data dictionary from get_ingredient_details response (extract the 'food' field).
                   Must contain 'fdcId' and 'description' fields.

    Returns:
        JSON string with success message, file path, and description used.
    """
    try:
        # Extract required fields from food_data
        fdc_id = food_data.get("fdcId")
        if not fdc_id:
            result = {
                "status": "failure",
                "stdout": "",
                "stderr": "food_data missing required field 'fdcId'",
            }
            return _dict_to_json_string(result)
        
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
            "filepath": str(filepath),
            "description": description,
        }
        return _dict_to_json_string(result)
    except KeyError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Missing required field in food_data: {e}",
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


if __name__ == "__main__":
    mcp.run(transport="stdio")

