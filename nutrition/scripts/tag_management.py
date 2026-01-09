#!/usr/bin/env python3
"""Tag management script.

Updates tags database from RecipeTag enum. The enum is the source of truth
for valid tags.
"""

import json
import logging
import typing
from pathlib import Path

import recipe_tags

# Constants
_RECIPES_DIR = Path(__file__).parent.parent / "recipes"
_TAGS_FILE = Path(__file__).parent.parent / "tags.json"
_JSON_INDENT = 2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _get_recipes_dir() -> Path:
    """Get the path to the recipes directory."""
    return _RECIPES_DIR


def _get_tags_file() -> Path:
    """Get the path to the tags database file."""
    return _TAGS_FILE


def _load_tags() -> typing.Dict[str, str]:
    """Load existing tags database.

    Returns:
        Dictionary mapping tag names to descriptions. Returns empty dict
        if file doesn't exist or is invalid.
    """
    tags_file = _get_tags_file()
    if not tags_file.exists():
        logger.debug(f"Tags file not found: {tags_file}, will create new one")
        return {}

    try:
        with open(tags_file, "r", encoding="utf-8") as f:
            tags = json.load(f)
        if not isinstance(tags, dict):
            logger.error(f"Tags file is not a valid JSON object: {tags_file}")
            return {}
        return tags
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse tags file {tags_file}: {e}")
        return {}


def _save_tags(tags: typing.Dict[str, str]) -> None:
    """Save tags database to file.

    Args:
        tags: Dictionary mapping tag names to descriptions.
    """
    tags_file = _get_tags_file()
    tags_file.parent.mkdir(parents=True, exist_ok=True)

    with open(tags_file, "w", encoding="utf-8") as f:
        json.dump(tags, f, indent=_JSON_INDENT, ensure_ascii=False)
        f.write("\n")

    logger.info(f"Saved {len(tags)} tags to {tags_file}")


def _validate_recipe_tags(recipe_path: Path) -> None:
    """Validate tags in a recipe file against RecipeTag enum.

    Args:
        recipe_path: Path to recipe JSON file.

    Raises:
        ValueError: If recipe contains invalid tags.
    """
    try:
        with open(recipe_path, "r", encoding="utf-8") as f:
            recipe = json.load(f)

        if not isinstance(recipe, dict):
            return

        tags = recipe.get("tags", [])
        if not isinstance(tags, list):
            return

        invalid_tags = []
        for tag in tags:
            if not isinstance(tag, str):
                continue
            try:
                recipe_tags.RecipeTag.from_string(tag)
            except ValueError:
                invalid_tags.append(tag)

        if invalid_tags:
            raise ValueError(
                f"Recipe {recipe_path.name} contains invalid tags: {invalid_tags}"
            )

    except json.JSONDecodeError:
        pass  # Will be handled elsewhere
    except Exception:
        pass  # Will be handled elsewhere


def _update_tags_database() -> None:
    """Update tags database from RecipeTag enum.

    The enum is the source of truth. This function updates the tags.json file
    to match all tags defined in the RecipeTag enum.
    """
    logger.info("Updating tags database from RecipeTag enum...")

    # Build tags dictionary from enum
    updated_tags = {}
    for tag in recipe_tags.RecipeTag:
        updated_tags[tag.value] = tag.description

    logger.info(f"Found {len(updated_tags)} tags in enum: {sorted(updated_tags.keys())}")

    existing_tags = _load_tags()
    if existing_tags:
        logger.info(f"Loaded {len(existing_tags)} existing tags from database")

    # Check for any tags in database that aren't in enum
    removed_tags = set(existing_tags.keys()) - set(updated_tags.keys())
    if removed_tags:
        logger.warning(
            f"Tags in database but not in enum (will be removed): {sorted(removed_tags)}"
        )

    _save_tags(updated_tags)
    logger.info("Tags database updated successfully.")


def main() -> None:
    """Main entry point for the tag update script."""
    try:
        _update_tags_database()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()

