#!/usr/bin/env python3
"""View recipe ingredients and instructions.

Usage:
    python view_recipe.py path/to/recipe.json
"""

import json
import sys
from pathlib import Path


def format_ingredient(ingredient: dict) -> str:
    """Format a single ingredient for display."""
    quantity = ingredient["quantity"]
    unit = ingredient["measure_unit"]
    name = ingredient["name"]
    
    # Format quantity (remove .0 if it's a whole number)
    if quantity == int(quantity):
        quantity_str = str(int(quantity))
    else:
        quantity_str = str(quantity)
    
    result = f"  {quantity_str} {unit} {name}"
    
    if "notes" in ingredient:
        notes = ", ".join(ingredient["notes"])
        result += f" ({notes})"
    
    return result


def format_instruction(instruction: dict) -> str:
    """Format a single instruction for display."""
    step_id = instruction["step_id"]
    text = instruction["text"]
    return f"  {step_id}. {text}"


def view_recipe(recipe_path: Path) -> None:
    """Display recipe ingredients and instructions."""
    if not recipe_path.exists():
        raise FileNotFoundError(f"Recipe file not found: {recipe_path}")
    
    if not recipe_path.is_file():
        raise ValueError(f"Path is not a file: {recipe_path}")
    
    with open(recipe_path, "r", encoding="utf-8") as f:
        recipe = json.load(f)
    
    if "name" not in recipe:
        raise KeyError(f"Recipe missing required field 'name': {recipe_path}")
    if "ingredients" not in recipe:
        raise KeyError(f"Recipe missing required field 'ingredients': {recipe_path}")
    if "instructions" not in recipe:
        raise KeyError(f"Recipe missing required field 'instructions': {recipe_path}")
    
    name = recipe["name"]
    ingredients = recipe["ingredients"]
    instructions = recipe["instructions"]
    
    # Display recipe name
    print(f"\n{name}")
    print("=" * len(name))
    
    # Display serving size if available
    if "serving_size" in recipe:
        print(f"\nServes: {recipe['serving_size']}")
    
    # Display ingredients
    print("\nIngredients:")
    print("-" * 50)
    for ingredient in ingredients:
        print(format_ingredient(ingredient))
    
    # Display instructions
    print("\nInstructions:")
    print("-" * 50)
    for instruction in instructions:
        print(format_instruction(instruction))
    
    print()


def main() -> None:
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python view_recipe.py path/to/recipe.json", file=sys.stderr)
        sys.exit(1)
    
    recipe_path = Path(sys.argv[1])
    
    try:
        view_recipe(recipe_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
