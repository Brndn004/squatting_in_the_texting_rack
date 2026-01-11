#!/usr/bin/env python3
"""Validate session files.

Validates that session JSON files conform to the session schema.
"""

from pathlib import Path

import fitness_paths


def get_all_session_files() -> list[Path]:
    """Get all session JSON files.
    
    Returns:
        List of paths to session JSON files.
        
    Raises:
        FileNotFoundError: If sessions directory does not exist.
    """
    sessions_dir = fitness_paths.get_sessions_dir()
    if not sessions_dir.exists():
        raise FileNotFoundError(f"Sessions directory not found: {sessions_dir}")
    return sorted(sessions_dir.glob("*.json"))


def validate_session(session_path: Path) -> None:
    """Validate a session file.
    
    Args:
        session_path: Path to session JSON file.
        
    Raises:
        ValueError: If session is invalid.
    """
    # TODO: Implement validation logic
    # - Validate JSON structure against session_schema.json
    # - Validate that percent_1rm is between 0 and 1 (inclusive) for all exercises
    print(f"Validation for session file {session_path} will be implemented later.")


def validate_all_sessions() -> None:
    """Validate all session files.
    
    Raises:
        FileNotFoundError: If sessions directory does not exist.
        ValueError: If no session files found or if any session is invalid.
    """
    session_files = get_all_session_files()
    if not session_files:
        raise ValueError("No session files found in sessions directory")
    
    for session_path in session_files:
        validate_session(session_path)


def main() -> None:
    """Main entry point for session validation."""
    validate_all_sessions()


if __name__ == "__main__":
    main()
