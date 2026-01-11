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
   - Create `fitness/sessions/` directory (for session data files)

3. **Verify structure**
   - Ensure `fitness/foundation.md` still exists and is accessible
   - Confirm all six new directories are created

### Deliverables:
- `fitness/` directory with `scripts/`, `schemas/`, `exercises/`, `snapshots/`, `routines/`, and `sessions/` subdirectories
- Existing `foundation.md` file preserved in new location

---

## Phase 2: JSON Schema Definition

### Tasks:
1. **Create `snapshot_schema.json`**
   - Create `fitness/schemas/snapshot_schema.json` with JSON Schema specification
   - Define structure:
     - `date` (string, datetime format YYYY-MM-DD-<unix epoch seconds>, required)
     - `body_metrics` (object, required):
       - `bodyweight` (number, required, in pounds)
       - `bodyfat_percentage` (number, required, between 0 and 1 inclusive)
       - `height` (number, required, in inches)
   - Note: Exercise, session, and routine data are stored separately and referenced by the snapshot

2. **Create `exercise_schema.json`**
   - Create `fitness/schemas/exercise_schema.json` with JSON Schema specification
   - Define structure for individual exercise files stored in `fitness/exercises/`:
     - `name` (string, required) - Human-readable name of the exercise (e.g., "Barbell Squat")
     - `exercise_name` (string, required) - Slugified name used for filename (e.g., "barbell_squat")
     - `1rm` (number, required, in pounds, can be 0 or positive)
     - `date_created` (string, datetime format YYYY-MM-DD-<unix epoch seconds>, required) - datetime when this exercise data was recorded
   - Filename format: `{exercise_name}.json` (no date in filename)
   - Add validation rules:
     - Add appropriate type constraints and value ranges (1rm can be 0 or positive)

3. **Create `session_schema.json`**
   - Create `fitness/schemas/session_schema.json` with JSON Schema specification
   - Define structure for individual session files stored in `fitness/sessions/`:
     - `name` (string, required) - Human-readable name of the session (e.g., "Push Day")
     - `session_name` (string, required) - Slugified name used for filename (e.g., "push_day")
     - `exercises` (array, required) - list of exercises in this session
       - Each exercise contains:
         - `exercise_name` (string, required, must reference an exercise file in `exercises/` directory)
         - `sets` (integer, required) - number of sets for this exercise in this session
         - `reps` (integer, required) - number of reps per set
         - `percent_1rm` (number, required, between 0 and 1 inclusive) - percentage of 1RM to use
         - Note: `weight` is computed from exercise 1rm * percent_1rm, not defined by user
     - `date_created` (string, datetime format YYYY-MM-DD-<unix epoch seconds>, required) - datetime when this session was created
   - Filename format: `{session_name}.json` (no date in filename)
   - Add validation rules:
     - Ensure `exercise_name` references valid exercise files (custom validation)
     - Validate that `percent_1rm` is between 0 and 1 (inclusive)
     - Add appropriate type constraints and value ranges

4. **Create `routine_schema.json`**
   - Create `fitness/schemas/routine_schema.json` with JSON Schema specification
   - Schema description: "Schema for routine files representing a single week of workouts"
   - Define structure for routine files stored in `fitness/routines/` directory:
     - `name` (string, required) - Human-readable name of the routine (e.g., "Beginner Routine")
     - `routine_name` (string, required) - Slugified name used for filename (e.g., "beginner_routine")
     - `date_created` (string, datetime format YYYY-MM-DD-<unix epoch seconds>, required) - datetime when this routine was created
     - `sessions` (array, required) - list of session names (strings) that reference session files in `sessions/` directory
       - Each string is a `session_name` slug that must reference a valid session file
   - Filename format: `{routine_name}.json` (no date in filename)
   - Add validation rules:
     - Ensure `session_name` references valid session files (custom validation)
     - Add appropriate type constraints

