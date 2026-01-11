#!/usr/bin/env python3
"""Schema loader for fitness tracking system.

This module provides functions to load JSON schema files for validation.
Note: Validation logic belongs in validation scripts, not in this module.
"""

from pathlib import Path

import file_utils
import fitness_paths


def load_schema(schema_name: str) -> dict:
    """Load a schema file by name.
    
    Args:
        schema_name: Name of the schema file (e.g., "body_snapshot_schema.json").
        
    Returns:
        Dictionary containing the schema.
        
    Raises:
        FileNotFoundError: If schema file does not exist.
        ValueError: If schema file does not contain a dictionary or schema_name is invalid.
        json.JSONDecodeError: If schema file contains invalid JSON.
        OSError: If schema file cannot be read.
    """
    if not schema_name:
        raise ValueError("Schema name cannot be empty")
    
    if not schema_name.endswith(".json"):
        raise ValueError(f"Schema name must end with '.json': {schema_name}")
    
    schemas_dir = fitness_paths.get_schemas_dir()
    schema_path = schemas_dir / schema_name
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    return file_utils.load_json_file(schema_path)


def load_snapshot_schema() -> dict:
    """Load snapshot schema.
    
    Returns:
        Dictionary containing the snapshot schema.
        
    Raises:
        FileNotFoundError: If snapshot schema file does not exist.
        ValueError: If snapshot schema file does not contain a dictionary.
        json.JSONDecodeError: If snapshot schema file contains invalid JSON.
        OSError: If snapshot schema file cannot be read.
    """
    return load_schema("body_snapshot_schema.json")


def load_exercise_schema() -> dict:
    """Load exercise schema.
    
    Returns:
        Dictionary containing the exercise schema.
        
    Raises:
        FileNotFoundError: If exercise schema file does not exist.
        ValueError: If exercise schema file does not contain a dictionary.
        json.JSONDecodeError: If exercise schema file contains invalid JSON.
        OSError: If exercise schema file cannot be read.
    """
    return load_schema("exercise_schema.json")


def load_session_schema() -> dict:
    """Load session schema.
    
    Returns:
        Dictionary containing the session schema.
        
    Raises:
        FileNotFoundError: If session schema file does not exist.
        ValueError: If session schema file does not contain a dictionary.
        json.JSONDecodeError: If session schema file contains invalid JSON.
        OSError: If session schema file cannot be read.
    """
    return load_schema("session_schema.json")


def load_routine_schema() -> dict:
    """Load routine schema.
    
    Returns:
        Dictionary containing the routine schema.
        
    Raises:
        FileNotFoundError: If routine schema file does not exist.
        ValueError: If routine schema file does not contain a dictionary.
        json.JSONDecodeError: If routine schema file contains invalid JSON.
        OSError: If routine schema file cannot be read.
    """
    return load_schema("routine_schema.json")


def load_all_schemas() -> dict[str, dict]:
    """Load all schemas.
    
    Returns:
        Dictionary with keys "snapshot", "exercise", "session", "routine" mapping to their respective schema dictionaries.
        
    Raises:
        FileNotFoundError: If any schema file does not exist.
        ValueError: If any schema file does not contain a dictionary.
        json.JSONDecodeError: If any schema file contains invalid JSON.
        OSError: If any schema file cannot be read.
    """
    return {
        "snapshot": load_snapshot_schema(),
        "exercise": load_exercise_schema(),
        "session": load_session_schema(),
        "routine": load_routine_schema(),
    }
