#!/usr/bin/env python3
"""Validate workout log files.

Validates that workout log JSON files conform to the workout log schema.
"""

from pathlib import Path

import date_utils
import file_utils
import fitness_paths
import schema_loader
import jsonschema


def get_all_workout_log_files() -> list[Path]:
    """Get all workout log JSON files.
    
    Returns:
        List of paths to workout log JSON files.
        
    Raises:
        FileNotFoundError: If workout_logs directory does not exist.
    """
    workout_logs_dir = fitness_paths.get_workout_logs_dir()
    if not workout_logs_dir.exists():
        raise FileNotFoundError(f"Workout logs directory not found: {workout_logs_dir}")
    return sorted(workout_logs_dir.glob("*.json"))


def validate_datetime_format(datetime_str: str, workout_log_path: Path) -> None:
    """Validate datetime format.
    
    Args:
        datetime_str: Datetime string to validate.
        workout_log_path: Path to workout log file (for error messages).
        
    Raises:
        ValueError: If datetime format is invalid.
    """
    try:
        date_utils.parse_datetime(datetime_str)
    except ValueError as e:
        raise ValueError(
            f"Invalid datetime format in {workout_log_path}: {datetime_str}. {e}"
        )


def validate_session_reference(session_name: str, workout_log_path: Path) -> None:
    """Validate that session_name references an existing session file.
    
    Args:
        session_name: Name of the session to validate.
        workout_log_path: Path to workout log file (for error messages).
        
    Raises:
        ValueError: If session reference is invalid.
    """
    if not session_name:
        raise ValueError(f"session_name cannot be empty in {workout_log_path}")
    
    sessions_dir = fitness_paths.get_sessions_dir()
    session_file = sessions_dir / f"{session_name}.json"
    
    if not session_file.exists():
        raise ValueError(
            f"session_name '{session_name}' in {workout_log_path} does not reference an existing session file: {session_file}"
        )


def validate_exercise_reference(exercise_name: str, workout_log_path: Path) -> None:
    """Validate that exercise_name references an existing exercise file.
    
    Args:
        exercise_name: Name of the exercise to validate.
        workout_log_path: Path to workout log file (for error messages).
        
    Raises:
        ValueError: If exercise reference is invalid.
    """
    if not exercise_name:
        raise ValueError(f"exercise_name cannot be empty in {workout_log_path}")
    
    exercises_dir = fitness_paths.get_exercises_dir()
    exercise_file = exercises_dir / f"{exercise_name}.json"
    
    if not exercise_file.exists():
        raise ValueError(
            f"exercise_name '{exercise_name}' in {workout_log_path} does not reference an existing exercise file: {exercise_file}"
        )


def validate_numeric_ranges(workout_data: dict, workout_log_path: Path) -> None:
    """Validate numeric ranges for bodyweight and sets.
    
    Args:
        workout_data: Workout log data dictionary.
        workout_log_path: Path to workout log file (for error messages).
        
    Raises:
        ValueError: If numeric ranges are invalid.
    """
    # Validate bodyweight_lb > 0
    if "bodyweight_lb" not in workout_data:
        raise ValueError(f"bodyweight_lb is required in {workout_log_path}")
    
    bodyweight_lb = workout_data["bodyweight_lb"]
    if not isinstance(bodyweight_lb, (int, float)):
        raise ValueError(
            f"bodyweight_lb must be a number in {workout_log_path}, got {type(bodyweight_lb).__name__}"
        )
    
    if bodyweight_lb <= 0:
        raise ValueError(
            f"bodyweight_lb must be greater than 0 in {workout_log_path}, got {bodyweight_lb}"
        )
    
    # Validate exercises and sets
    if "exercises" not in workout_data:
        raise ValueError(f"exercises is required in {workout_log_path}")
    
    if not isinstance(workout_data["exercises"], list):
        raise ValueError(
            f"exercises must be a list in {workout_log_path}, got {type(workout_data['exercises']).__name__}"
        )
    
    for exercise_idx, exercise in enumerate(workout_data["exercises"]):
        if not isinstance(exercise, dict):
            raise ValueError(
                f"exercise at index {exercise_idx} must be a dictionary in {workout_log_path}"
            )
        
        if "sets" not in exercise:
            raise ValueError(
                f"sets is required for exercise at index {exercise_idx} in {workout_log_path}"
            )
        
        if not isinstance(exercise["sets"], list):
            raise ValueError(
                f"sets must be a list for exercise at index {exercise_idx} in {workout_log_path}, got {type(exercise['sets']).__name__}"
            )
        
        for set_idx, set_data in enumerate(exercise["sets"]):
            if not isinstance(set_data, dict):
                raise ValueError(
                    f"set at index {set_idx} for exercise at index {exercise_idx} must be a dictionary in {workout_log_path}"
                )
            
            if "reps" not in set_data:
                raise ValueError(
                    f"reps is required for set at index {set_idx} of exercise at index {exercise_idx} in {workout_log_path}"
                )
            
            if "lb" not in set_data:
                raise ValueError(
                    f"lb is required for set at index {set_idx} of exercise at index {exercise_idx} in {workout_log_path}"
                )
            
            reps = set_data["reps"]
            if not isinstance(reps, int):
                raise ValueError(
                    f"reps must be an integer for set at index {set_idx} of exercise at index {exercise_idx} in {workout_log_path}, got {type(reps).__name__}"
                )
            
            if reps < 0:
                raise ValueError(
                    f"reps must be >= 0 for set at index {set_idx} of exercise at index {exercise_idx} in {workout_log_path}, got {reps}"
                )
            
            lb = set_data["lb"]
            if not isinstance(lb, (int, float)):
                raise ValueError(
                    f"lb must be a number for set at index {set_idx} of exercise at index {exercise_idx} in {workout_log_path}, got {type(lb).__name__}"
                )
            
            if lb < 0:
                raise ValueError(
                    f"lb must be >= 0 for set at index {set_idx} of exercise at index {exercise_idx} in {workout_log_path}, got {lb}"
                )


