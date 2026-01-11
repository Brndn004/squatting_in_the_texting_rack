#!/usr/bin/env python3
"""MCP server for fitness tracking system.

Provides tools for managing fitness data including exercises, sessions, routines, and snapshots.
"""

from pathlib import Path
from typing import Any

import json

from mcp.server import fastmcp

import exercise_discovery
import file_utils
import fitness_paths
import validate_exercise
import validate_routine
import validate_session
import validate_snapshot

# Initialize FastMCP server
mcp = fastmcp.FastMCP("Fitness Tracking System")


def _dict_to_json_string(d: dict[str, Any]) -> str:
    """Convert a dictionary to a JSON string."""
    return json.dumps(d)


@mcp.tool(
    description=(
        "Get list of available exercises. Returns a list of exercises with their "
        "human-readable names and slugified exercise names. Check the 'status' key "
        "in the returned JSON to determine if the request was successful."
    )
)
async def get_exercises() -> str:
    """Get list of available exercises.
    
    Returns:
        JSON string containing list of exercises with names and slugs.
    """
    try:
        exercises = exercise_discovery.get_available_exercises()
        
        exercise_list = []
        for name, exercise_name in exercises:
            exercise_list.append({
                "name": name,
                "exercise_name": exercise_name,
            })
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "exercises": exercise_list,
            "total": len(exercise_list),
        }
        return _dict_to_json_string(result)
    except FileNotFoundError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Directory not found: {e}",
        }
        return _dict_to_json_string(result)
    except ValueError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Validation error: {e}",
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get list of available sessions. Returns a list of sessions with their "
        "human-readable names and slugified session names. Check the 'status' key "
        "in the returned JSON to determine if the request was successful."
    )
)
async def get_sessions() -> str:
    """Get list of available sessions.
    
    Returns:
        JSON string containing list of sessions with names and slugs.
    """
    try:
        sessions_dir = fitness_paths.get_sessions_dir()
        if not sessions_dir.exists():
            raise FileNotFoundError(f"Sessions directory not found: {sessions_dir}")
        
        session_files = sorted(sessions_dir.glob("*.json"))
        if not session_files:
            raise ValueError("No session files found in sessions directory")
        
        sessions = []
        for session_file in session_files:
            try:
                session_data = file_utils.load_json_file(session_file)
                
                if "name" not in session_data:
                    raise ValueError(f"Session file missing 'name' field: {session_file}")
                
                if "session_name" not in session_data:
                    raise ValueError(f"Session file missing 'session_name' field: {session_file}")
                
                name = session_data["name"]
                session_name = session_data["session_name"]
                
                if not isinstance(name, str) or not isinstance(session_name, str):
                    raise ValueError(f"Session name fields must be strings in {session_file}")
                
                if not name or not session_name:
                    raise ValueError(f"Session name fields cannot be empty in {session_file}")
                
                sessions.append({
                    "name": name,
                    "session_name": session_name,
                })
            except (FileNotFoundError, ValueError) as e:
                raise ValueError(f"Failed to load session file {session_file}: {e}")
        
        if not sessions:
            raise ValueError("No valid sessions found")
        
        # Sort by human-readable name
        sessions.sort(key=lambda x: x["name"])
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "sessions": sessions,
            "total": len(sessions),
        }
        return _dict_to_json_string(result)
    except FileNotFoundError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Directory not found: {e}",
        }
        return _dict_to_json_string(result)
    except ValueError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Validation error: {e}",
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get list of available routines. Returns a list of routines with their "
        "human-readable names and slugified routine names. Check the 'status' key "
        "in the returned JSON to determine if the request was successful."
    )
)
async def get_routines() -> str:
    """Get list of available routines.
    
    Returns:
        JSON string containing list of routines with names and slugs.
    """
    try:
        routines_dir = fitness_paths.get_routines_dir()
        if not routines_dir.exists():
            raise FileNotFoundError(f"Routines directory not found: {routines_dir}")
        
        routine_files = sorted(routines_dir.glob("*.json"))
        if not routine_files:
            raise ValueError("No routine files found in routines directory")
        
        routines = []
        for routine_file in routine_files:
            try:
                routine_data = file_utils.load_json_file(routine_file)
                
                if "name" not in routine_data:
                    raise ValueError(f"Routine file missing 'name' field: {routine_file}")
                
                # Extract routine_name from filename (filename is {routine_name}.json)
                routine_name = routine_file.stem
                name = routine_data["name"]
                
                if not isinstance(name, str):
                    raise ValueError(f"Routine name must be a string in {routine_file}")
                
                if not name:
                    raise ValueError(f"Routine name cannot be empty in {routine_file}")
                
                routines.append({
                    "name": name,
                    "routine_name": routine_name,
                })
            except (FileNotFoundError, ValueError) as e:
                raise ValueError(f"Failed to load routine file {routine_file}: {e}")
        
        if not routines:
            raise ValueError("No valid routines found")
        
        # Sort by human-readable name
        routines.sort(key=lambda x: x["name"])
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "routines": routines,
            "total": len(routines),
        }
        return _dict_to_json_string(result)
    except FileNotFoundError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Directory not found: {e}",
        }
        return _dict_to_json_string(result)
    except ValueError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Validation error: {e}",
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get the full contents of an exercise file by its slugified exercise name. "
        "Returns the complete exercise JSON data including name, exercise_name, 1rm, "
        "and date_created. Use this tool when you need detailed exercise information "
        "such as 1RM values. The exercise_name should be the slugified name (e.g., "
        "'barbell_squat', 'barbell_bench_press'). Check the 'status' key in the "
        "returned JSON to determine if the request was successful."
    )
)
async def get_exercise(exercise_name: str) -> str:
    """Get full contents of an exercise file.
    
    Args:
        exercise_name: Slugified exercise name (e.g., "barbell_squat").
    
    Returns:
        JSON string containing the full exercise data.
    """
    try:
        if not exercise_name:
            raise ValueError("Exercise name cannot be empty")
        
        exercise_file = exercise_discovery.find_exercise_file(exercise_name)
        exercise_data = file_utils.load_json_file(exercise_file)
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "exercise": exercise_data,
        }
        return _dict_to_json_string(result)
    except FileNotFoundError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Exercise not found: {e}",
        }
        return _dict_to_json_string(result)
    except ValueError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Validation error: {e}",
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get the full contents of a session file by its slugified session name. "
        "Returns the complete session JSON data including name, session_name, exercises "
        "array with sets, reps, percent_1rm, and date_created. Use this tool when you "
        "need detailed session information such as exercise percentages and rep schemes. "
        "The session_name should be the slugified name (e.g., 'squat_horizontal_pushpull', "
        "'hinge_vertical_pushpull'). Check the 'status' key in the returned JSON to "
        "determine if the request was successful."
    )
)
async def get_session(session_name: str) -> str:
    """Get full contents of a session file.
    
    Args:
        session_name: Slugified session name (e.g., "squat_horizontal_pushpull").
    
    Returns:
        JSON string containing the full session data.
    """
    try:
        if not session_name:
            raise ValueError("Session name cannot be empty")
        
        sessions_dir = fitness_paths.get_sessions_dir()
        if not sessions_dir.exists():
            raise FileNotFoundError(f"Sessions directory not found: {sessions_dir}")
        
        session_file = sessions_dir / f"{session_name}.json"
        if not session_file.exists():
            raise FileNotFoundError(f"Session file not found: {session_file}")
        
        session_data = file_utils.load_json_file(session_file)
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "session": session_data,
        }
        return _dict_to_json_string(result)
    except FileNotFoundError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Session not found: {e}",
        }
        return _dict_to_json_string(result)
    except ValueError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Validation error: {e}",
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get the full contents of a routine file by its slugified routine name. "
        "Returns the complete routine JSON data including name, date_created, and "
        "sessions array. Use this tool when you need detailed routine information "
        "such as which sessions are included. The routine_name should be the slugified "
        "name (e.g., 'beginner', 'intermediate'). Check the 'status' key in the "
        "returned JSON to determine if the request was successful."
    )
)
async def get_routine(routine_name: str) -> str:
    """Get full contents of a routine file.
    
    Args:
        routine_name: Slugified routine name (e.g., "beginner").
    
    Returns:
        JSON string containing the full routine data.
    """
    try:
        if not routine_name:
            raise ValueError("Routine name cannot be empty")
        
        routines_dir = fitness_paths.get_routines_dir()
        if not routines_dir.exists():
            raise FileNotFoundError(f"Routines directory not found: {routines_dir}")
        
        routine_file = routines_dir / f"{routine_name}.json"
        if not routine_file.exists():
            raise FileNotFoundError(f"Routine file not found: {routine_file}")
        
        routine_data = file_utils.load_json_file(routine_file)
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "routine": routine_data,
        }
        return _dict_to_json_string(result)
    except FileNotFoundError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Routine not found: {e}",
        }
        return _dict_to_json_string(result)
    except ValueError as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Validation error: {e}",
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Validate all exercise files in the database. This tool checks that all exercise "
        "JSON files conform to the exercise schema. Returns a list of invalid exercises "
        "if any are found. Check the 'status' key in the returned JSON to determine if "
        "validation was successful. If 'status' is 'success' and 'all_valid' is True, "
        "all exercises are valid. If 'all_valid' is False, check the 'invalid_exercises' "
        "array for details about exercises that need to be fixed."
    )
)
async def validate_exercises_tool() -> str:
    """Validate all exercise files.
    
    Returns:
        JSON string with validation results including list of invalid exercises.
    """
    try:
        exercises_dir = fitness_paths.get_exercises_dir()
        
        if not exercises_dir.exists():
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": f"Exercises directory not found: {exercises_dir}",
                "invalid_exercises": [],
            }
            return _dict_to_json_string(result)
        
        exercise_files = list(exercise_discovery.discover_exercise_files())
        
        if not exercise_files:
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": "No exercise files found.",
                "invalid_exercises": [],
            }
            return _dict_to_json_string(result)
        
        invalid_exercises = []
        for exercise_file in exercise_files:
            try:
                validate_exercise.validate_exercise(exercise_file)
            except ValueError as e:
                exercise_name = None
                name_error_msg = None
                try:
                    exercise_data = file_utils.load_json_file(exercise_file)
                    if "name" not in exercise_data:
                        raise ValueError(f"Exercise file missing 'name' field: {exercise_file}")
                    exercise_name = exercise_data["name"]
                    if not isinstance(exercise_name, str):
                        raise ValueError(f"Exercise name must be a string in {exercise_file}")
                    if not exercise_name:
                        raise ValueError(f"Exercise name cannot be empty in {exercise_file}")
                except Exception as name_error:
                    name_error_msg = f"Failed to get exercise name: {name_error}"
                
                error_message = str(e)
                if name_error_msg:
                    error_message = f"{error_message}. {name_error_msg}"
                
                invalid_exercises.append({
                    "exercise": exercise_file.name,
                    "name": exercise_name,
                    "error": error_message,
                })
        
        all_valid = len(invalid_exercises) == 0
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "all_valid": all_valid,
            "total_exercises": len(exercise_files),
            "invalid_exercises": invalid_exercises,
            "message": (
                f"All {len(exercise_files)} exercises are valid."
                if all_valid
                else f"{len(invalid_exercises)} exercise(s) are invalid."
            ),
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error during validation: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Validate all session files in the database. This tool checks that all session "
        "JSON files conform to the session schema. Returns a list of invalid sessions "
        "if any are found. Check the 'status' key in the returned JSON to determine if "
        "validation was successful. If 'status' is 'success' and 'all_valid' is True, "
        "all sessions are valid. If 'all_valid' is False, check the 'invalid_sessions' "
        "array for details about sessions that need to be fixed."
    )
)
async def validate_sessions_tool() -> str:
    """Validate all session files.
    
    Returns:
        JSON string with validation results including list of invalid sessions.
    """
    try:
        sessions_dir = fitness_paths.get_sessions_dir()
        
        if not sessions_dir.exists():
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": f"Sessions directory not found: {sessions_dir}",
                "invalid_sessions": [],
            }
            return _dict_to_json_string(result)
        
        session_files = list(validate_session.get_all_session_files())
        
        if not session_files:
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": "No session files found.",
                "invalid_sessions": [],
            }
            return _dict_to_json_string(result)
        
        invalid_sessions = []
        for session_file in session_files:
            try:
                validate_session.validate_session(session_file)
            except ValueError as e:
                session_name = None
                name_error_msg = None
                try:
                    session_data = file_utils.load_json_file(session_file)
                    if "name" not in session_data:
                        raise ValueError(f"Session file missing 'name' field: {session_file}")
                    session_name = session_data["name"]
                    if not isinstance(session_name, str):
                        raise ValueError(f"Session name must be a string in {session_file}")
                    if not session_name:
                        raise ValueError(f"Session name cannot be empty in {session_file}")
                except Exception as name_error:
                    name_error_msg = f"Failed to get session name: {name_error}"
                
                error_message = str(e)
                if name_error_msg:
                    error_message = f"{error_message}. {name_error_msg}"
                
                invalid_sessions.append({
                    "session": session_file.name,
                    "name": session_name,
                    "error": error_message,
                })
        
        all_valid = len(invalid_sessions) == 0
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "all_valid": all_valid,
            "total_sessions": len(session_files),
            "invalid_sessions": invalid_sessions,
            "message": (
                f"All {len(session_files)} sessions are valid."
                if all_valid
                else f"{len(invalid_sessions)} session(s) are invalid."
            ),
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error during validation: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Validate all routine files in the database. This tool checks that all routine "
        "JSON files conform to the routine schema. Returns a list of invalid routines "
        "if any are found. Check the 'status' key in the returned JSON to determine if "
        "validation was successful. If 'status' is 'success' and 'all_valid' is True, "
        "all routines are valid. If 'all_valid' is False, check the 'invalid_routines' "
        "array for details about routines that need to be fixed."
    )
)
async def validate_routines_tool() -> str:
    """Validate all routine files.
    
    Returns:
        JSON string with validation results including list of invalid routines.
    """
    try:
        routines_dir = fitness_paths.get_routines_dir()
        
        if not routines_dir.exists():
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": f"Routines directory not found: {routines_dir}",
                "invalid_routines": [],
            }
            return _dict_to_json_string(result)
        
        routine_files = list(validate_routine.get_all_routine_files())
        
        if not routine_files:
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": "No routine files found.",
                "invalid_routines": [],
            }
            return _dict_to_json_string(result)
        
        invalid_routines = []
        for routine_file in routine_files:
            try:
                validate_routine.validate_routine(routine_file)
            except ValueError as e:
                routine_name = None
                name_error_msg = None
                try:
                    routine_data = file_utils.load_json_file(routine_file)
                    if "name" not in routine_data:
                        raise ValueError(f"Routine file missing 'name' field: {routine_file}")
                    routine_name = routine_data["name"]
                    if not isinstance(routine_name, str):
                        raise ValueError(f"Routine name must be a string in {routine_file}")
                    if not routine_name:
                        raise ValueError(f"Routine name cannot be empty in {routine_file}")
                except Exception as name_error:
                    name_error_msg = f"Failed to get routine name: {name_error}"
                
                error_message = str(e)
                if name_error_msg:
                    error_message = f"{error_message}. {name_error_msg}"
                
                invalid_routines.append({
                    "routine": routine_file.name,
                    "name": routine_name,
                    "error": error_message,
                })
        
        all_valid = len(invalid_routines) == 0
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "all_valid": all_valid,
            "total_routines": len(routine_files),
            "invalid_routines": invalid_routines,
            "message": (
                f"All {len(routine_files)} routines are valid."
                if all_valid
                else f"{len(invalid_routines)} routine(s) are invalid."
            ),
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error during validation: {e}",
        }
        return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Validate all snapshot files in the database. This tool checks that all snapshot "
        "JSON files conform to the snapshot schema. Returns a list of invalid snapshots "
        "if any are found. Check the 'status' key in the returned JSON to determine if "
        "validation was successful. If 'status' is 'success' and 'all_valid' is True, "
        "all snapshots are valid. If 'all_valid' is False, check the 'invalid_snapshots' "
        "array for details about snapshots that need to be fixed."
    )
)
async def validate_snapshots_tool() -> str:
    """Validate all snapshot files.
    
    Returns:
        JSON string with validation results including list of invalid snapshots.
    """
    try:
        snapshots_dir = fitness_paths.get_snapshots_dir()
        
        if not snapshots_dir.exists():
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": f"Snapshots directory not found: {snapshots_dir}",
                "invalid_snapshots": [],
            }
            return _dict_to_json_string(result)
        
        snapshot_files = list(validate_snapshot.get_all_snapshot_files())
        
        if not snapshot_files:
            result = {
                "status": "success",
                "stdout": "",
                "stderr": "",
                "all_valid": True,
                "message": "No snapshot files found.",
                "invalid_snapshots": [],
            }
            return _dict_to_json_string(result)
        
        invalid_snapshots = []
        for snapshot_file in snapshot_files:
            try:
                validate_snapshot.validate_snapshot(snapshot_file)
            except ValueError as e:
                invalid_snapshots.append({
                    "snapshot": snapshot_file.name,
                    "error": str(e),
                })
        
        all_valid = len(invalid_snapshots) == 0
        
        result = {
            "status": "success",
            "stdout": "",
            "stderr": "",
            "all_valid": all_valid,
            "total_snapshots": len(snapshot_files),
            "invalid_snapshots": invalid_snapshots,
            "message": (
                f"All {len(snapshot_files)} snapshots are valid."
                if all_valid
                else f"{len(invalid_snapshots)} snapshot(s) are invalid."
            ),
        }
        return _dict_to_json_string(result)
    except Exception as e:
        result = {
            "status": "failure",
            "stdout": "",
            "stderr": f"Unexpected error during validation: {e}",
        }
        return _dict_to_json_string(result)


if __name__ == "__main__":
    mcp.run(transport="stdio")
