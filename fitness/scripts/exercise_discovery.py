#!/usr/bin/env python3
"""Exercise discovery module for fitness tracking system.

This module provides functions to discover and parse exercise files.
"""

from pathlib import Path

import file_utils
import fitness_paths


def discover_exercise_files() -> list[Path]:
    """Scan exercises directory, returns list of exercise file paths.
    
    Returns:
        List of paths to exercise JSON files, sorted by filename.
        
    Raises:
        FileNotFoundError: If exercises directory does not exist.
        ValueError: If no exercise files found.
    """
    exercises_dir = fitness_paths.get_exercises_dir()
    if not exercises_dir.exists():
        raise FileNotFoundError(f"Exercises directory not found: {exercises_dir}")
    
    exercise_files = sorted(exercises_dir.glob("*.json"))
    if not exercise_files:
        raise ValueError("No exercise files found in exercises directory")
    
    return exercise_files


def extract_exercise_name_from_file(filepath: Path) -> str:
    """Extract exercise name from exercise JSON file.
    
    Args:
        filepath: Path to exercise JSON file.
        
    Returns:
        Slugified exercise_name from the file.
        
    Raises:
        FileNotFoundError: If exercise file does not exist.
        ValueError: If exercise file is malformed or missing required fields.
        json.JSONDecodeError: If exercise file contains invalid JSON.
        OSError: If exercise file cannot be read.
    """
    exercise_data = file_utils.load_json_file(filepath)
    
    if "exercise_name" not in exercise_data:
        raise ValueError(f"Exercise file missing 'exercise_name' field: {filepath}")
    
    exercise_name = exercise_data["exercise_name"]
    
    if not isinstance(exercise_name, str):
        raise ValueError(f"Exercise name slug must be a string in {filepath}")
    
    if not exercise_name:
        raise ValueError(f"Exercise name slug cannot be empty in {filepath}")
    
    return exercise_name


def get_available_exercises() -> list[tuple[str, str]]:
    """Get list of available exercises from exercise files.
    
    Returns:
        List of tuples (human-readable name, slugified exercise_name) sorted by human-readable name.
        
    Raises:
        FileNotFoundError: If exercises directory does not exist.
        ValueError: If no exercise files found or if exercise files are invalid.
    """
    exercise_files = discover_exercise_files()
    
    exercises = []
    for exercise_file in exercise_files:
        try:
            exercise_data = file_utils.load_json_file(exercise_file)
            
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
        except (FileNotFoundError, ValueError) as e:
            raise ValueError(f"Failed to load exercise file {exercise_file}: {e}")
    
    if not exercises:
        raise ValueError("No valid exercises found")
    
    # Sort by human-readable name
    return sorted(exercises, key=lambda x: x[0])


def find_exercise_file(exercise_name: str) -> Path:
    """Find exercise file by slugified name.
    
    Args:
        exercise_name: Slugified exercise name (e.g., "barbell_squat").
        
    Returns:
        Path to exercise file.
        
    Raises:
        FileNotFoundError: If exercise file does not exist.
        ValueError: If exercise_name is empty or invalid.
    """
    if not exercise_name:
        raise ValueError("Exercise name cannot be empty")
    
    if not isinstance(exercise_name, str):
        raise ValueError(f"Exercise name must be a string, got {type(exercise_name)}")
    
    exercises_dir = fitness_paths.get_exercises_dir()
    if not exercises_dir.exists():
        raise FileNotFoundError(f"Exercises directory not found: {exercises_dir}")
    
    exercise_file = exercises_dir / f"{exercise_name}.json"
    
    if not exercise_file.exists():
        raise FileNotFoundError(f"Exercise file not found: {exercise_file}")
    
    return exercise_file
