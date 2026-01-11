#!/usr/bin/env python3
"""Fitness units enumeration.

Defines all valid fitness units for measurements.
"""

import enum


class FitnessUnits(str, enum.Enum):
    """Enumeration of valid fitness units.
    
    Units for weight, height, and quantity.
    """
    
    # Weight units
    LB = "lb"
    KG = "kg"
    
    # Height units
    IN = "in"
    CM = "cm"
    
    # Quantity (count)
    QUANTITY = "quantity"
    
    @classmethod
    def values(cls) -> list[str]:
        """Get list of all valid unit values."""
        return [unit.value for unit in cls]

