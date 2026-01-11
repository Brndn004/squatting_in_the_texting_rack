#!/usr/bin/env python3
"""File I/O utilities for fitness tracking system.

This module provides file I/O utility functions for reading and writing JSON files
and ensuring directories exist.
"""

import json
from pathlib import Path


def save_json_file(data: dict, filepath: Path) -> None:
    """Save dict to JSON file with proper formatting.
    
    Args:
        data: Dictionary to save as JSON.
        filepath: Path where file should be saved.
        
    Raises:
        OSError: If file cannot be written or directory cannot be created.
        TypeError: If data cannot be serialized to JSON.
    """
    ensure_directory_exists(filepath.parent)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_json_file(filepath: Path) -> dict:
    """Load JSON file, handles errors.
    
    Args:
        filepath: Path to JSON file to load.
        
    Returns:
        Dictionary loaded from JSON file.
        
    Raises:
        FileNotFoundError: If file does not exist.
        json.JSONDecodeError: If file contains invalid JSON.
        OSError: If file cannot be read.
        ValueError: If JSON does not represent a dictionary.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"JSON file not found: {filepath}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not isinstance(data, dict):
        raise ValueError(f"JSON file does not contain a dictionary: {filepath}")
    
    return data


def ensure_directory_exists(dirpath: Path) -> None:
    """Create directory if it doesn't exist.
    
    Args:
        dirpath: Path to directory that should exist.
        
    Raises:
        OSError: If directory cannot be created.
    """
    dirpath.mkdir(parents=True, exist_ok=True)