def validate_workout_log(workout_log_path: Path) -> None:
    """Validate a workout log file.
    
    Args:
        workout_log_path: Path to workout log JSON file.
        
    Raises:
        ValueError: If workout log is invalid.
        FileNotFoundError: If workout log file does not exist.
        json.JSONDecodeError: If workout log file contains invalid JSON.
    """
    # Load workout log data
    workout_data = file_utils.load_json_file(workout_log_path)
    
    # Load schema
    schema = schema_loader.load_workout_log_schema()
    
    # Validate against JSON schema
    try:
        jsonschema.validate(instance=workout_data, schema=schema)
    except jsonschema.ValidationError as e:
        raise ValueError(
            f"Schema validation failed for {workout_log_path}: {str(e)}"
        )
    except jsonschema.SchemaError as e:
        raise ValueError(f"Schema error: {str(e)}")
    
    # Validate datetime format
    if "date" not in workout_data:
        raise ValueError(f"date is required in {workout_log_path}")
    
    validate_datetime_format(workout_data["date"], workout_log_path)
    
    # Validate session reference
    if "session_name" not in workout_data:
        raise ValueError(f"session_name is required in {workout_log_path}")
    
    validate_session_reference(workout_data["session_name"], workout_log_path)
    
    # Validate exercise references
    if "exercises" not in workout_data:
        raise ValueError(f"exercises is required in {workout_log_path}")
    
    if not isinstance(workout_data["exercises"], list):
        raise ValueError(
            f"exercises must be a list in {workout_log_path}, got {type(workout_data['exercises']).__name__}"
        )
    
    for exercise_idx, exercise in enumerate(workout_data["exercises"]):
        if not isinstance(exercise, dict):
            raise ValueError(
                f"exercise at index {exercise_idx} must be a dictionary in {workout_log_path}"
            )
        
        if "exercise_name" not in exercise:
            raise ValueError(
                f"exercise_name is required for exercise at index {exercise_idx} in {workout_log_path}"
            )
        
        validate_exercise_reference(exercise["exercise_name"], workout_log_path)
    
    # Validate numeric ranges
    validate_numeric_ranges(workout_data, workout_log_path)
    
    print(f"✓ Validated {workout_log_path}")


def validate_all_workout_logs() -> None:
    """Validate all workout log files.
    
    Raises:
        FileNotFoundError: If workout_logs directory does not exist.
        ValueError: If no workout log files found or if any workout log is invalid.
    """
    workout_log_files = get_all_workout_log_files()
    if not workout_log_files:
        raise ValueError("No workout log files found in workout_logs directory")
    
    for workout_log_path in workout_log_files:
        validate_workout_log(workout_log_path)


def main() -> None:
    """Main entry point for workout log validation."""
    validate_all_workout_logs()


if __name__ == "__main__":
    main()
