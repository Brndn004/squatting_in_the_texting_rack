#!/usr/bin/env python3
"""Create routine files.

Creates a new fitness routine file with workout sessions for a week.
"""

import json
import re
from datetime import datetime
from pathlib import Path

import fitness_paths
import validate_routine


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


def get_current_datetime() -> str:
    """Get current datetime in format YYYY-MM-DD-<unix epoch seconds>.
    
    Returns:
        Current datetime as a string.
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    unix_seconds = int(now.timestamp())
    return f"{date_str}-{unix_seconds}"


def get_available_sessions() -> list[tuple[str, str]]:
    """Get list of available sessions from session files.
    
    Returns:
        List of tuples (human-readable name, session_name slug) sorted by human-readable name.
        
    Raises:
        FileNotFoundError: If sessions directory does not exist.
        ValueError: If no session files found or if session files are invalid.
    """
    sessions_dir = fitness_paths.get_sessions_dir()
    if not sessions_dir.exists():
        raise FileNotFoundError(f"Sessions directory not found: {sessions_dir}")
    
    session_files = sorted(sessions_dir.glob("*.json"))
    if not session_files:
        raise ValueError("No session files found in sessions directory")
    
    sessions = []
    for session_file in session_files:
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            
            if not isinstance(session_data, dict):
                raise ValueError(f"Session file is not a valid JSON object: {session_file}")
            
            if "name" not in session_data:
                raise ValueError(f"Session file missing 'name' field: {session_file}")
            
            if "session_name" not in session_data:
                raise ValueError(f"Session file missing 'session_name' field: {session_file}")
            
            name = session_data["name"]
            session_name = session_data["session_name"]
            
            if not isinstance(name, str):
                raise ValueError(f"Session name must be a string in {session_file}")
            
            if not isinstance(session_name, str):
                raise ValueError(f"Session name slug must be a string in {session_file}")
            
            if not name:
                raise ValueError(f"Session name cannot be empty in {session_file}")
            
            if not session_name:
                raise ValueError(f"Session name slug cannot be empty in {session_file}")
            
            sessions.append((name, session_name))
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse session file {session_file}: {e}")
    
    if not sessions:
        raise ValueError("No valid sessions found")
    
    # Sort by human-readable name
    return sorted(sessions, key=lambda x: x[0])


def prompt_routine_name() -> str:
    """Prompt user for human-readable routine name.
    
    Returns:
        Human-readable routine name as a string.
    """
    print("Routine name:")
    while True:
        name_input = input("  Name: ").strip()
        
        if not name_input:
            print("  Error: Routine name cannot be empty.")
            continue
        
        try:
            slugify(name_input)
        except ValueError as e:
            print(f"  Error: {e}")
            continue
        
        return name_input


def prompt_num_sessions() -> int:
    """Prompt user for number of workout sessions per week.
    
    Returns:
        Number of sessions as an integer.
    """
    print("Number of workout sessions per week:")
    while True:
        value_input = input("  Sessions: ").strip()
        
        if not value_input:
            print("  Error: Value cannot be empty.")
            continue
        
        try:
            value = int(value_input)
        except ValueError:
            print(f"  Error: Invalid number: {value_input}")
            continue
        
        if value <= 0:
            print("  Error: Number of sessions must be positive.")
            continue
        
        return value


def prompt_session_selections(available_sessions: list[tuple[str, str]], num_sessions: int) -> list[str]:
    """Prompt user to select sessions using space-delimited numbers.
    
    Args:
        available_sessions: List of tuples (human-readable name, session_name slug).
        num_sessions: Number of sessions to select.
        
    Returns:
        List of selected session_name slugs.
    """
    print("Available sessions:")
    for i, (name, session_name) in enumerate(available_sessions, 1):
        print(f"  {i}. {name}")
    print()
    
    while True:
        selection_input = input(f"  Select {num_sessions} session(s) (space-delimited numbers, e.g., '2 1 3'): ").strip()
        
        if not selection_input:
            print("  Error: Selection cannot be empty.")
            continue
        
        # Split by spaces
        selection_parts = selection_input.split()
        
        if len(selection_parts) != num_sessions:
            print(f"  Error: Expected {num_sessions} session(s), but got {len(selection_parts)}.")
            continue
        
        session_names = []
        for part in selection_parts:
            try:
                selection_num = int(part)
            except ValueError:
                print(f"  Error: Invalid number: {part}")
                session_names = None
                break
            
            if not (1 <= selection_num <= len(available_sessions)):
                print(f"  Error: Invalid selection number {selection_num}. Must be between 1 and {len(available_sessions)}.")
                session_names = None
                break
            
            session_names.append(available_sessions[selection_num - 1][1])  # Return session_name slug
        
        if session_names is not None:
            return session_names


def create_routine_data(routine_name: str, datetime_str: str, session_names: list[str]) -> dict:
    """Create routine data dictionary.
    
    Args:
        routine_name: Name of the routine.
        datetime_str: Datetime in format YYYY-MM-DD-<unix epoch seconds>.
        session_names: List of session_name slugs (references to session files).
        
    Returns:
        Routine data dictionary.
    """
    return {
        "name": routine_name,
        "date_created": datetime_str,
        "sessions": session_names,
    }


def save_routine_file(routine_data: dict, filepath: Path) -> None:
    """Save routine data to JSON file.
    
    Args:
        routine_data: Routine data dictionary.
        filepath: Path where file should be saved.
        
    Raises:
        OSError: If file cannot be written.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(routine_data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_routine_filepath(routine_name: str, datetime_str: str) -> Path:
    """Get routine filepath.
    
    Args:
        routine_name: Human-readable name of the routine (will be slugified).
        datetime_str: Datetime in format YYYY-MM-DD-<unix epoch seconds> (unused, kept for API consistency).
        
    Returns:
        Path to routine file.
    """
    routines_dir = fitness_paths.get_routines_dir()
    routine_slug = slugify(routine_name)
    filename = f"{routine_slug}.json"
    return routines_dir / filename


def validate_routine_file(filepath: Path) -> None:
    """Run validation on routine file.
    
    Args:
        filepath: Path to routine file to validate.
        
    Raises:
        ValueError: If validation fails.
    """
    validate_routine.validate_routine(filepath)


def create_routine() -> None:
    """Create a new routine file by prompting user for input.
    
    Raises:
        ValueError: If invalid input provided or validation fails.
        FileNotFoundError: If sessions directory does not exist.
        OSError: If file cannot be written.
    """
    datetime_str = get_current_datetime()
    
    # Validate datetime format
    parts = datetime_str.split("-")
    if len(parts) < 4:
        raise ValueError(f"Invalid datetime format: {datetime_str}. Expected YYYY-MM-DD-<unix epoch seconds>")
    
    while True:
        routine_name = prompt_routine_name()
        routine_slug = slugify(routine_name)
        filepath = get_routine_filepath(routine_name, datetime_str)
        
        if filepath.exists():
            print(f"  Error: Routine file already exists: {filepath.name}")
            print()
            continue
        
        break
    
    print()
    
    available_sessions = get_available_sessions()
    
    num_sessions = prompt_num_sessions()
    print()
    
    session_names = prompt_session_selections(available_sessions, num_sessions)
    print()
    
    filepath = get_routine_filepath(routine_name, datetime_str)
    routine_data = create_routine_data(routine_name, datetime_str, session_names)
    save_routine_file(routine_data, filepath)
    
    print(f"\nRoutine saved to: {filepath}")
    
    print("\nValidating routine...")
    validate_routine_file(filepath)
    print("Validation passed.")


def main() -> None:
    """Main entry point for routine creation."""
    create_routine()


if __name__ == "__main__":
    main()
