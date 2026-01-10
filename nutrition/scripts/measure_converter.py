#!/usr/bin/env python3
"""Convert recipe measures to USDA foodPortions.

Simple library that matches quantity + MeasureUnit to foodPortions from ingredient data.
"""

import enum
import re
import typing


class MeasureUnit(str, enum.Enum):
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
    def values(cls) -> typing.List[str]:
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
    portion: typing.Dict[str, typing.Any],
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
        # Check if any unit alias is contained in the modifier (e.g., "tsp, ground" contains "tsp")
        for alias in unit_aliases:
            if alias in normalized_modifier:
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


def _extract_base_amount(portion: typing.Dict[str, typing.Any]) -> float:
    """Extract base amount from portion description or amount field.
    
    Args:
        portion: FoodPortion dictionary with 'portionDescription' and/or 'amount' fields.
    
    Returns:
        Base amount.
    
    Raises:
        MeasureMatchError: If no numeric amount can be extracted from portion description
            or amount field.
    """
    desc = portion.get("portionDescription", "")
    
    # First, try to extract amount from portionDescription
    if desc and desc != "(none)":
        base_match = re.search(r'^(\d+(?:\.\d+)?)', desc)
        if base_match:
            return float(base_match.group(1))
    
    # If portionDescription is empty or doesn't contain a number, check amount field
    amount = portion.get("amount")
    if amount is not None:
        try:
            amount_float = float(amount)
            if amount_float > 0:
                return amount_float
        except (ValueError, TypeError):
            pass
    
    # Neither portionDescription nor amount field provides a valid amount
    desc_str = f"'{desc}'" if desc else "empty"
    amount_str = f"{amount}" if amount is not None else "missing"
    raise MeasureMatchError(
        f"Cannot extract base amount from foodPortion. "
        f"portionDescription is {desc_str}, amount field is {amount_str}. "
        f"Either portionDescription must start with a numeric amount (e.g., '1 cup', '2 tablespoons') "
        f"or amount field must be a positive number."
    )


def _format_available_portions(food_portions: typing.List[typing.Dict[str, typing.Any]]) -> str:
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
    food_portions: typing.List[typing.Dict[str, typing.Any]]
) -> typing.Tuple[typing.Dict[str, typing.Any], float]:
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
    
    # Handle weight units (Oz, Lb, Gram, Kg) FIRST - they should never match portions
    # Since USDA data is per 100g, we can calculate directly from weight
    weight_units = {MeasureUnit.Oz, MeasureUnit.Lb, MeasureUnit.Gram, MeasureUnit.Kg}
    
    if unit in weight_units:
        # Convert to grams directly - weight units should never match portions
        if unit == MeasureUnit.Oz:
            gram_weight = quantity * 28.3495  # 1 oz = 28.3495 g
        elif unit == MeasureUnit.Lb:
            gram_weight = quantity * 453.592  # 1 lb = 453.592 g
        elif unit == MeasureUnit.Gram:
            gram_weight = quantity
        elif unit == MeasureUnit.Kg:
            gram_weight = quantity * 1000  # 1 kg = 1000 g
        
        # Return a dummy portion with the calculated weight
        # The caller will use this weight directly with per-100g nutrition data
        dummy_portion = {
            "modifier": "",
            "portionDescription": f"{quantity} {unit.value}",
            "gramWeight": gram_weight
        }
        return (dummy_portion, gram_weight)
    
    unit_aliases = _get_unit_aliases(unit)
    
    # Find best matching portion (for non-weight units only)
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
    
    # Require a valid match for non-weight units - no fallbacks allowed
    if not best_match or best_score == 0:
        available_str = _format_available_portions(food_portions)
        raise MeasureMatchError(
            f"Could not find matching foodPortion for {quantity} {unit.value}. "
            f"No foodPortion found with matching modifier or description. "
            f"This is a hard error - no fallback assumptions are made. "
            f"Please use a weight unit (Gram, Oz, Lb, Kg) or ensure the ingredient has a matching portion. "
            f"\nAvailable foodPortions:\n{available_str}"
            f"\n\nTo add volume information, run: python3 add_volume_to_ingredient.py <fdc_id> <amount> <unit> <grams>"
            f"\nExample: python3 add_volume_to_ingredient.py <fdc_id> 1.0 {unit.value} <grams_per_unit>"
        )
    
    # Calculate gram weight
    # Try to extract base amount - if this fails, provide context about the matched portion
    try:
        base_amount = _extract_base_amount(best_match)
    except MeasureMatchError as e:
        # Re-raise with context about the matched portion
        modifier = best_match.get("modifier", "")
        desc = best_match.get("portionDescription", "")
        amount = best_match.get("amount")
        gram_weight = best_match.get("gramWeight", 0)
        
        modifier_info = f"modifier='{modifier}'" if modifier else "modifier missing"
        desc_info = f"portionDescription='{desc}'" if desc else "portionDescription missing"
        amount_info = f"amount={amount}" if amount is not None else "amount missing"
        
        raise MeasureMatchError(
            f"Found matching foodPortion by {unit.value} unit, but cannot determine base amount. "
            f"The portion matched by modifier/description but lacks valid amount information. "
            f"\nMatched portion details: {modifier_info}, {desc_info}, {amount_info}, gramWeight={gram_weight}g. "
            f"\nOriginal error: {str(e)}"
            f"\n\nTo fix this issue, run: python3 add_volume_to_ingredient.py <fdc_id> <amount> <unit> <grams>"
            f"\nExample: python3 add_volume_to_ingredient.py <fdc_id> 1.0 {unit.value} {gram_weight}"
        ) from e
    
    gram_weight = best_match.get("gramWeight", 0)
    calculated_weight = (quantity / base_amount) * gram_weight
    
    return (best_match, calculated_weight)
