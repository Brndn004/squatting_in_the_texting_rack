# Fitness Tracking System Implementation Plan

This document outlines the step-by-step phases for implementing a fitness tracking system with JSON schema-based fitness stats, data collection scripts, and an MCP server.

## Overview

The system will track fitness metrics including body measurements and exercise performance (squat, bench press, deadlift). All data will be stored as JSON snapshots with validation.

## Phase 1: Directory Structure Setup

### Tasks:
1. **Rename `workouts/` to `fitness/`**
   - Move all existing files from `workouts/` to `fitness/`
   - Update any references to the old directory name

2. **Create new subdirectories**
   - Create `fitness/scripts/` directory
   - Create `fitness/schemas/` directory (for schema definitions)
   - Create `fitness/exercises/` directory (for exercise data files)
   - Create `fitness/snapshots/` directory (for snapshot data files)
   - Create `fitness/routines/` directory (for routine data files)

3. **Verify structure**
   - Ensure `fitness/foundation.md` still exists and is accessible
   - Confirm all five new directories are created

### Deliverables:
- `fitness/` directory with `scripts/`, `schemas/`, `exercises/`, `snapshots/`, and `routines/` subdirectories
- Existing `foundation.md` file preserved in new location

---

## Phase 2: JSON Schema Definition

### Tasks:
1. **Create `snapshot_schema.json`**
   - Create `fitness/schemas/snapshot_schema.json` with JSON Schema specification
   - Define structure:
     - `date` (string, ISO 8601 date format, required)
     - `body_metrics` (object, required):
       - `bodyweight` (number, required, in pounds)
       - `bodyfat_percentage` (number, required, in percent)
       - `height` (number, required, in inches)
   - Note: Exercise and routine data are stored separately and referenced by the snapshot

2. **Create `exercise_schema.json`**
   - Create `fitness/schemas/exercise_schema.json` with JSON Schema specification
   - Define structure for individual exercise files stored in `fitness/exercises/`:
     - `exercise_name` (string, required, e.g., "squat", "bench_press", "deadlift")
     - `1rm` (number, required, in pounds)
     - `date` (string, ISO 8601 date format, required) - date when this exercise data was recorded
   - Add validation rules:
     - Add appropriate type constraints and value ranges (e.g., positive numbers)

3. **Create `routine_schema.json`**
   - Create `fitness/schemas/routine_schema.json` with JSON Schema specification
   - Define structure for routine files stored in `fitness/routines/` or as part of snapshot:
     - `date` (string, ISO 8601 date format, required) - date when this routine was active
     - `exercises` (array, required):
       - Each element contains:
         - `exercise_name` (string, required, must reference an exercise file in `exercises/` directory)
         - `sets_per_week` (integer, required, positive)
   - Add validation rules:
     - Ensure `exercise_name` references valid exercise files (custom validation)
     - Add appropriate type constraints and value ranges

4. **Clarify data storage structure**
   - Exercise data stored as individual JSON files in `fitness/exercises/` directory (e.g., `squat_2025-01-11.json`)
   - Routine data stored as JSON files in `fitness/routines/` directory or referenced by snapshot
   - Snapshot files in `fitness/snapshots/` contain date and body_metrics, and may reference exercise/routine files
   - Cross-validation: Ensure routine exercise names reference existing exercise files

### Deliverables:
- `fitness/schemas/snapshot_schema.json` - Snapshot schema file (date + body_metrics only)
- `fitness/schemas/exercise_schema.json` - Exercise definition schema file (for exercise files in `exercises/` directory)
- `fitness/schemas/routine_schema.json` - Routine schema file (for routine files in `routines/` directory)
- All schemas stored in `schemas/` directory
- All schemas validate required fields independently
- Exercise and routine schemas are separate from snapshot schema

---

## Phase 3: Validation Scripts

### Tasks:
1. **Create `fitness/scripts/validate_snapshot.py`**
   - Create a no-op validation script for snapshot files
   - Script should accept a snapshot file path as argument
   - For now, just print a placeholder message indicating validation will be implemented later
   - Structure the script to be ready for future validation logic

2. **Create `fitness/scripts/validate_exercise.py`**
   - Create a no-op validation script for exercise files
   - Script should accept an exercise file path as argument
   - For now, just print a placeholder message indicating validation will be implemented later
   - Structure the script to be ready for future validation logic

3. **Create `fitness/scripts/validate_routine.py`**
   - Create a no-op validation script for routine files
   - Script should accept a routine file path as argument
   - For now, just print a placeholder message indicating validation will be implemented later
   - Structure the script to be ready for future validation logic

### Deliverables:
- `fitness/scripts/validate_snapshot.py` - No-op validation script for snapshots
- `fitness/scripts/validate_exercise.py` - No-op validation script for exercises
- `fitness/scripts/validate_routine.py` - No-op validation script for routines
- All scripts accept file path arguments and are structured for future implementation

