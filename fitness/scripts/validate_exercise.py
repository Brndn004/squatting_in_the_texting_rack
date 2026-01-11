#!/usr/bin/env python3
"""Validate exercise files.

Validates that exercise JSON files conform to the exercise schema.
"""

from pathlib import Path

import exercise_discovery
import fitness_paths


def validate_exercise(exercise_path: Path) -> None:
    """Validate an exercise file.
    
    Args:
        exercise_path: Path to exercise JSON file.
        
    Raises:
        ValueError: If exercise is invalid.
    """
    # TODO: Implement validation logic
    # - Validate JSON structure against exercise_schema.json
    print(f"Validation for exercise file {exercise_path} will be implemented later.")


def validate_all_exercises() -> None:
    """Validate all exercise files.
    
    Raises:
        FileNotFoundError: If exercises directory does not exist.
        ValueError: If no exercise files found or if any exercise is invalid.
    """
    exercise_files = exercise_discovery.discover_exercise_files()
    
    for exercise_path in exercise_files:
        validate_exercise(exercise_path)


def main() -> None:
    """Main entry point for exercise validation."""
    validate_all_exercises()


if __name__ == "__main__":
    main()

