#!/usr/bin/env python3
"""Convert recipe measures to USDA foodPortions.

Simple library that matches quantity + MeasureUnit to foodPortions from ingredient data.
"""

import re
from enum import Enum
from typing import Dict, List, Tuple, Any


class MeasureUnit(str, Enum):
    """Enumeration of valid measure units for recipes.
    
    All units must be written exactly as shown (capitalized first letter).
    """
    # Volume units
    Cup = "Cup"
    Tbsp = "Tbsp"
    Tsp = "Tsp"
    Fl_Oz = "Fl Oz"
    Pint = "Pint"
    Quart = "Quart"
    Gallon = "Gallon"
    Ml = "Ml"
    Liter = "Liter"
    
    # Weight units
    Oz = "Oz"
    Lb = "Lb"
    Gram = "Gram"
    Kg = "Kg"
    
    # Count units
    Piece = "Piece"
    Whole = "Whole"
    Slice = "Slice"
    Clove = "Clove"
    Head = "Head"
    Stalk = "Stalk"
    Bunch = "Bunch"
    
    @classmethod
    def values(cls) -> List[str]:
        """Get list of all valid unit values."""
        return [unit.value for unit in cls]


class MeasureMatchError(Exception):
    """Raised when no matching foodPortion can be found."""
    pass


def _get_unit_aliases(unit: MeasureUnit) -> set[str]:
    """Get aliases for a unit to match against USDA data.
    
    Args:
        unit: MeasureUnit enum value.
    
    Returns:
        Set of unit aliases (lowercase) for matching.
    """
    unit_map = {
        MeasureUnit.Cup: ["cup", "cups", "c"],
        MeasureUnit.Tbsp: ["tablespoon", "tablespoons", "tbsp", "tbs", "T"],
        MeasureUnit.Tsp: ["teaspoon", "teaspoons", "tsp", "t"],
        MeasureUnit.Fl_Oz: ["fluid ounce", "fl oz", "floz", "fl. oz.", "fluid ounces"],
        MeasureUnit.Pint: ["pint", "pints", "pt"],
        MeasureUnit.Quart: ["quart", "quarts", "qt"],
        MeasureUnit.Gallon: ["gallon", "gallons", "gal"],
        MeasureUnit.Ml: ["milliliter", "milliliters", "ml", "mL"],
        MeasureUnit.Liter: ["liter", "liters", "litres", "l", "L"],
        MeasureUnit.Oz: ["ounce", "ounces", "oz"],
        MeasureUnit.Lb: ["pound", "pounds", "lb", "lbs"],
        MeasureUnit.Gram: ["gram", "grams", "g"],
        MeasureUnit.Kg: ["kilogram", "kilograms", "kg"],
        MeasureUnit.Piece: ["piece", "pieces", "pc", "pcs"],
        MeasureUnit.Whole: ["whole", "item", "items"],
        MeasureUnit.Slice: ["slice", "slices"],
        MeasureUnit.Clove: ["clove", "cloves"],
        MeasureUnit.Head: ["head", "heads"],
        MeasureUnit.Stalk: ["stalk", "stalks"],
        MeasureUnit.Bunch: ["bunch", "bunches"],
    }
    return set(unit_map.get(unit, [unit.value.lower()]))


def _normalize_portion_description(desc: str) -> str:
    """Normalize a portion description for matching.
    
    Removes leading numbers and converts to lowercase.
    
    Args:
        desc: Portion description (e.g., "1 cup", "1 tablespoon").
    
    Returns:
        Normalized string.
    """
    if not desc:
        return ""
    desc = re.sub(r'^\d+\s*', '', desc.lower())
    return desc.strip()


def _normalize_modifier(modifier: str) -> str:
    """Normalize a modifier for matching.
    
    Args:
        modifier: Modifier string (e.g., "cup", "tbsp", "10205").
    
    Returns:
        Normalized string (lowercase, stripped).
    """
    if not modifier:
        return ""
    return modifier.lower().strip()


