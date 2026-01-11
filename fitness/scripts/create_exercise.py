#!/usr/bin/env python3
"""Create exercise files.

Creates a new fitness exercise file with exercise name and 1RM.
"""

import json
from datetime import datetime
from pathlib import Path

import validate_exercise


def get_exercises_dir() -> Path:
    """Get the exercises directory path.
    
    Returns:
        Path to the exercises directory.
    """
    return Path(__file__).parent.parent / "exercises"


def get_current_datetime() -> str:
    """Get current datetime in format YYYY-MM-DD-<unix epoch seconds>.
    
    Returns:
        Current datetime as a string.
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    unix_seconds = int(now.timestamp())
    return f"{date_str}-{unix_seconds}"


def prompt_exercise_name() -> str:
    """Prompt user for exercise name.
    
    Returns:
        Exercise name as a string.
    """
    print("Exercise name:")
    while True:
        name_input = input("  Name (e.g., 'squat', 'bench_press', 'deadlift'): ").strip()
        
        if not name_input:
            print("  Error: Exercise name cannot be empty.")
            continue
        
        return name_input


def prompt_1rm() -> dict:
    """Prompt user for 1RM in pounds.
    
    Returns:
        Dictionary with unit and value (e.g., {"lb": 225}).
    """
    print("One-rep max (1RM):")
    while True:
        value_input = input("  Value (lb): ").strip()
        
        if not value_input:
            print("  Error: Value cannot be empty.")
            continue
        
        try:
            value = float(value_input)
        except ValueError:
            print(f"  Error: Invalid number: {value_input}")
            continue
        
        if value <= 0:
            print("  Error: 1RM must be positive.")
            continue
        
        return {"lb": value}


def create_exercise_data(exercise_name: str, datetime_str: str, one_rm: dict) -> dict:
    """Create exercise data dictionary.
    
    Args:
        exercise_name: Name of the exercise.
        datetime_str: Datetime in format YYYY-MM-DD-<unix epoch seconds>.
        one_rm: Dictionary with unit and value.
        
    Returns:
        Exercise data dictionary.
    """
    return {
        "exercise_name": exercise_name,
        "1rm": one_rm,
        "date_created": datetime_str,
    }


def save_exercise_file(exercise_data: dict, filepath: Path) -> None:
    """Save exercise data to JSON file.
    
    Args:
        exercise_data: Exercise data dictionary.
        filepath: Path where file should be saved.
        
    Raises:
        OSError: If file cannot be written.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(exercise_data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_exercise_filepath(exercise_name: str, datetime_str: str) -> Path:
    """Get exercise filepath for given exercise name.
    
    Args:
        exercise_name: Name of the exercise.
        datetime_str: Datetime in format YYYY-MM-DD-<unix epoch seconds> (unused, kept for API consistency).
        
    Returns:
        Path to exercise file.
    """
    exercises_dir = get_exercises_dir()
    filename = f"{exercise_name}.json"
    return exercises_dir / filename


def validate_exercise_file(filepath: Path) -> None:
    """Run validation on exercise file.
    
    Args:
        filepath: Path to exercise file to validate.
        
    Raises:
        ValueError: If validation fails.
    """
    validate_exercise.validate_exercise(filepath)


def create_exercise() -> None:
    """Create a new exercise file by prompting user for input.
    
    Raises:
        ValueError: If invalid input provided or validation fails.
        OSError: If file cannot be written.
    """
    datetime_str = get_current_datetime()
    
    # Extract date part for display
    parts = datetime_str.split("-")
    if len(parts) < 4:
        raise ValueError(f"Invalid datetime format: {datetime_str}. Expected YYYY-MM-DD-<unix epoch seconds>")
    
    date_part = parts[:3]
    date_str = "-".join(date_part)
    print(f"Creating exercise for {date_str}")
    print()
    
    exercise_name = prompt_exercise_name()
    one_rm = prompt_1rm()
    
    filepath = get_exercise_filepath(exercise_name, datetime_str)
    
    if filepath.exists():
        raise ValueError(f"Exercise file already exists: {filepath}")
    
    exercise_data = create_exercise_data(exercise_name, datetime_str, one_rm)
    save_exercise_file(exercise_data, filepath)
    
    print(f"\nExercise saved to: {filepath}")
    
    print("\nValidating exercise...")
    validate_exercise_file(filepath)
    print("Validation passed.")


def main() -> None:
    """Main entry point for exercise creation."""
    create_exercise()


if __name__ == "__main__":
    main()
