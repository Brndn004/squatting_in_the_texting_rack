#!/usr/bin/env python3
"""Validate routine files.

Validates that routine JSON files conform to the routine schema.
"""

from pathlib import Path


def get_routines_dir() -> Path:
    """Get the routines directory path.
    
    Returns:
        Path to the routines directory.
    """
    return Path(__file__).parent.parent / "routines"


def get_all_routine_files() -> list[Path]:
    """Get all routine JSON files.
    
    Returns:
        List of paths to routine JSON files.
        
    Raises:
        FileNotFoundError: If routines directory does not exist.
    """
    routines_dir = get_routines_dir()
    if not routines_dir.exists():
        raise FileNotFoundError(f"Routines directory not found: {routines_dir}")
    return sorted(routines_dir.glob("*.json"))


def validate_routine(routine_path: Path) -> None:
    """Validate a routine file.
    
    Args:
        routine_path: Path to routine JSON file.
        
    Raises:
        ValueError: If routine is invalid.
    """
    # TODO: Implement validation logic
    # - Validate JSON structure against routine_schema.json
    # - Validate that percent_1rm is between 0 and 1 (inclusive) for all exercises in all sessions
    # - Validate that exercise_name references existing exercise files
    print(f"Validation for routine file {routine_path} will be implemented later.")


def validate_all_routines() -> None:
    """Validate all routine files.
    
    Raises:
        FileNotFoundError: If routines directory does not exist.
        ValueError: If no routine files found or if any routine is invalid.
    """
    routine_files = get_all_routine_files()
    if not routine_files:
        raise ValueError("No routine files found in routines directory")
    
    for routine_path in routine_files:
        validate_routine(routine_path)


def main() -> None:
    """Main entry point for routine validation."""
    validate_all_routines()


if __name__ == "__main__":
    main()

