#!/usr/bin/env python3
"""Create snapshot files.

Creates a new fitness snapshot file with body metrics.
"""

from pathlib import Path

import date_utils
import file_utils
import fitness_paths
import validate_snapshot


def prompt_bodyweight() -> dict:
    """Prompt user for bodyweight.
    
    Returns:
        Dictionary with unit and value (e.g., {"lb": 180}).
    """
    print("Bodyweight:")
    while True:
        value_input = input("  Value (lb): ").strip()
        
        if not value_input:
            print("  Error: Value cannot be empty.")
            continue
        
        try:
            value = float(value_input)
        except ValueError:
            print(f"  Error: Invalid number: {value_input}")
            continue
        
        if value <= 0:
            print("  Error: Bodyweight must be positive.")
            continue
        
        return {"lb": value}


def prompt_bodyfat_percentage() -> float:
    """Prompt user for bodyfat percentage.
    
    Returns:
        Bodyfat percentage as a decimal (0-1).
    """
    print("Bodyfat percentage:")
    while True:
        value_input = input("  Value (0-100): ").strip()
        
        if not value_input:
            print("  Error: Value cannot be empty.")
            continue
        
        try:
            value = float(value_input)
        except ValueError:
            print(f"  Error: Invalid number: {value_input}")
            continue
        
        if value < 0 or value > 100:
            print("  Error: Bodyfat percentage must be between 0 and 100.")
            continue
        
        # Convert to decimal (0-1)
        return value / 100


def prompt_height() -> dict:
    """Prompt user for height in feet and inches (space-delimited).
    
    Returns:
        Dictionary with unit and value (e.g., {"in": 72}).
    """
    print("Height:")
    while True:
        value_input = input("  Feet and inches (e.g., '5 9' for 5 ft 9 in): ").strip()
        
        if not value_input:
            print("  Error: Value cannot be empty.")
            continue
        
        parts = value_input.split()
        if len(parts) != 2:
            print("  Error: Height must be two space-delimited numbers (feet inches).")
            continue
        
        feet_input = parts[0]
        inches_input = parts[1]
        
        try:
            feet = int(feet_input)
        except ValueError:
            print(f"  Error: Invalid number for feet: {feet_input}")
            continue
        
        if feet < 0:
            print("  Error: Feet must be non-negative.")
            continue
        
        try:
            inches = int(inches_input)
        except ValueError:
            print(f"  Error: Invalid number for inches: {inches_input}")
            continue
        
        if inches < 0 or inches >= 12:
            print("  Error: Inches must be between 0 and 11.")
            continue
        
        total_inches = (feet * 12) + inches
        
        if total_inches <= 0:
            print("  Error: Total height must be positive.")
            continue
        
        return {"in": total_inches}


def create_snapshot_data(datetime_str: str, bodyweight: dict, bodyfat_percentage: float, height: dict) -> dict:
    """Create snapshot data dictionary.
    
    Args:
        datetime_str: Datetime in format YYYY-MM-DD-<unix epoch seconds>.
        bodyweight: Dictionary with unit and value.
        bodyfat_percentage: Bodyfat percentage as decimal (0-1).
        height: Dictionary with unit and value.
        
    Returns:
        Snapshot data dictionary.
    """
    return {
        "date": datetime_str,
        "body_metrics": {
            "bodyweight": bodyweight,
            "bodyfat_percentage": bodyfat_percentage,
            "height": height,
        },
    }




def get_snapshot_filepath(datetime_str: str) -> Path:
    """Get snapshot filepath for given datetime.
    
    Args:
        datetime_str: Datetime in format YYYY-MM-DD-<unix epoch seconds>.
        
    Returns:
        Path to snapshot file.
    """
    snapshots_dir = fitness_paths.get_snapshots_dir()
    filename = f"{datetime_str}_snapshot.json"
    return snapshots_dir / filename


def validate_snapshot_file(filepath: Path) -> None:
    """Run validation on snapshot file.
    
    Args:
        filepath: Path to snapshot file to validate.
        
    Raises:
        ValueError: If validation fails.
    """
    validate_snapshot.validate_snapshot(filepath)


def create_snapshot() -> None:
    """Create a new snapshot file by prompting user for input.
    
    Raises:
        ValueError: If invalid input provided or validation fails.
        OSError: If file cannot be written.
    """
    datetime_str = date_utils.get_current_datetime()
    
    # Validate datetime format
    parts = datetime_str.split("-")
    if len(parts) < 4:
        raise ValueError(f"Invalid datetime format: {datetime_str}. Expected YYYY-MM-DD-<unix epoch seconds>")
    
    filepath = get_snapshot_filepath(datetime_str)
    
    if filepath.exists():
        raise ValueError(f"Snapshot file already exists: {filepath}")
    
    # Extract date part for display
    date_part = parts[:3]
    date_str = "-".join(date_part)
    print(f"Creating snapshot for {date_str}")
    print()
    
    bodyweight = prompt_bodyweight()
    bodyfat_percentage = prompt_bodyfat_percentage()
    height = prompt_height()
    
    snapshot_data = create_snapshot_data(datetime_str, bodyweight, bodyfat_percentage, height)
    file_utils.save_json_file(snapshot_data, filepath)
    
    print(f"\nSnapshot saved to: {filepath}")
    
    print("\nValidating snapshot...")
    validate_snapshot_file(filepath)
    print("Validation passed.")


def main() -> None:
    """Main entry point for snapshot creation."""
    create_snapshot()


if __name__ == "__main__":
    main()

