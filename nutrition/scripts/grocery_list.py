#!/usr/bin/env python3
"""
Generate a grocery list CSV from selected recipes.

This script:
1. Lists all available recipes
2. Prompts user to select recipes
3. Collects and combines ingredients from selected recipes
4. Formats ingredients with generics first (e.g., "Milk, Whole")
5. Sorts alphabetically
6. Outputs as CSV: Ingredient, Qty MeasureUnit
"""

import json
import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


def _get_recipes_dir() -> Path:
    """Get the path to the recipes directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "recipes"


def _get_all_recipes() -> List[Tuple[str, int, Path]]:
    """Get all recipe files.
    
    Returns:
        List of tuples: (name, serving_size, recipe_file_path)
    """
    recipes_dir = _get_recipes_dir()
    recipes = []
    
    for recipe_file in sorted(recipes_dir.glob("*.json")):
        try:
            with open(recipe_file, "r", encoding="utf-8") as f:
                recipe = json.load(f)
                name = recipe.get("name", recipe_file.stem)
                serving_size = recipe.get("serving_size", 0)
                recipes.append((name, serving_size, recipe_file))
        except (json.JSONDecodeError, Exception):
            # Skip invalid JSON files
            continue
    
    return recipes


def _format_ingredient_name(name: str) -> str:
    """Format ingredient name with generics first, only one comma.
    
    Examples:
        "Milk, whole" -> "Milk, Whole"
        "Banana, raw" -> "Banana"
        "Onions, yellow, raw" -> "Onion, Yellow"
        "Black beans, from canned, no added fat" -> "Beans, Black Canned"
        "Beef, flank, steak, boneless, choice" -> "Beef, Flank Steak Boneless Choice"
        "Olive oil" -> "Oil, Olive"
    """
    name = name.strip()
    
    # Remove meaningless suffixes
    meaningless = [", raw", ", cooked", ", as ingredient", " raw", " cooked", " as ingredient"]
    for suffix in meaningless:
        name = name.replace(suffix, "")
    
    # Handle plural to singular
    plural_map = {
        "Onions": "Onion",
        "Peppers": "Pepper", 
        "Carrots": "Carrot",
        "Mushrooms": "Mushroom",
        "Tomatoes": "Tomato"
    }
    for plural, singular in plural_map.items():
        if name.startswith(plural):
            name = name.replace(plural, singular, 1)
            break
    
    # Handle oils
    if name.lower() == "olive oil":
        return "Oil, Olive"
    elif name.lower() == "sesame oil":
        return "Oil, Sesame"
    elif name.startswith("Oil, "):
        parts = name.split(", ", 1)
        return f"{parts[0].title()}, {parts[1].title()}" if len(parts) == 2 else name.title()
    elif " oil" in name.lower() and not name.startswith("Oil,"):
        parts = name.split()
        if "oil" in parts:
            oil_idx = parts.index("oil")
            return f"Oil, {' '.join(parts[:oil_idx]).title()}"
    
    # Handle beans - extract color/type descriptor
    if "bean" in name.lower():
        # Split by comma
        if "," in name:
            parts = [p.strip() for p in name.split(",")]
            # Find part with "bean"
            bean_idx = next((i for i, p in enumerate(parts) if "bean" in p.lower()), None)
            if bean_idx is not None:
                bean_part = parts[bean_idx]
                bean_words = bean_part.split()
                # Extract descriptor before "beans/bean"
                descriptor_words = []
                generic = "Beans"
                
                for word in bean_words:
                    if "bean" not in word.lower():
                        descriptor_words.append(word)
                
                # Collect other meaningful descriptors
                for i, part in enumerate(parts):
                    if i != bean_idx:
                        part_lower = part.lower()
                        # Extract "canned" from "from canned"
                        if "canned" in part_lower:
                            descriptor_words.append("Canned")
                        elif part_lower not in ["from", "no added fat", "nfs", "no", "added", "fat"]:
                            # Add meaningful words
                            words = part.split()
                            for w in words:
                                w_lower = w.lower()
                                if w_lower not in ["from", "no", "added", "fat"]:
                                    descriptor_words.append(w)
                
                if descriptor_words:
                    return f"{generic}, {' '.join(descriptor_words).title()}"
                return generic
        else:
            # No comma: "Black beans" -> "Beans, Black"
            words = name.split()
            if len(words) >= 2 and "bean" in words[-1].lower():
                return f"Beans, {' '.join(words[:-1]).title()}"
    
    # General case: split by comma
    if "," in name:
        parts = [p.strip() for p in name.split(",")]
        generic = parts[0]
        descriptors = []
        
        for part in parts[1:]:
            part_lower = part.lower()
            if part_lower in ["from", "no added fat", "nfs"]:
                continue
            elif "canned" in part_lower:
                descriptors.append("Canned")
            elif "from" in part_lower and "canned" in part_lower:
                descriptors.append("Canned")
            else:
                descriptors.append(part)
        
        generic = generic.title()
        if descriptors:
            return f"{generic}, {' '.join(descriptors).title()}"
        return generic
    else:
        # No comma - check if descriptor before noun
        words = name.split()
        if len(words) >= 2:
            last_word = words[-1].lower()
            if last_word in ["beans", "bean", "oil", "juice", "sauce"]:
                generic = words[-1].title()
                if generic.lower() == "beans":
                    generic = "Beans"
                return f"{generic}, {' '.join(words[:-1]).title()}"
        
        return name.title()


def _collect_ingredients(recipe_paths: List[Path]) -> List[Dict[str, any]]:
    """Collect ingredients from selected recipes without combining duplicates.
    
    Returns:
        List of ingredient dictionaries, each with:
            'quantity': quantity,
            'measure_unit': measure_unit,
            'formatted_name': formatted_name,
            'notes': list of notes
    """
    ingredients = []
    
    for recipe_path in recipe_paths:
        try:
            with open(recipe_path, "r", encoding="utf-8") as f:
                recipe = json.load(f)
            
            recipe_ingredients = recipe.get("ingredients", [])
            for ingredient in recipe_ingredients:
                raw_name = ingredient.get("name", "")
                quantity = ingredient.get("quantity", 0.0)
                measure_unit = ingredient.get("measure_unit", "")
                notes = ingredient.get("notes", [])
                
                if not raw_name or quantity == 0:
                    continue
                
                formatted_name = _format_ingredient_name(raw_name)
                
                # Add each ingredient as a separate entry (no combining)
                ingredients.append({
                    'quantity': float(quantity),
                    'measure_unit': measure_unit,
                    'formatted_name': formatted_name,
                    'notes': notes.copy() if notes else []
                })
        
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error reading {recipe_path}: {e}", file=sys.stderr)
            continue
    
    return ingredients


def _format_quantity(quantity: float) -> str:
    """Format quantity as string, removing unnecessary decimals."""
    if quantity == int(quantity):
        return str(int(quantity))
    else:
        return str(quantity)


def _print_recipe_list(recipes: List[Tuple[str, int, Path]]) -> None:
    """Print the list of available recipes."""
    print("\nAvailable recipes:")
    print("-" * 70)
    for i, (name, serving_size, _) in enumerate(recipes, 1):
        print(f"{i}. {name} ({serving_size} servings)")
    print("-" * 70)


def main():
    """Main function to generate grocery list."""
    recipes = _get_all_recipes()
    
    if not recipes:
        print("No recipes found!", file=sys.stderr)
        sys.exit(1)
    
    # Print initial recipe list
    _print_recipe_list(recipes)
    
    # Iterative recipe selection
    selected_recipes = []
    selected_recipe_info = []  # List of (name, count) tuples for display
    
    print("\nSelect recipes (enter 'Done' when finished):")
    while True:
        print("\nWhich recipe? (enter number or 'Done'):")
        recipe_input = input().strip()
        
        if recipe_input.lower() == "done":
            break
        
        try:
            recipe_num = int(recipe_input)
            if recipe_num < 1 or recipe_num > len(recipes):
                print(f"Invalid recipe number. Please enter a number between 1 and {len(recipes)}.")
                continue
            
            idx = recipe_num - 1
            recipe_name, serving_size, recipe_path = recipes[idx]
            
            print(f"How many of '{recipe_name}'?")
            count_input = input().strip()
            
            try:
                count = int(count_input)
                if count < 1:
                    print("Count must be at least 1. Skipping this recipe.")
                    continue
                
                # Add recipe path 'count' times
                selected_recipes.extend([recipe_path] * count)
                selected_recipe_info.append((recipe_name, count))
                
                print(f"Added {count}x '{recipe_name}'")
                
                # Reprint recipe list after successful entry
                _print_recipe_list(recipes)
                
            except ValueError:
                print(f"Invalid count '{count_input}'. Please enter a number. Skipping this recipe.")
                continue
                
        except ValueError:
            print(f"Invalid input '{recipe_input}'. Please enter a recipe number or 'Done'.")
            continue
    
    if not selected_recipes:
        print("\nNo recipes selected!", file=sys.stderr)
        sys.exit(1)
    
    # Display summary
    print("\n" + "-" * 70)
    print("Selected recipes:")
    for name, count in selected_recipe_info:
        if count > 1:
            print(f"  - {name} (x{count})")
        else:
            print(f"  - {name}")
    print("-" * 70)
    
    # Collect ingredients
    ingredients = _collect_ingredients(selected_recipes)
    
    if not ingredients:
        print("No ingredients found in selected recipes!", file=sys.stderr)
        sys.exit(1)
    
    # Sort alphabetically by ingredient name
    sorted_ingredients = sorted(ingredients, key=lambda x: x['formatted_name'])
    
    # Get output filename
    print("\nEnter output CSV filename (default: grocery_list.csv):")
    output_filename = input().strip()
    if not output_filename:
        output_filename = "grocery_list.csv"
    if not output_filename.endswith(".csv"):
        output_filename += ".csv"
    
    # Write CSV (without header, without quotes)
    output_path = _get_recipes_dir().parent / output_filename
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        for ingredient in sorted_ingredients:
            formatted_name = ingredient['formatted_name']
            quantity = _format_quantity(ingredient['quantity'])
            measure_unit = ingredient['measure_unit']
            qty_unit = f"{quantity} {measure_unit}" if measure_unit else quantity
            
            # Include notes in ingredient name if present
            notes = ingredient.get('notes', [])
            if notes:
                # Join notes with semicolons if multiple
                notes_str = "; ".join(notes)
                ingredient_display = f"{formatted_name} ({notes_str})"
            else:
                ingredient_display = formatted_name
            
            # Write without quotes: Ingredient, Qty MeasureUnit
            f.write(f"{ingredient_display}, {qty_unit}\n")
    
    print(f"\nGrocery list saved to: {output_path}")
    print(f"Total ingredients: {len(sorted_ingredients)}")


if __name__ == "__main__":
    main()

