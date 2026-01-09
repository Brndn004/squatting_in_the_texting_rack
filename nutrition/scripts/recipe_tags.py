#!/usr/bin/env python3
"""Recipe tag enumeration.

Defines all valid recipe tags and their descriptions.
"""

import enum


class RecipeTag(str, enum.Enum):
    """Enumeration of valid recipe tags.

    Each tag has a name (used as the enum value) and a description.
    Recipes should reference tags using these enum values (e.g., RecipeTag.DRINK).
    """

    DRINK = "drink"
    WARM = "warm"
    SIMPLE = "simple"

    def __init__(self, value: str) -> None:
        """Initialize tag with value and description."""
        self._value_ = value
        # Set description based on tag value
        descriptions = {
            "drink": "Liquid-based recipes meant to be consumed as beverages",
            "warm": "Recipes that are served warm or heated",
            "simple": "Recipes with minimal ingredients and straightforward preparation",
        }
        self._description = descriptions.get(value, "")

    @property
    def description(self) -> str:
        """Get the description for this tag."""
        return self._description

    @classmethod
    def values(cls) -> list[str]:
        """Get list of all valid tag values."""
        return [tag.value for tag in cls]

    @classmethod
    def from_string(cls, tag_string: str) -> "RecipeTag":
        """Create RecipeTag from string value.

        Args:
            tag_string: String tag value.

        Returns:
            RecipeTag enum value.

        Raises:
            ValueError: If tag_string is not a valid tag.
        """
        try:
            return cls(tag_string)
        except ValueError:
            valid_tags = ", ".join(cls.values())
            raise ValueError(
                f"Invalid tag '{tag_string}'. Valid tags are: {valid_tags}"
            ) from None

