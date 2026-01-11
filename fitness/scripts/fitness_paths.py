#!/usr/bin/env python3
"""Path utilities for fitness tracking system.

This module provides path resolution functions for all fitness-related directories.
All paths are resolved relative to the fitness directory using Path(__file__).parent.parent.
"""

from pathlib import Path


def get_fitness_dir() -> Path:
    """Get the fitness directory path (base directory).
    
    Returns:
        Path to the fitness directory.
    """
    return Path(__file__).parent.parent


def get_snapshots_dir() -> Path:
    """Get the snapshots directory path.
    
    Returns:
        Path to the snapshots directory.
    """
    return get_fitness_dir() / "body_snapshots"


def get_exercises_dir() -> Path:
    """Get the exercises directory path.
    
    Returns:
        Path to the exercises directory.
    """
    return get_fitness_dir() / "exercises"


def get_sessions_dir() -> Path:
    """Get the sessions directory path.
    
    Returns:
        Path to the sessions directory.
    """
    return get_fitness_dir() / "sessions"


def get_routines_dir() -> Path:
    """Get the routines directory path.
    
    Returns:
        Path to the routines directory.
    """
    return get_fitness_dir() / "routines"


def get_schemas_dir() -> Path:
    """Get the schemas directory path.
    
    Returns:
        Path to the schemas directory.
    """
    return get_fitness_dir() / "schemas"


def get_scripts_dir() -> Path:
    """Get the scripts directory path.
    
    Returns:
        Path to the scripts directory.
    """
    return get_fitness_dir() / "scripts"
