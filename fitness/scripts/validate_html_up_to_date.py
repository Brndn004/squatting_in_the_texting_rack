#!/usr/bin/env python3
"""Validate that embedded_data.js is up-to-date with current JSON files.

This script checks if embedded_data.js matches the current state of routines,
sessions, and exercises JSON files. Raises hard exception if data is out of sync.
"""

import json
import re
from pathlib import Path

import generate_embedded_data
import fitness_paths


def load_embedded_data_js() -> str:
    """Load embedded_data.js file content.
    
    Returns:
        File content as string.
        
    Raises:
        FileNotFoundError: If embedded_data.js file does not exist.
        OSError: If file cannot be read.
    """
    web_dir = fitness_paths.get_web_dir()
    embedded_data_path = web_dir / "embedded_data.js"
    
    if not embedded_data_path.exists():
        raise FileNotFoundError(f"embedded_data.js not found: {embedded_data_path}")
    
    with open(embedded_data_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_javascript_object(content: str, var_name: str) -> dict:
    """Extract JavaScript object from embedded_data.js content.
    
    Args:
        content: Complete embedded_data.js file content.
        var_name: Name of the JavaScript variable to extract (e.g., "ROUTINES").
        
    Returns:
        Dictionary parsed from JavaScript object.
        
    Raises:
        ValueError: If variable declaration not found or contains invalid JSON.
    """
    if not var_name:
        raise ValueError("Variable name cannot be empty")
    
    # Pattern to match: const VAR_NAME = {...};
    pattern = rf"const\s+{re.escape(var_name)}\s*=\s*(\{{.*?\}});"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError(f"Variable {var_name} not found in embedded_data.js")
    
    json_str = match.group(1)
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {var_name} variable: {e}")


def extract_all_objects(content: str) -> tuple[dict, dict, dict]:
    """Extract all three JavaScript objects from embedded_data.js.
    
    Args:
        content: Complete embedded_data.js file content.
        
    Returns:
        Tuple of (routines_dict, sessions_dict, exercises_dict).
        
    Raises:
        ValueError: If any variable declaration not found or contains invalid JSON.
    """
    routines = extract_javascript_object(content, "ROUTINES")
    sessions = extract_javascript_object(content, "SESSIONS")
    exercises = extract_javascript_object(content, "EXERCISES")
    
    return (routines, sessions, exercises)


def compare_dicts(dict1: dict, dict2: dict, name: str) -> None:
    """Compare two dictionaries and raise exception if they differ.
    
    Args:
        dict1: First dictionary to compare.
        dict2: Second dictionary to compare.
        name: Name of the data type (for error messages).
        
    Raises:
        ValueError: If dictionaries differ, with clear error message describing the difference.
    """
    if dict1 == dict2:
        return
    
    # Check for missing keys
    missing_in_dict2 = set(dict1.keys()) - set(dict2.keys())
    if missing_in_dict2:
        raise ValueError(f"{name} data is out of sync: Missing keys in embedded_data.js: {sorted(missing_in_dict2)}")
    
    missing_in_dict1 = set(dict2.keys()) - set(dict1.keys())
    if missing_in_dict1:
        raise ValueError(f"{name} data is out of sync: Extra keys in embedded_data.js: {sorted(missing_in_dict1)}")
    
    # Check for differing values
    for key in dict1.keys():
        if dict1[key] != dict2[key]:
            raise ValueError(f"{name} data is out of sync: Key '{key}' differs between JSON files and embedded_data.js")


def validate_embedded_data() -> None:
    """Validate that embedded_data.js matches current JSON files.
    
    Raises:
        FileNotFoundError: If embedded_data.js or any JSON directory doesn't exist.
        OSError: If any file cannot be read.
        json.JSONDecodeError: If any JSON file contains invalid JSON.
        ValueError: If embedded_data.js is out of sync with JSON files, with clear error message.
    """
    print("Validating embedded_data.js is up-to-date...")
    
    # Generate current data from JSON files
    current_routines = generate_embedded_data.load_all_routines()
    current_sessions = generate_embedded_data.load_all_sessions()
    current_exercises = generate_embedded_data.load_all_exercises()
    
    # Load embedded_data.js
    embedded_content = load_embedded_data_js()
    
    # Extract objects from embedded_data.js
    embedded_routines, embedded_sessions, embedded_exercises = extract_all_objects(embedded_content)
    
    # Compare each data type
    compare_dicts(current_routines, embedded_routines, "Routines")
    compare_dicts(current_sessions, embedded_sessions, "Sessions")
    compare_dicts(current_exercises, embedded_exercises, "Exercises")
    
    print("embedded_data.js is up-to-date")


def main() -> None:
    """Main function to validate embedded_data.js."""
    try:
        validate_embedded_data()
    except Exception as e:
        print(f"Validation failed: {e}")
        raise


if __name__ == "__main__":
    main()