---

## Phase 4: Create Snapshot Script

### Tasks:
1. **Create `fitness/scripts/create_snapshot.py`**
   - Script should:
     - Use today's date automatically (ISO 8601 format: YYYY-MM-DD)
     - Prompt user for input fields:
       - Bodyweight (required, in pounds)
       - Bodyfat percentage (required, in percent)
       - Height (required, in inches)
     - Save snapshot data to `fitness/snapshots/YYYY-MM-DD_snapshot.json`
     - Filename format: `YYYY-MM-DD_snapshot.json`

2. **Add error handling**
   - Handle invalid inputs gracefully
   - Provide clear error messages
   - Allow user to retry or cancel

3. **Run validation script**
   - After saving the snapshot file, run `validate_snapshot.py` on the created file
   - Report validation errors if any

### Deliverables:
- `fitness/scripts/create_snapshot.py` - Fully functional script
- Script prompts for body metrics, uses today's date, validates, and saves JSON
- Example snapshot file created in `fitness/snapshots/`

---

## Phase 5: Create Exercise Script

### Tasks:
1. **Create `fitness/scripts/create_exercise.py`**
   - Script should:
     - Use today's date automatically (ISO 8601 format: YYYY-MM-DD)
     - Prompt user for input fields:
       - Exercise name (required, string, e.g., "squat", "bench_press", "deadlift")
       - 1RM (required, in pounds)
     - Save exercise data to `fitness/exercises/{exercise_name}_YYYY-MM-DD.json`
     - Filename format: `{exercise_name}_YYYY-MM-DD.json`

2. **Add error handling**
   - Handle invalid inputs gracefully
   - Provide clear error messages
   - Allow user to retry or cancel

3. **Run validation script**
   - After saving the exercise file, run `validate_exercise.py` on the created file
   - Report validation errors if any

### Deliverables:
- `fitness/scripts/create_exercise.py` - Fully functional script
- Script prompts for exercise data, uses today's date, validates, and saves JSON
- Example exercise file created in `fitness/exercises/`

---

## Phase 6: Create Routine Script

### Tasks:
1. **Create `fitness/scripts/create_routine.py`**
   - Script should:
     - Use today's date automatically (ISO 8601 format: YYYY-MM-DD)
     - Scan `exercises/` directory to find all existing exercise files
     - Extract exercise names from existing exercise files
     - Auto-populate exercise options based on exercises found in `exercises/` folder
     - Prompt user for routine entries:
       - For each exercise in the routine:
         - Exercise name (required, selected from auto-populated list of existing exercises)
         - Sets per week (required, positive integer)
     - Save routine data to `fitness/routines/YYYY-MM-DD_routine.json`
     - Filename format: `YYYY-MM-DD_routine.json`

2. **Add error handling**
   - Handle invalid inputs gracefully
   - Provide clear error messages
   - Allow user to retry or cancel
   - Validate that referenced exercise files exist

3. **Run validation script**
   - After saving the routine file, run `validate_routine.py` on the created file
   - Report validation errors if any

### Deliverables:
- `fitness/scripts/create_routine.py` - Fully functional script
- Script prompts for routine entries, uses today's date, validates exercise references, validates, and saves JSON
- Example routine file created in `fitness/routines/`

---

## Phase 7: Path Utilities Module

### Tasks:
1. **Create `fitness/scripts/fitness_paths.py`**
   - Path utility module following single responsibility principle
   - Functions:
     - `get_fitness_dir() -> Path` - Returns Path to fitness directory (base directory)
     - `get_snapshots_dir() -> Path` - Returns Path to snapshots directory
     - `get_exercises_dir() -> Path` - Returns Path to exercises directory
     - `get_routines_dir() -> Path` - Returns Path to routines directory
     - `get_schemas_dir() -> Path` - Returns Path to schemas directory
     - `get_scripts_dir() -> Path` - Returns Path to scripts directory
   - All functions use `Path(__file__).parent.parent` pattern for relative path resolution
   - Include proper type hints and docstrings
   - No external dependencies (only uses `pathlib.Path`)

### Deliverables:
- `fitness/scripts/fitness_paths.py` - Path utility module
- Module can be tested independently
- All functions return correct Path objects

---

## Phase 8: Date Utilities Module

### Tasks:
1. **Create `fitness/scripts/date_utils.py`**
   - Date utility module
   - Functions:
     - `get_today_date() -> str` - Returns today's date in ISO 8601 format (YYYY-MM-DD)
     - `format_date_for_filename(date: str) -> str` - Formats date for use in filenames (ensures valid filename characters)
     - `parse_date(date_str: str) -> datetime.date` - Parses ISO 8601 date string, handles errors
   - Use `datetime` module for date operations
   - Include proper type hints and docstrings
   - No external dependencies (only uses standard library `datetime`)

