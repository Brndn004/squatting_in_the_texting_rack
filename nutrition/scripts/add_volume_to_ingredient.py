#!/usr/bin/env python3
"""Add volume information to an ingredient JSON file.

This script allows users to add volume-to-weight conversions to ingredient files
when USDA data doesn't include the necessary volume portions.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import ingredient_management_lib
import measure_converter


def _get_unit_modifier(unit: measure_converter.MeasureUnit) -> str:
    """Convert MeasureUnit enum to lowercase modifier string.
    
    Args:
        unit: MeasureUnit enum value.
    
    Returns:
        Lowercase modifier string (e.g., "cup", "tbsp", "tsp").
    """
    # Map units to their primary modifier form (first alias from _get_unit_aliases)
    unit_to_modifier = {
        measure_converter.MeasureUnit.Cup: "cup",
        measure_converter.MeasureUnit.Tbsp: "tbsp",
        measure_converter.MeasureUnit.Tsp: "tsp",
        measure_converter.MeasureUnit.Fl_Oz: "fl oz",
        measure_converter.MeasureUnit.Pint: "pint",
        measure_converter.MeasureUnit.Quart: "quart",
        measure_converter.MeasureUnit.Gallon: "gallon",
        measure_converter.MeasureUnit.Ml: "ml",
        measure_converter.MeasureUnit.Liter: "liter",
        measure_converter.MeasureUnit.Oz: "oz",
        measure_converter.MeasureUnit.Lb: "lb",
        measure_converter.MeasureUnit.Gram: "g",
        measure_converter.MeasureUnit.Kg: "kg",
        measure_converter.MeasureUnit.Piece: "piece",
        measure_converter.MeasureUnit.Whole: "whole",
        measure_converter.MeasureUnit.Slice: "slice",
        measure_converter.MeasureUnit.Clove: "clove",
        measure_converter.MeasureUnit.Head: "head",
        measure_converter.MeasureUnit.Stalk: "stalk",
        measure_converter.MeasureUnit.Bunch: "bunch",
    }
    if unit not in unit_to_modifier:
        raise ValueError(
            f"Unit {unit.value} is not supported for modifier conversion. "
            f"Supported units: {', '.join(sorted(u.value for u in unit_to_modifier.keys()))}"
        )
    return unit_to_modifier[unit]


def _format_unit_description(amount: float, unit: measure_converter.MeasureUnit) -> str:
    """Format human-readable portion description.
    
    Args:
        amount: Numeric amount.
        unit: MeasureUnit enum value.
    
    Returns:
        Formatted description (e.g., "1 cup", "2 tablespoons").
    """
    # Convert amount to int if it's a whole number
    amount_str = str(int(amount)) if amount == int(amount) else str(amount)
    
    # Use plural forms for clarity
    unit_str = unit.value
    if amount != 1.0:
        if unit == measure_converter.MeasureUnit.Tbsp:
            unit_str = "tablespoons"
        elif unit == measure_converter.MeasureUnit.Tsp:
            unit_str = "teaspoons"
        elif unit == measure_converter.MeasureUnit.Cup:
            unit_str = "cups"
        elif unit == measure_converter.MeasureUnit.Fl_Oz:
            unit_str = "fluid ounces"
        elif unit == measure_converter.MeasureUnit.Pint:
            unit_str = "pints"
        elif unit == measure_converter.MeasureUnit.Quart:
            unit_str = "quarts"
        elif unit == measure_converter.MeasureUnit.Gallon:
            unit_str = "gallons"
        elif unit == measure_converter.MeasureUnit.Oz:
            unit_str = "ounces"
        elif unit == measure_converter.MeasureUnit.Lb:
            unit_str = "pounds"
        elif unit == measure_converter.MeasureUnit.Gram:
            unit_str = "grams"
        elif unit == measure_converter.MeasureUnit.Kg:
            unit_str = "kilograms"
        elif unit == measure_converter.MeasureUnit.Ml:
            unit_str = "milliliters"
        elif unit == measure_converter.MeasureUnit.Liter:
            unit_str = "liters"
        elif unit == measure_converter.MeasureUnit.Piece:
            unit_str = "pieces"
        elif unit == measure_converter.MeasureUnit.Whole:
            unit_str = "wholes"
        elif unit == measure_converter.MeasureUnit.Slice:
            unit_str = "slices"
        elif unit == measure_converter.MeasureUnit.Clove:
            unit_str = "cloves"
        elif unit == measure_converter.MeasureUnit.Head:
            unit_str = "heads"
        elif unit == measure_converter.MeasureUnit.Stalk:
            unit_str = "stalks"
        elif unit == measure_converter.MeasureUnit.Bunch:
            unit_str = "bunches"
        else:
            # No fallback - raise error for unsupported units
            raise ValueError(
                f"Unit {unit.value} does not have plural form defined. "
                f"Please add plural form handling for this unit."
            )
    
    return f"{amount_str} {unit_str}"


def _find_existing_portion(
    food_portions: list, modifier: str, portion_description: str
) -> dict | None:
    """Find existing foodPortion with matching modifier or description.
    
    Args:
        food_portions: List of foodPortion dictionaries.
        modifier: Modifier string to match.
        portion_description: Portion description to match.
    
    Returns:
        Matching foodPortion dictionary if found, None otherwise.
    """
    modifier_lower = modifier.lower()
    desc_lower = portion_description.lower()
    
    for portion in food_portions:
        portion_modifier = portion.get("modifier", "").lower().strip()
        portion_desc = portion.get("portionDescription", "").lower().strip()
        
        # Skip empty modifiers/descriptions
        if not portion_modifier and not portion_desc:
            continue
        
        # Exact match or contains match (but not empty)
        if portion_modifier and (modifier_lower == portion_modifier or modifier_lower in portion_modifier or portion_modifier in modifier_lower):
            return portion
        if portion_desc and (desc_lower == portion_desc or desc_lower in portion_desc or portion_desc in desc_lower):
            return portion
    
    return None


def add_volume_to_ingredient(
    fdc_id: int,
    amount: float,
    unit: measure_converter.MeasureUnit,
    grams: float,
    force: bool = False,
) -> None:
    """Add volume information to an ingredient JSON file.
    
    Args:
        fdc_id: USDA FoodData Central ID.
        amount: Base amount for the volume unit (e.g., 1.0 for "1 cup").
        unit: MeasureUnit enum value.
        grams: Weight in grams for that volume amount.
        force: If True, overwrite existing portion without asking.
    
    Raises:
        FileNotFoundError: If ingredient file doesn't exist.
        ValueError: If arguments are invalid or portion already exists.
        json.JSONDecodeError: If ingredient file is invalid JSON.
        OSError: If file cannot be read or written.
    """
    # Validate arguments
    if amount <= 0:
        raise ValueError(f"Amount must be greater than zero, got {amount}")
    if grams <= 0:
        raise ValueError(f"Grams must be greater than zero, got {grams}")
    
    # Get ingredient file path
    ingredients_dir = ingredient_management_lib._get_ingredients_dir()
    ingredient_file = ingredients_dir / f"{fdc_id}.json"
    
    if not ingredient_file.exists():
        raise FileNotFoundError(
            f"Ingredient file not found: {ingredient_file}. "
            f"Make sure FDC ID {fdc_id} is correct."
        )
    
    # Load ingredient data - read as text first to preserve formatting
    try:
        with open(ingredient_file, "r", encoding="utf-8") as f:
            file_content = f.read()
            ingredient_data = json.loads(file_content)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in ingredient file {ingredient_file}: {e.msg}",
            e.doc,
            e.pos,
        )
    
    # Get foodPortions array - must exist and be a list
    if "foodPortions" not in ingredient_data:
        raise ValueError(
            f"Ingredient file {ingredient_file} is missing required 'foodPortions' field. "
            f"This field is required in USDA ingredient data."
        )
    
    food_portions = ingredient_data["foodPortions"]
    if not isinstance(food_portions, list):
        raise ValueError(
            f"Ingredient file {ingredient_file} has invalid 'foodPortions' field. "
            f"Expected list, got {type(food_portions).__name__}."
        )
    
    # Prepare new portion data
    modifier = _get_unit_modifier(unit)
    portion_description = _format_unit_description(amount, unit)
    
    # Check for existing portion
    existing_portion = _find_existing_portion(food_portions, modifier, portion_description)
    
    if existing_portion and not force:
        existing_modifier = existing_portion.get("modifier", "")
        existing_desc = existing_portion.get("portionDescription", "")
        existing_grams = existing_portion.get("gramWeight", 0)
        
        print(f"Warning: A foodPortion already exists with similar modifier/description:")
        print(f"  modifier: '{existing_modifier}'")
        print(f"  portionDescription: '{existing_desc}'")
        print(f"  gramWeight: {existing_grams}g")
        print(f"\nTo overwrite it, use the --force flag.")
        raise ValueError(
            f"FoodPortion already exists for {modifier}. Use --force to overwrite."
        )
    
    # Generate new ID and sequenceNumber
    # Require all portions to have id and sequenceNumber - no defaults allowed
    if not food_portions:
        raise ValueError(
            f"Ingredient file {ingredient_file} has empty 'foodPortions' array. "
            f"Cannot determine next ID and sequenceNumber."
        )
    
    ids = []
    sequences = []
    for i, p in enumerate(food_portions):
        if "id" not in p:
            raise ValueError(
                f"Ingredient file {ingredient_file} has foodPortion at index {i} missing required 'id' field. "
                f"All foodPortions must have an 'id' field."
            )
        if "sequenceNumber" not in p:
            raise ValueError(
                f"Ingredient file {ingredient_file} has foodPortion at index {i} missing required 'sequenceNumber' field. "
                f"All foodPortions must have a 'sequenceNumber' field."
            )
        ids.append(p["id"])
        sequences.append(p["sequenceNumber"])
    
    max_id = max(ids)
    max_sequence = max(sequences)
    
    new_id = max_id + 1
    new_sequence = max_sequence + 1
    
    # Create new foodPortion entry
    new_portion = {
        "id": new_id,
        "sequenceNumber": new_sequence,
        "amount": amount,
        "modifier": modifier,
        "portionDescription": portion_description,
        "gramWeight": grams,
        "measureUnit": {
            "id": 9999,
            "name": "undetermined",
            "abbreviation": "undetermined",
        },
    }
    
    # Add to foodPortions array
    if existing_portion and force:
        # Replace existing portion
        index = food_portions.index(existing_portion)
        existing_id = existing_portion.get("id")
        if existing_id is None:
            raise ValueError(
                f"Existing foodPortion at index {index} missing required 'id' field. "
                f"Cannot update portion without an ID."
            )
        food_portions[index] = new_portion
        print(f"Updated existing foodPortion (ID {existing_id})")
    else:
        # Append new portion
        food_portions.append(new_portion)
        print(f"Added new foodPortion (ID {new_id})")
    
    # Sort by sequenceNumber
    # Require all portions to have sequenceNumber - no defaults allowed
    for i, p in enumerate(food_portions):
        if "sequenceNumber" not in p:
            raise ValueError(
                f"FoodPortion at index {i} missing required 'sequenceNumber' field. "
                f"All foodPortions must have a 'sequenceNumber' field for sorting."
            )
    food_portions.sort(key=lambda p: p["sequenceNumber"])
    
    # Update the foodPortions in the data structure
    ingredient_data["foodPortions"] = food_portions
    
    # Replace only the foodPortions section in the original file content
    # This preserves all other formatting, spacing, and structure
    
    # Find the start of the foodPortions array in the file
    start_match = re.search(r'"foodPortions"\s*:\s*\[', file_content)
    if not start_match:
        raise ValueError(f"Could not find 'foodPortions' array in file {ingredient_file}")
    
    start_pos = start_match.start()
    # Find the matching closing bracket
    bracket_count = 0
    in_string = False
    escape_next = False
    pos = start_match.end() - 1  # Start from the opening bracket
    
    for i in range(pos, len(file_content)):
        char = file_content[i]
        
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        
        if in_string:
            continue
        
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end_pos = i + 1
                break
    else:
        raise ValueError(f"Could not find matching closing bracket for 'foodPortions' array")
    
    # Extract prefix (everything up to but not including "foodPortions": [)
    # and suffix (everything after the closing bracket])
    prefix = file_content[:start_match.start()]
    suffix = file_content[end_pos:]
    
    # Detect indentation pattern from existing array content
    original_array_content = file_content[start_match.end():end_pos-1]  # Content between [ and ]
    array_lines = original_array_content.split('\n')
    
    # Find the indent of the "foodPortions" line
    line_start = file_content.rfind('\n', 0, start_pos) + 1
    foodportions_line_start = file_content[line_start:start_match.start()]
    foodportions_indent = len(foodportions_line_start) - len(foodportions_line_start.lstrip())
    
    # Detect indentation pattern: find first property line and first nested property line
    # This is required - we cannot proceed without detecting the indentation pattern
    item_property_indent = None
    nested_property_indent = None
    
    for line in array_lines:
        stripped = line.lstrip()
        if not stripped or stripped in ['{', '}', '[', ']']:
            continue
        line_indent = len(line) - len(stripped)
        if item_property_indent is None:
            item_property_indent = line_indent
        elif nested_property_indent is None and line_indent > item_property_indent:
            nested_property_indent = line_indent
            break
    
    # Require detection of item property indent - no defaults allowed
    if item_property_indent is None:
        raise ValueError(
            f"Could not detect indentation pattern from 'foodPortions' array in file {ingredient_file}. "
            f"The array appears to be empty or contains no property lines. "
            f"Cannot preserve formatting without detecting the indentation pattern."
        )
    
    # Calculate indent per level (how many spaces json.dumps should add per nesting level)
    if nested_property_indent is not None:
        indent_per_level = nested_property_indent - item_property_indent
        if indent_per_level <= 0:
            raise ValueError(
                f"Invalid indentation pattern detected in file {ingredient_file}. "
                f"Nested property indent ({nested_property_indent}) must be greater than "
                f"item property indent ({item_property_indent})."
            )
    else:
        # If no nested properties detected, calculate from the structure
        # item_property_indent represents properties inside the object (level 1)
        # The object itself starts at foodportions_indent + some amount
        # We can calculate: item_property_indent = object_start + indent_per_level
        # So: indent_per_level = item_property_indent - object_start
        # Find object start indent by looking for '{' lines
        object_start_indent = None
        for line in array_lines:
            stripped = line.lstrip()
            if stripped == '{':
                object_start_indent = len(line) - len(stripped)
                break
        
        if object_start_indent is None:
            raise ValueError(
                f"Could not detect object start indentation in 'foodPortions' array in file {ingredient_file}. "
                f"Cannot determine indent_per_level without detecting object structure. "
                f"Detected item property indent: {item_property_indent}."
            )
        
        indent_per_level = item_property_indent - object_start_indent
        if indent_per_level <= 0:
            raise ValueError(
                f"Invalid indentation pattern detected in file {ingredient_file}. "
                f"Item property indent ({item_property_indent}) must be greater than "
                f"object start indent ({object_start_indent})."
            )
        
        # Set nested_property_indent for later use (for level 2+ properties)
        nested_property_indent = item_property_indent + indent_per_level
    
    # Calculate base indent for the array (where the '[' should start)
    # The array should be indented to match the space after "foodPortions": 
    array_base_indent = foodportions_indent + len('"foodPortions": ')
    
    # Serialize with detected indent pattern
    food_portions_json = json.dumps(food_portions, indent=indent_per_level, ensure_ascii=False)
    
    # Adjust indentation: json.dumps starts at column 0, we need to match the file
    lines = food_portions_json.split('\n')
    adjusted_lines = []
    for line in lines:
        if not line.strip():
            adjusted_lines.append('')
            continue
        
        stripped = line.lstrip()
        json_indent = len(line) - len(stripped)
        
        # Calculate target indent based on nesting level
        if stripped == '[':
            # Opening bracket: should be at array_base_indent
            target_indent = array_base_indent
        elif stripped == ']':
            # Closing bracket: should align with opening bracket
            target_indent = array_base_indent
        elif stripped == '{':
            # Object opening: typically foodportions_indent + 4 (for array item)
            target_indent = foodportions_indent + 4
        elif stripped == '}':
            # Object closing: same as opening
            target_indent = foodportions_indent + 4
        else:
            # Property line: calculate level from json_indent
            if indent_per_level <= 0:
                raise ValueError(
                    f"Invalid indent_per_level ({indent_per_level}) detected. "
                    f"This should not happen - indent_per_level must be positive."
                )
            level = json_indent // indent_per_level
            
            if level == 0:
                raise ValueError(
                    f"Unexpected indentation level 0 for property line '{stripped[:50]}...'. "
                    f"This should not happen - property lines should be at level 1 or higher. "
                    f"json_indent={json_indent}, indent_per_level={indent_per_level}"
                )
            elif level == 1:
                # First level property (inside object)
                # item_property_indent is guaranteed to be not None from earlier check
                target_indent = item_property_indent
            else:
                # Nested property (inside nested object like measureUnit)
                # nested_property_indent is guaranteed to be not None from earlier check
                # For deeper nesting, add indent_per_level for each additional level
                additional_levels = level - 2  # level 2 is nested_property_indent, level 3+ adds more
                target_indent = nested_property_indent + (additional_levels * indent_per_level)
        
        adjusted_lines.append(' ' * target_indent + stripped)
    
    food_portions_json = '\n'.join(adjusted_lines)
    
    # Reconstruct the file content
    new_content = prefix + '"foodPortions": ' + food_portions_json + suffix
    
    # Save updated file
    try:
        with open(ingredient_file, "w", encoding="utf-8") as f:
            f.write(new_content)
    except OSError as e:
        raise OSError(f"Failed to write ingredient file {ingredient_file}: {e}")
    
    # Print success message
    print(f"\nSuccessfully added volume information to ingredient {fdc_id}:")
    print(f"  {portion_description} = {grams}g")
    print(f"\nYou may want to recalculate recipe nutrition:")
    print(f"  python3 calculate_recipe_nutrition.py <recipe_file>")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Add volume information to an ingredient JSON file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add: 1 cup = 40g for oats (FDC 2346396)
  python3 add_volume_to_ingredient.py 2346396 1.0 Cup 40.0

  # Add: 1 tablespoon = 15g for chia seeds (FDC 2710819)
  python3 add_volume_to_ingredient.py 2710819 1.0 Tbsp 15.0

  # Overwrite existing portion
  python3 add_volume_to_ingredient.py 2346396 1.0 Cup 40.0 --force
        """,
    )
    
    parser.add_argument(
        "fdc_id",
        type=int,
        help="USDA FoodData Central ID (integer)",
    )
    parser.add_argument(
        "amount",
        type=float,
        help="Base amount for the volume unit (e.g., 1.0 for '1 cup')",
    )
    parser.add_argument(
        "unit",
        type=str,
        help="MeasureUnit enum value (e.g., 'Cup', 'Tbsp', 'Tsp')",
    )
    parser.add_argument(
        "grams",
        type=float,
        help="Weight in grams for that volume amount",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing foodPortion if it exists",
    )
    
    args = parser.parse_args()
    
    # Validate unit
    unit_enum = None
    for measure_unit in measure_converter.MeasureUnit:
        if measure_unit.value == args.unit:
            unit_enum = measure_unit
            break
    
    if unit_enum is None:
        valid_units = ", ".join(sorted(measure_converter.MeasureUnit.values()))
        parser.error(
            f"Invalid unit '{args.unit}'. Must be one of: {valid_units}"
        )
    
    # Call main function
    try:
        add_volume_to_ingredient(
            args.fdc_id,
            args.amount,
            unit_enum,
            args.grams,
            force=args.force,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

