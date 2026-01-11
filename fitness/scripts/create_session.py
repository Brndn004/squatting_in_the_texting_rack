#!/usr/bin/env python3
"""Create session files.

Creates a new fitness session file with exercises.
"""

import json
import re
from datetime import datetime
from pathlib import Path

import validate_session


def get_exercises_dir() -> Path:
    """Get the exercises directory path.
    
    Returns:
        Path to the exercises directory.
    """
    return Path(__file__).parent.parent / "exercises"


def get_sessions_dir() -> Path:
    """Get the sessions directory path.
    
    Returns:
        Path to the sessions directory.
    """
    return Path(__file__).parent.parent / "sessions"


def get_current_datetime() -> str:
    """Get current datetime in format YYYY-MM-DD-<unix epoch seconds>.
    
    Returns:
        Current datetime as a string.
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    unix_seconds = int(now.timestamp())
    return f"{date_str}-{unix_seconds}"


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


def get_available_exercises() -> list[tuple[str, str]]:
    """Get list of available exercises from exercise files.
    
    Returns:
        List of tuples (human-readable name, exercise_name slug) sorted by human-readable name.
        
    Raises:
        FileNotFoundError: If exercises directory does not exist.
        ValueError: If no exercise files found or if exercise files are invalid.
    """
    exercises_dir = get_exercises_dir()
    if not exercises_dir.exists():
        raise FileNotFoundError(f"Exercises directory not found: {exercises_dir}")
    
    exercise_files = sorted(exercises_dir.glob("*.json"))
    if not exercise_files:
        raise ValueError("No exercise files found in exercises directory")
    
    exercises = []
    for exercise_file in exercise_files:
        try:
            with open(exercise_file, "r", encoding="utf-8") as f:
                exercise_data = json.load(f)
            
            if not isinstance(exercise_data, dict):
                raise ValueError(f"Exercise file is not a valid JSON object: {exercise_file}")
            
            if "name" not in exercise_data:
                raise ValueError(f"Exercise file missing 'name' field: {exercise_file}")
            
            if "exercise_name" not in exercise_data:
                raise ValueError(f"Exercise file missing 'exercise_name' field: {exercise_file}")
            
            name = exercise_data["name"]
            exercise_name = exercise_data["exercise_name"]
            
            if not isinstance(name, str):
                raise ValueError(f"Exercise name must be a string in {exercise_file}")
            
            if not isinstance(exercise_name, str):
                raise ValueError(f"Exercise name slug must be a string in {exercise_file}")
            
            if not name:
                raise ValueError(f"Exercise name cannot be empty in {exercise_file}")
            
            if not exercise_name:
                raise ValueError(f"Exercise name slug cannot be empty in {exercise_file}")
            
            exercises.append((name, exercise_name))
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse exercise file {exercise_file}: {e}")
    
    if not exercises:
        raise ValueError("No valid exercises found")
    
    # Sort by human-readable name
    return sorted(exercises, key=lambda x: x[0])


def prompt_session_name() -> str:
    """Prompt user for human-readable session name.
    
    Returns:
        Human-readable session name as a string.
    """
    print("Session name:")
    while True:
        name_input = input("  Name (e.g., 'Push Day', 'Pull Day', 'Leg Day'): ").strip()
        
        if not name_input:
            print("  Error: Session name cannot be empty.")
            continue
        
        try:
            slugify(name_input)
        except ValueError as e:
            print(f"  Error: {e}")
            continue
        
        return name_input


def display_available_exercises(available_exercises: list[tuple[str, str]]) -> None:
    """Display available exercises in a numbered list.
    
    Args:
        available_exercises: List of tuples (human-readable name, exercise_name slug).
    """
    print("  Available exercises:")
    for i, (name, exercise_name) in enumerate(available_exercises, 1):
        print(f"    {i}. {name}")


def prompt_sets() -> int:
    """Prompt user for number of sets.
    
    Returns:
        Number of sets as an integer.
    """
    while True:
        value_input = input("    Sets: ").strip()
        
        if not value_input:
            print("    Error: Value cannot be empty.")
            continue
        
        try:
            value = int(value_input)
        except ValueError:
            print(f"    Error: Invalid number: {value_input}")
            continue
        
        if value <= 0:
            print("    Error: Sets must be positive.")
            continue
        
        return value


def prompt_reps() -> int:
    """Prompt user for number of reps.
    
    Returns:
        Number of reps as an integer.
    """
    while True:
        value_input = input("    Reps: ").strip()
        
        if not value_input:
            print("    Error: Value cannot be empty.")
            continue
        
        try:
            value = int(value_input)
        except ValueError:
            print(f"    Error: Invalid number: {value_input}")
            continue
        
        if value <= 0:
            print("    Error: Reps must be positive.")
            continue
        
        return value


def prompt_percent_1rm() -> float:
    """Prompt user for percent 1RM (as percentage 0-100, converted to decimal 0-1).
    
    Returns:
        Percent 1RM as a decimal (0-1).
    """
    while True:
        value_input = input("    Percent 1RM (0-100): ").strip()
        
        if not value_input:
            print("    Error: Value cannot be empty.")
            continue
        
        try:
            value = float(value_input)
        except ValueError:
            print(f"    Error: Invalid number: {value_input}")
            continue
        
        if value < 0 or value > 100:
            print("    Error: Percent 1RM must be between 0 and 100.")
            continue
        
        # Convert to decimal (0-1)
        return value / 100


def prompt_session_exercises(available_exercises: list[tuple[str, str]]) -> list[dict]:
    """Prompt user for exercises in a session.
    
    Args:
        available_exercises: List of tuples (human-readable name, exercise_name slug).
        
    Returns:
        List of exercise dictionaries for the session.
    """
    exercises = []
    
    while True:
        display_available_exercises(available_exercises)
        print()
        print(f"  Exercise {len(exercises) + 1} (or type 'Done' to finish):")
        exercise_input = input("  Select exercise (number or name, or 'Done'): ").strip()
        
        if exercise_input.lower() == "done":
            break
        
        if not exercise_input:
            print("  Error: Selection cannot be empty.")
            continue
        
        # Try to parse as number
        exercise_name = None
        try:
            selection_num = int(exercise_input)
            if 1 <= selection_num <= len(available_exercises):
                exercise_name = available_exercises[selection_num - 1][1]  # Return exercise_name slug
            else:
                print(f"  Error: Invalid selection number. Must be between 1 and {len(available_exercises)}.")
                continue
        except ValueError:
            # Try to match by human-readable name or exercise_name slug
            for name, ex_name in available_exercises:
                if exercise_input == name or exercise_input == ex_name:
                    exercise_name = ex_name
                    break
            
            if exercise_name is None:
                print(f"  Error: Exercise '{exercise_input}' not found. Please select from available exercises.")
                continue
        
        sets = prompt_sets()
        reps = prompt_reps()
        percent_1rm = prompt_percent_1rm()
        
        exercises.append({
            "exercise_name": exercise_name,
            "sets": sets,
            "reps": reps,
            "percent_1rm": percent_1rm,
        })
        print()
    
    return exercises


def create_session_data(name: str, session_name: str, datetime_str: str, exercises: list[dict]) -> dict:
    """Create session data dictionary.
    
    Args:
        name: Human-readable name of the session.
        session_name: Slugified name of the session (used for filename).
        datetime_str: Datetime in format YYYY-MM-DD-<unix epoch seconds>.
        exercises: List of exercise dictionaries.
        
    Returns:
        Session data dictionary.
    """
    return {
        "name": name,
        "session_name": session_name,
        "exercises": exercises,
        "date_created": datetime_str,
    }


def save_session_file(session_data: dict, filepath: Path) -> None:
    """Save session data to JSON file.
    
    Args:
        session_data: Session data dictionary.
        filepath: Path where file should be saved.
        
    Raises:
        OSError: If file cannot be written.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_session_filepath(session_name: str, datetime_str: str) -> Path:
    """Get session filepath for given session name.
    
    Args:
        session_name: Slugified name of the session.
        datetime_str: Datetime in format YYYY-MM-DD-<unix epoch seconds> (unused, kept for API consistency).
        
    Returns:
        Path to session file.
    """
    sessions_dir = get_sessions_dir()
    filename = f"{session_name}.json"
    return sessions_dir / filename