5. **Clarify data storage structure**
   - Exercise data stored as individual JSON files in `fitness/exercises/` directory (e.g., `barbell_squat.json`)
   - Session data stored as individual JSON files in `fitness/sessions/` directory (e.g., `push_day.json`)
   - Routine data stored as JSON files in `fitness/routines/` directory (e.g., `beginner_routine.json`)
   - Snapshot files in `fitness/snapshots/` contain date and body_metrics (e.g., `2026-01-11-1768169486_snapshot.json`)
   - Cross-validation: Ensure session exercise names reference existing exercise files, and routine session names reference existing session files

### Deliverables:
- `fitness/schemas/snapshot_schema.json` - Snapshot schema file (date + body_metrics only)
- `fitness/schemas/exercise_schema.json` - Exercise definition schema file (for exercise files in `exercises/` directory)
- `fitness/schemas/session_schema.json` - Session schema file (for session files in `sessions/` directory)
- `fitness/schemas/routine_schema.json` - Routine schema file (for routine files in `routines/` directory)
- All schemas stored in `schemas/` directory
- All schemas validate required fields independently
- Exercise, session, and routine schemas are separate from snapshot schema

---

## Phase 3: Validation Scripts

### Tasks:
1. **Create `fitness/scripts/validate_snapshot.py`**
   - Create validation script for snapshot files
   - When run as a script, validates ALL snapshot files in `fitness/snapshots/` directory
   - Structure the script with free functions and a `main()` dispatcher
   - When implemented, validate that `bodyfat_percentage` is between 0 and 1 (inclusive)
   - Use `print` statements (no logging)
   - Raise hard exceptions (no defaults or fallbacks)

2. **Create `fitness/scripts/validate_exercise.py`**
   - Create validation script for exercise files
   - When run as a script, validates ALL exercise files in `fitness/exercises/` directory
   - Structure the script with free functions and a `main()` dispatcher
   - Use `print` statements (no logging)
   - Raise hard exceptions (no defaults or fallbacks)

3. **Create `fitness/scripts/validate_session.py`**
   - Create validation script for session files
   - When run as a script, validates ALL session files in `fitness/sessions/` directory
   - Structure the script with free functions and a `main()` dispatcher
   - When implemented, validate that `percent_1rm` is between 0 and 1 (inclusive) for all exercises
   - Use `print` statements (no logging)
   - Raise hard exceptions (no defaults or fallbacks)

4. **Create `fitness/scripts/validate_routine.py`**
   - Create validation script for routine files
   - When run as a script, validates ALL routine files in `fitness/routines/` directory
   - Structure the script with free functions and a `main()` dispatcher
   - Validate that referenced session files exist
   - Use `print` statements (no logging)
   - Raise hard exceptions (no defaults or fallbacks)

### Deliverables:
- `fitness/scripts/validate_snapshot.py` - Validation script for snapshots
- `fitness/scripts/validate_exercise.py` - Validation script for exercises
- `fitness/scripts/validate_session.py` - Validation script for sessions
- `fitness/scripts/validate_routine.py` - Validation script for routines
- All scripts validate all files in their respective directories when run

---

## Phase 4: Create Snapshot Script

### Tasks:
1. **Create `fitness/scripts/create_snapshot.py`**
   - Script should:
     - Use current datetime automatically (format: YYYY-MM-DD-<unix epoch seconds>)
     - Prompt user for input fields:
       - Bodyweight (required, in pounds)
       - Bodyfat percentage (required, between 0 and 1 inclusive)
       - Height (required, in inches, accepts space-delimited feet and inches like "5 9")
     - Save snapshot data to `fitness/snapshots/YYYY-MM-DD-<unix epoch seconds>_snapshot.json`
     - Filename format: `YYYY-MM-DD-<unix epoch seconds>_snapshot.json`

2. **Add error handling**
   - For interactive prompts, reject invalid input, explain the issue, and re-prompt (no hard errors)
   - Provide clear error messages
   - Height input accepts space-delimited feet and inches (e.g., "5 9" for 5 feet 9 inches)

3. **Run validation script**
   - After saving the snapshot file, run `validate_snapshot.py` on the created file
   - Report validation errors if any

