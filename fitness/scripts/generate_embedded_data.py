#!/usr/bin/env python3
"""Generate embedded_data.js from routines, sessions, and exercises JSON files.

This script reads all JSON files from the routines, sessions, and exercises
directories and generates a JavaScript file with embedded data objects.
"""

import json
from pathlib import Path

import file_utils
import fitness_paths


def get_routine_files() -> list[Path]:
    """Get all routine JSON files.
    
    Returns:
        List of paths to routine JSON files, sorted by filename.
        
    Raises:
        OSError: If routines directory cannot be accessed.
    """
    routines_dir = fitness_paths.get_routines_dir()
    if not routines_dir.exists():
        raise FileNotFoundError(f"Routines directory not found: {routines_dir}")
    
    routine_files = sorted(routines_dir.glob("*.json"))
    return routine_files


def get_session_files() -> list[Path]:
    """Get all session JSON files.
    
    Returns:
        List of paths to session JSON files, sorted by filename.
        
    Raises:
        OSError: If sessions directory cannot be accessed.
    """
    sessions_dir = fitness_paths.get_sessions_dir()
    if not sessions_dir.exists():
        raise FileNotFoundError(f"Sessions directory not found: {sessions_dir}")
    
    session_files = sorted(sessions_dir.glob("*.json"))
    return session_files


def get_exercise_files() -> list[Path]:
    """Get all exercise JSON files.
    
    Returns:
        List of paths to exercise JSON files, sorted by filename.
        
    Raises:
        OSError: If exercises directory cannot be accessed.
    """
    exercises_dir = fitness_paths.get_exercises_dir()
    if not exercises_dir.exists():
        raise FileNotFoundError(f"Exercises directory not found: {exercises_dir}")
    
    exercise_files = sorted(exercises_dir.glob("*.json"))
    return exercise_files


def extract_routine_name(filepath: Path) -> str:
    """Extract routine name from filepath (filename without .json extension).
    
    Args:
        filepath: Path to routine JSON file.
        
    Returns:
        Routine name (filename without .json extension).
        
    Raises:
        ValueError: If filename doesn't end with .json or is empty.
    """
    if not filepath.name.endswith(".json"):
        raise ValueError(f"Routine file must end with .json: {filepath}")
    
    routine_name = filepath.stem
    if not routine_name:
        raise ValueError(f"Routine filename is empty: {filepath}")
    
    return routine_name


def extract_session_name(filepath: Path) -> str:
    """Extract session name from filepath (filename without .json extension).
    
    Args:
        filepath: Path to session JSON file.
        
    Returns:
        Session name (filename without .json extension).
        
    Raises:
        ValueError: If filename doesn't end with .json or is empty.
    """
    if not filepath.name.endswith(".json"):
        raise ValueError(f"Session file must end with .json: {filepath}")
    
    session_name = filepath.stem
    if not session_name:
        raise ValueError(f"Session filename is empty: {filepath}")
    
    return session_name


def extract_exercise_name(filepath: Path) -> str:
    """Extract exercise name from filepath (filename without .json extension).
    
    Args:
        filepath: Path to exercise JSON file.
        
    Returns:
        Exercise name (filename without .json extension).
        
    Raises:
        ValueError: If filename doesn't end with .json or is empty.
    """
    if not filepath.name.endswith(".json"):
        raise ValueError(f"Exercise file must end with .json: {filepath}")
    
    exercise_name = filepath.stem
    if not exercise_name:
        raise ValueError(f"Exercise filename is empty: {filepath}")
    
    return exercise_name


def load_all_routines() -> dict:
    """Load all routines from JSON files.
    
    Returns:
        Dictionary mapping routine names to routine data.
        
    Raises:
        FileNotFoundError: If routines directory doesn't exist.
        OSError: If any routine file cannot be read.
        json.JSONDecodeError: If any routine file contains invalid JSON.
        ValueError: If any routine file doesn't contain a dictionary or has invalid filename.
    """
    routines = {}
    routine_files = get_routine_files()
    
    for routine_file in routine_files:
        routine_name = extract_routine_name(routine_file)
        routine_data = file_utils.load_json_file(routine_file)
        routines[routine_name] = routine_data
    
    return routines