def validate_session_file(filepath: Path) -> None:
    """Run validation on session file.
    
    Args:
        filepath: Path to session file to validate.
        
    Raises:
        ValueError: If validation fails.
    """
    validate_session.validate_session(filepath)


def create_single_session() -> None:
    """Create a single session file by prompting user for input.
    
    Raises:
        ValueError: If invalid input provided or validation fails.
        FileNotFoundError: If exercises directory does not exist.
        OSError: If file cannot be written.
    """
    datetime_str = get_current_datetime()
    
    # Validate datetime format
    parts = datetime_str.split("-")
    if len(parts) < 4:
        raise ValueError(f"Invalid datetime format: {datetime_str}. Expected YYYY-MM-DD-<unix epoch seconds>")
    
    available_exercises = get_available_exercises()
    print(f"Found {len(available_exercises)} available exercises")
    print()
    
    while True:
        name = prompt_session_name()
        session_name = slugify(name)
        filepath = get_session_filepath(session_name, datetime_str)
        
        if filepath.exists():
            print(f"  Error: Session file already exists: {filepath.name}")
            print()
            continue
        
        break
    
    print()
    exercises = prompt_session_exercises(available_exercises)
    
    session_data = create_session_data(name, session_name, datetime_str, exercises)
    save_session_file(session_data, filepath)
    
    print(f"\nSession saved to: {filepath}")
    
    print("\nValidating session...")
    validate_session_file(filepath)
    print("Validation passed.")


def main() -> None:
    """Main entry point for session creation."""
    create_single_session()


if __name__ == "__main__":
    main()
