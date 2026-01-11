#!/usr/bin/env python3
"""Create exercise files.

Creates a new fitness exercise file with exercise name and 1RM.
"""

import json
import re
from pathlib import Path

import date_utils
import fitness_paths
import validate_exercise


def slugify(text: str) -> str:
    """Convert text to a slugified version suitable for filenames.
    
    Args:
        text: Text to slugify.
        
    Returns:
        Slugified text (lowercase, spaces replaced with underscores, special chars removed).
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and hyphens with underscores
    text = re.sub(r'[\s-]+', '_', text)
    # Remove all non-alphanumeric characters except underscores
    text = re.sub(r'[^a-z0-9_]', '', text)
    # Remove multiple consecutive underscores
    text = re.sub(r'_+', '_', text)
    # Remove leading/trailing underscores
    text = text.strip('_')
    
    if not text:
        raise ValueError("Slugified name cannot be empty")
    
    return text


def prompt_exercise_name() -> str:
    """Prompt user for human-readable exercise name.
    
    Returns:
        Human-readable exercise name as a string.
    """
    print("Exercise name:")
    while True:
        name_input = input("  Name (e.g., 'Barbell Squat', 'Bench Press', 'Deadlift'): ").strip()
        
        if not name_input:
            print("  Error: Exercise name cannot be empty.")
            continue
        
        try:
            slugify(name_input)
        except ValueError as e:
            print(f"  Error: {e}")
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
        
        if value < 0:
            print("  Error: 1RM cannot be negative.")
            continue
        
        return {"lb": value}


def create_exercise_data(name: str, exercise_name: str, datetime_str: str, one_rm: dict) -> dict:
    """Create exercise data dictionary.
    
    Args:
        name: Human-readable name of the exercise.
        exercise_name: Slugified name of the exercise (used for filename).
        datetime_str: Datetime in format YYYY-MM-DD-<unix epoch seconds>.
        one_rm: Dictionary with unit and value.
        
    Returns:
        Exercise data dictionary.
    """
    return {
        "name": name,
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
    exercises_dir = fitness_paths.get_exercises_dir()
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


def create_single_exercise() -> None:
    """Create a single exercise file by prompting user for input.
    
    Raises:
        ValueError: If invalid input provided or validation fails.
        OSError: If file cannot be written.
    """
    datetime_str = date_utils.get_current_datetime()
    
    # Validate datetime format
    parts = datetime_str.split("-")
    if len(parts) < 4:
        raise ValueError(f"Invalid datetime format: {datetime_str}. Expected YYYY-MM-DD-<unix epoch seconds>")
    
    while True:
        name = prompt_exercise_name()
        exercise_name = slugify(name)
        filepath = get_exercise_filepath(exercise_name, datetime_str)
        
        if filepath.exists():
            print(f"  Error: Exercise file already exists: {filepath.name}")
            print()
            continue
        
        break
    
    one_rm = prompt_1rm()
    
    exercise_data = create_exercise_data(name, exercise_name, datetime_str, one_rm)
    save_exercise_file(exercise_data, filepath)
    
    print(f"\nExercise saved to: {filepath}")
    
    print("\nValidating exercise...")
    validate_exercise_file(filepath)
    print("Validation passed.")


def create_exercise() -> None:
    """Create exercise files in a loop, allowing multiple exercises to be created.
    
    Raises:
        ValueError: If invalid input provided or validation fails.
        OSError: If file cannot be written.
    """
    print("Creating exercises (press Ctrl+C to finish)")
    print()
    
    try:
        while True:
            create_single_exercise()
            print()
    except KeyboardInterrupt:
        print("\nFinished creating exercises.")


def main() -> None:
    """Main entry point for exercise creation."""
    create_exercise()


if __name__ == "__main__":
    main()