### Deliverables:
- `fitness/scripts/create_snapshot.py` - Fully functional script
- Script prompts for body metrics, uses current datetime, validates, and saves JSON
- Example snapshot file created in `fitness/snapshots/`

---

## Phase 5: Create Exercise Script

### Tasks:
1. **Create `fitness/scripts/create_exercise.py`**
   - Script should:
     - Use current datetime automatically (format: YYYY-MM-DD-<unix epoch seconds>)
     - Loop to allow creating multiple exercises in a row
     - Prompt user for input fields:
       - Exercise name (required, human-readable string, e.g., "Barbell Squat")
         - Script slugifies the name to create `exercise_name` (e.g., "barbell_squat")
         - Checks if exercise file already exists and re-prompts if it does
       - One-rep max (1RM) (required, in pounds, can be 0 or positive)
     - Save exercise data to `fitness/exercises/{exercise_name}.json`
     - Filename format: `{exercise_name}.json` (no date in filename)
     - Save each exercise immediately after all required inputs are entered
     - Anticipate Ctrl+C command to finish creating exercises

2. **Add error handling**
   - For interactive prompts, reject invalid input, explain the issue, and re-prompt (no hard errors)
   - Check if exercise file already exists after name entry and re-prompt if it does
   - Provide clear error messages
   - Handle Ctrl+C gracefully

3. **Run validation script**
   - After saving each exercise file, run `validate_exercise.py` on the created file
   - Report validation errors if any

### Deliverables:
- `fitness/scripts/create_exercise.py` - Fully functional script
- Script loops to create multiple exercises, prompts for exercise data, uses current datetime, validates, and saves JSON
- Example exercise file created in `fitness/exercises/`

---

## Phase 5.5: Create Session Script

### Tasks:
1. **Create `fitness/scripts/create_session.py`**
   - Script should:
     - Use current datetime automatically (format: YYYY-MM-DD-<unix epoch seconds>)
     - Scan `exercises/` directory to find all existing exercise files
     - Extract exercise names from existing exercise files
     - Prompt user for input fields:
       - Session name (required, human-readable string, e.g., "Push Day")
         - Script slugifies the name to create `session_name` (e.g., "push_day")
         - Checks if session file already exists and re-prompts if it does
       - For each exercise in the session (user types "Done" when finished):
         - Exercise name (required, selected from auto-populated list of existing exercises)
         - Sets (required, positive integer) - number of sets for this exercise in this session
         - Reps (required, positive integer) - number of reps per set
         - Percent 1RM (required, between 0 and 1 inclusive) - percentage of 1RM to use (weight will be computed)
     - Save session data to `fitness/sessions/{session_name}.json`
     - Filename format: `{session_name}.json` (no date in filename)
     - Creates one session at a time, terminates cleanly after "Done" is typed

2. **Add error handling**
   - For interactive prompts, reject invalid input, explain the issue, and re-prompt (no hard errors)
   - Check if session file already exists after name entry and re-prompt if it does
   - Re-display available exercises list between exercise entries
   - Provide clear error messages

3. **Run validation script**
   - After saving the session file, run `validate_session.py` on the created file
   - Report validation errors if any

### Deliverables:
- `fitness/scripts/create_session.py` - Fully functional script
- Script prompts for session data, uses current datetime, validates exercise references, validates, and saves JSON
- Example session file created in `fitness/sessions/`

---

## Phase 6: Create Routine Script

### Tasks:
1. **Create `fitness/scripts/create_routine.py`**
   - Script should:
     - Use current datetime automatically (format: YYYY-MM-DD-<unix epoch seconds>)
     - Scan `sessions/` directory to find all existing session files
     - Extract session names from existing session files
     - Prompt user for input fields:
       - Routine name (required, human-readable string, e.g., "Beginner Routine")
         - Script slugifies the name to create `routine_name` (e.g., "beginner_routine")
         - Checks if routine file already exists and re-prompts if it does
       - Number of sessions (required, positive integer)
       - Session selections (required, space-delimited numbers, e.g., "2 1 3")
         - Number of entries must match the number of sessions required
         - Each number references a session from the available sessions list
     - Save routine data to `fitness/routines/{routine_name}.json`
     - Filename format: `{routine_name}.json` (no date in filename)

