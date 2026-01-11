#!/usr/bin/env python3
"""Validate snapshot files.

Validates that snapshot JSON files conform to the snapshot schema.
"""

from pathlib import Path

import fitness_paths


def get_all_snapshot_files() -> list[Path]:
    """Get all snapshot JSON files.
    
    Returns:
        List of paths to snapshot JSON files.
        
    Raises:
        FileNotFoundError: If snapshots directory does not exist.
    """
    snapshots_dir = fitness_paths.get_snapshots_dir()
    if not snapshots_dir.exists():
        raise FileNotFoundError(f"Snapshots directory not found: {snapshots_dir}")
    return sorted(snapshots_dir.glob("*.json"))


def validate_snapshot(snapshot_path: Path) -> None:
    """Validate a snapshot file.
    
    Args:
        snapshot_path: Path to snapshot JSON file.
        
    Raises:
        ValueError: If snapshot is invalid.
    """
    # TODO: Implement validation logic
    # - Validate JSON structure against snapshot_schema.json
    # - Validate that bodyfat_percentage is between 0 and 1 (inclusive)
    print(f"Validation for snapshot file {snapshot_path} will be implemented later.")


def validate_all_snapshots() -> None:
    """Validate all snapshot files.
    
    Raises:
        FileNotFoundError: If snapshots directory does not exist.
        ValueError: If no snapshot files found or if any snapshot is invalid.
    """
    snapshot_files = get_all_snapshot_files()
    if not snapshot_files:
        raise ValueError("No snapshot files found in snapshots directory")
    
    for snapshot_path in snapshot_files:
        validate_snapshot(snapshot_path)


def main() -> None:
    """Main entry point for snapshot validation."""
    validate_all_snapshots()


if __name__ == "__main__":
    main()