### Deliverables:
- `fitness/scripts/date_utils.py` - Date utility module
- Module can be tested independently
- All functions handle date operations correctly

---

## Phase 9: File I/O Utilities Module

### Tasks:
1. **Create `fitness/scripts/file_utils.py`**
   - File I/O utility module
   - Functions:
     - `save_json_file(data: dict, filepath: Path) -> None` - Saves dict to JSON file with proper formatting
     - `load_json_file(filepath: Path) -> dict` - Loads JSON file, handles errors
     - `ensure_directory_exists(dirpath: Path) -> None` - Creates directory if it doesn't exist
   - Handle file I/O errors gracefully
   - Use proper encoding (UTF-8)
   - Include proper type hints and docstrings
   - Imports from `fitness_paths` for directory paths

### Deliverables:
- `fitness/scripts/file_utils.py` - File I/O utility module
- Module can be tested independently (with fitness_paths)
- All functions handle file operations correctly

---

## Phase 10: Schema Loader Module

### Tasks:
1. **Create `fitness/scripts/schema_loader.py`**
   - Schema loading module (validation logic belongs in validation scripts)
   - Functions:
     - `load_schema(schema_name: str) -> dict` - Loads a schema file by name (e.g., "snapshot_schema.json")
     - `load_snapshot_schema() -> dict` - Loads snapshot schema
     - `load_exercise_schema() -> dict` - Loads exercise schema
     - `load_routine_schema() -> dict` - Loads routine schema
     - `load_all_schemas() -> dict[str, dict]` - Loads all schemas, returns dict with keys: "snapshot", "exercise", "routine"
   - Handle file not found errors gracefully
   - Handle JSON parsing errors
   - Include proper type hints and docstrings
   - Imports from `fitness_paths` and `file_utils`
   - Note: Validation logic will be implemented in validation scripts (Phase 3), which will call the appropriate validation script

### Deliverables:
- `fitness/scripts/schema_loader.py` - Schema loading module
- Module can be tested independently (with fitness_paths and file_utils)
- All functions handle schema loading correctly
- Validation is handled by validation scripts, not this module

---

## Phase 11: Exercise Discovery Module

### Tasks:
1. **Create `fitness/scripts/exercise_discovery.py`**
   - Exercise file discovery and parsing module
   - Functions:
     - `discover_exercise_files() -> list[Path]` - Scans exercises directory, returns list of exercise file paths
     - `extract_exercise_name_from_file(filepath: Path) -> str` - Extracts exercise name from exercise JSON file
     - `get_available_exercises() -> list[str]` - Returns list of unique exercise names from all exercise files
     - `find_exercise_file(exercise_name: str, date: str | None = None) -> Path | None` - Finds exercise file by name and optionally date
   - Handle missing files gracefully
   - Handle malformed JSON files
   - Include proper type hints and docstrings
   - Imports from `fitness_paths` and `file_utils`

### Deliverables:
- `fitness/scripts/exercise_discovery.py` - Exercise discovery module
- Module can be tested independently (with fitness_paths and file_utils)
- All functions handle exercise file discovery correctly

---

## Phase 12: MCP Server Implementation

### Tasks:
1. **Create `fitness/scripts/fitness_mcp.py`**
   - Create a no-op placeholder MCP server file
   - Pattern match basic structure from `nutrition/scripts/usda_mcp_server.py`
   - Use FastMCP framework
   - For now, just create the basic server structure with placeholder message
   - Structure the file to be ready for future MCP tool implementation

### Deliverables:
- `fitness/scripts/fitness_mcp.py` - No-op placeholder MCP server file
- File is structured and ready for future implementation

---

## Notes

- All body_metrics fields are required (bodyweight, bodyfat_percentage, height)
- Schemas are split into three files stored in `schemas/` directory: `snapshot_schema.json`, `exercise_schema.json`, and `routine_schema.json`
- Snapshot schema only contains date and body_metrics (no exercise/routine data)
- Schema definitions stored in `schemas/` directory
- Exercise data stored as separate JSON files in `exercises/` directory
- Routine data stored as separate JSON files in `routines/` directory
- Snapshot data stored as JSON files in `snapshots/` directory
- The routine structure allows for tracking any exercise, not just the big three
- Date format should be ISO 8601 (YYYY-MM-DD) for consistency
- Consider adding versioning to the schemas if structure changes are anticipated
- MCP server tools should follow the same error handling patterns as the USDA server for consistency
- When loading schemas, ensure `$ref` resolution works correctly (may need a resolver for relative paths)

---

## Phase 13: Compute Bodyweight Multiple

### Tasks:
1. **Figure out what this means later**
   - Determine how bodyweight multiple should be computed
   - Determine where it should be stored
   - Determine when it should be calculated

### Deliverables:
- Understanding of what bodyweight multiple computation entails
- Plan for implementation