def _score_portion_match(
    portion: Dict[str, Any],
    unit_aliases: set[str]
) -> int:
    """Score how well a portion matches the unit.
    
    Args:
        portion: FoodPortion dictionary.
        unit_aliases: Set of unit aliases to match against.
    
    Returns:
        Score: 100 = exact modifier match, 80 = description starts with unit,
               50 = description contains unit, 0 = no match.
    """
    modifier = portion.get("modifier", "")
    desc = portion.get("portionDescription", "")
    
    # Exact modifier match (highest priority)
    if modifier:
        normalized_modifier = _normalize_modifier(modifier)
        if normalized_modifier in unit_aliases:
            return 100
    
    # Description match (medium priority)
    if desc:
        normalized_desc = _normalize_portion_description(desc)
        for alias in unit_aliases:
            if alias in normalized_desc:
                if normalized_desc.startswith(alias):
                    return 80
                else:
                    return 50
    
    return 0


def _extract_base_amount(desc: str) -> float:
    """Extract base amount from portion description.
    
    Args:
        desc: Portion description (e.g., "1 cup", "2 tablespoons").
    
    Returns:
        Base amount (defaults to 1.0 if not found).
    """
    if not desc:
        return 1.0
    
    base_match = re.search(r'^(\d+(?:\.\d+)?)', desc)
    if base_match:
        return float(base_match.group(1))
    
    return 1.0


def _format_available_portions(food_portions: List[Dict[str, Any]]) -> str:
    """Format available portions for error messages.
    
    Args:
        food_portions: List of foodPortion dictionaries.
    
    Returns:
        Formatted string listing available portions.
    """
    available = []
    for portion in food_portions:
        modifier = portion.get("modifier", "")
        desc = portion.get("portionDescription", "")
        gram_weight = portion.get("gramWeight", 0)
        
        if gram_weight > 0:
            info = []
            if modifier:
                info.append(f"modifier='{modifier}'")
            if desc:
                info.append(f"description='{desc}'")
            if info:
                available.append(f"  - {', '.join(info)}")
    
    if available:
        return "\n".join(available)
    return "  (none with valid gramWeight)"


def find_food_portion(
    quantity: float,
    unit: MeasureUnit,
    food_portions: List[Dict[str, Any]]
) -> Tuple[Dict[str, Any], float]:
    """Find matching foodPortion for quantity and unit.
    
    This is the main entrypoint for the library. Given a quantity, unit enum,
    and list of foodPortions, it finds the best matching portion and calculates
    the gram weight.
    
    Args:
        quantity: Amount in the specified unit (must be > 0).
        unit: MeasureUnit enum value.
        food_portions: List of foodPortion dictionaries from ingredient JSON.
    
    Returns:
        Tuple of (matched_food_portion, calculated_gram_weight).
        The gram weight is calculated based on the quantity and the portion's
        base amount (e.g., if portion is "1 cup" = 244g, then 2 cups = 488g).
    
    Raises:
        MeasureMatchError: If no matching foodPortion can be found. The error
            message includes details about available portions to help debug.
    
    Example:
        >>> food_portions = [{"id": 123, "modifier": "cup", "gramWeight": 244}]
        >>> portion, weight = find_food_portion(2.0, MeasureUnit.Cup, food_portions)
        >>> weight
        488.0
        >>> portion["id"]
        123
    """
    if not food_portions:
        raise MeasureMatchError("No foodPortions available in ingredient data")
    
    if quantity <= 0:
        raise ValueError(f"Quantity must be greater than zero, got {quantity}")
    
    unit_aliases = _get_unit_aliases(unit)
    
    # Find best matching portion
    best_match = None
    best_score = 0
    
    for portion in food_portions:
        gram_weight = portion.get("gramWeight", 0)
        if gram_weight <= 0:
            continue
        
        score = _score_portion_match(portion, unit_aliases)
        if score > best_score:
            best_score = score
            best_match = portion
    
    # Require a valid match
    if not best_match or best_score == 0:
        available_str = _format_available_portions(food_portions)
        raise MeasureMatchError(
            f"Could not find matching foodPortion for {quantity} {unit.value}. "
            f"No foodPortion found with matching modifier or description. "
            f"\nAvailable foodPortions:\n{available_str}"
        )
    
    # Calculate gram weight
    desc = best_match.get("portionDescription", "")
    base_amount = _extract_base_amount(desc)
    gram_weight = best_match.get("gramWeight", 0)
    calculated_weight = (quantity / base_amount) * gram_weight
    
    return (best_match, calculated_weight)