2. **Add error handling**
   - For interactive prompts, reject invalid input, explain the issue, and re-prompt (no hard errors)
   - Check if routine file already exists after name entry and re-prompt if it does
   - Validate that number of session selections matches the required number of sessions
   - Validate that referenced session files exist
   - Provide clear error messages

3. **Run validation script**
   - After saving the routine file, run `validate_routine.py` on the created file
   - Report validation errors if any

### Deliverables:
- `fitness/scripts/create_routine.py` - Fully functional script
- Script prompts for routine data, uses current datetime, validates session references, validates, and saves JSON
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
     - `get_sessions_dir() -> Path` - Returns Path to sessions directory
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
     - `get_current_datetime() -> str` - Returns current datetime in format YYYY-MM-DD-<unix epoch seconds>
     - `format_datetime_for_filename(datetime_str: str) -> str` - Formats datetime for use in filenames (ensures valid filename characters)
     - `parse_datetime(datetime_str: str) -> datetime.datetime` - Parses datetime string in format YYYY-MM-DD-<unix epoch seconds>, handles errors
   - Use `datetime` module for date operations
   - Include proper type hints and docstrings
   - No external dependencies (only uses standard library `datetime`)

### Deliverables:
- `fitness/scripts/date_utils.py` - Date utility module
- Module can be tested independently
- All functions handle datetime operations correctly

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
     - `load_session_schema() -> dict` - Loads session schema
     - `load_routine_schema() -> dict` - Loads routine schema
     - `load_all_schemas() -> dict[str, dict]` - Loads all schemas, returns dict with keys: "snapshot", "exercise", "session", "routine"
   - Handle file not found errors gracefully (raise hard exceptions, no defaults)
   - Handle JSON parsing errors (raise hard exceptions, no defaults)
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
     - `get_available_exercises() -> list[tuple[str, str]]` - Returns list of tuples (human-readable name, slugified exercise_name) from all exercise files
     - `find_exercise_file(exercise_name: str) -> Path` - Finds exercise file by slugified name (raises FileNotFoundError if not found, no defaults)
   - Handle missing files gracefully (raise hard exceptions, no defaults)
   - Handle malformed JSON files (raise hard exceptions, no defaults)
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
- Schemas are split into four files stored in `schemas/` directory: `snapshot_schema.json`, `exercise_schema.json`, `session_schema.json`, and `routine_schema.json`
- Snapshot schema only contains date and body_metrics (no exercise/session/routine data)
- Schema definitions stored in `schemas/` directory
- Exercise data stored as separate JSON files in `exercises/` directory (filenames: `{exercise_name}.json`)
- Session data stored as separate JSON files in `sessions/` directory (filenames: `{session_name}.json`)
- Routine data stored as separate JSON files in `routines/` directory (filenames: `{routine_name}.json`)
- Snapshot data stored as JSON files in `snapshots/` directory (filenames: `YYYY-MM-DD-<unix epoch seconds>_snapshot.json`)
- The session structure allows for tracking any exercise, not just the big three
- Routines reference sessions by name (slugified `session_name`), sessions reference exercises by name (slugified `exercise_name`)
- Datetime format: YYYY-MM-DD-<unix epoch seconds> (e.g., "2026-01-11-1768169486")
- All names use slugification for filenames (human-readable `name` field + slugified `*_name` field)
- Units: pounds (lb) for weight, inches (in) for height (no metric units)
- Percentages stored as numbers between 0 and 1 (inclusive), not as percentages (0-100)
- Interactive prompts reject invalid input, explain the issue, and re-prompt (no hard errors)
- Validation scripts validate ALL files in their respective directories when run as scripts
- No defaults or fallbacks: all code uses hard exceptions with clear error messages
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