def load_all_sessions() -> dict:
    """Load all sessions from JSON files.
    
    Returns:
        Dictionary mapping session names to session data.
        
    Raises:
        FileNotFoundError: If sessions directory doesn't exist.
        OSError: If any session file cannot be read.
        json.JSONDecodeError: If any session file contains invalid JSON.
        ValueError: If any session file doesn't contain a dictionary or has invalid filename.
    """
    sessions = {}
    session_files = get_session_files()
    
    for session_file in session_files:
        session_name = extract_session_name(session_file)
        session_data = file_utils.load_json_file(session_file)
        sessions[session_name] = session_data
    
    return sessions


def load_all_exercises() -> dict:
    """Load all exercises from JSON files.
    
    Returns:
        Dictionary mapping exercise names to exercise data.
        
    Raises:
        FileNotFoundError: If exercises directory doesn't exist.
        OSError: If any exercise file cannot be read.
        json.JSONDecodeError: If any exercise file contains invalid JSON.
        ValueError: If any exercise file doesn't contain a dictionary or has invalid filename.
    """
    exercises = {}
    exercise_files = get_exercise_files()
    
    for exercise_file in exercise_files:
        exercise_name = extract_exercise_name(exercise_file)
        exercise_data = file_utils.load_json_file(exercise_file)
        exercises[exercise_name] = exercise_data
    
    return exercises


def generate_javascript_object(var_name: str, data: dict) -> str:
    """Generate JavaScript object declaration from Python dictionary.
    
    Args:
        var_name: Name of the JavaScript variable (e.g., "ROUTINES").
        data: Python dictionary to convert to JavaScript object.
        
    Returns:
        JavaScript code string declaring the variable with the data.
        
    Raises:
        ValueError: If var_name is empty.
    """
    if not var_name:
        raise ValueError("Variable name cannot be empty")
    
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    return f"const {var_name} = {json_str};"


def generate_embedded_data_js() -> str:
    """Generate complete embedded_data.js file content.
    
    Returns:
        Complete JavaScript file content as string.
        
    Raises:
        FileNotFoundError: If any required directory doesn't exist.
        OSError: If any JSON file cannot be read.
        json.JSONDecodeError: If any JSON file contains invalid JSON.
        ValueError: If any JSON file doesn't contain a dictionary or has invalid filename.
    """
    routines = load_all_routines()
    sessions = load_all_sessions()
    exercises = load_all_exercises()
    
    routines_js = generate_javascript_object("ROUTINES", routines)
    sessions_js = generate_javascript_object("SESSIONS", sessions)
    exercises_js = generate_javascript_object("EXERCISES", exercises)
    
    return f"{routines_js}\n\n{sessions_js}\n\n{exercises_js}\n"


def write_embedded_data_js(content: str) -> None:
    """Write embedded_data.js file to web directory.
    
    Args:
        content: JavaScript file content to write.
        
    Raises:
        OSError: If file cannot be written or directory cannot be created.
    """
    web_dir = fitness_paths.get_web_dir()
    file_utils.ensure_directory_exists(web_dir)
    
    output_path = web_dir / "embedded_data.js"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> None:
    """Main function to generate embedded_data.js."""
    print("Generating embedded_data.js...")
    
    try:
        content = generate_embedded_data_js()
        write_embedded_data_js(content)
        
        routines_count = len(get_routine_files())
        sessions_count = len(get_session_files())
        exercises_count = len(get_exercise_files())
        
        print(f"Successfully generated embedded_data.js")
        print(f"  Routines: {routines_count}")
        print(f"  Sessions: {sessions_count}")
        print(f"  Exercises: {exercises_count}")
        
    except Exception as e:
        print(f"Error generating embedded_data.js: {e}")
        raise


if __name__ == "__main__":
    main()
