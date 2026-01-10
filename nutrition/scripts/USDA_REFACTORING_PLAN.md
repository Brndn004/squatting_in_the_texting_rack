# USDA Lookup Refactoring Plan

## Overview

Refactor `usda_lookup.py` to separate business logic from user interaction. Extract all business logic into a library module `usda_lib.py` that can be called programmatically. The CLI script will remain for interactive use, but will import and use the library functions.

## Goals

- Separate business logic from user interaction
- Remove logger dependency, use `print()` for informational output
- Library functions should be pure (no `input()`, no user prompts)
- Keep interactive CLI functionality intact
- Create MCP server for programmatic use by AI agents in Cursor on macOS

---

## Phase 1: Create Library Module Structure

### Tasks

1. **Create `usda_lib.py`**
   - Create new file `nutrition/scripts/usda_lib.py`
   - Copy all constants from `usda_lookup.py`:
     - `_API_KEY_ENV_VAR`
     - `_BASE_URL`
     - `_SEARCH_ENDPOINT`
     - `_DETAILS_ENDPOINT`
     - `_DEFAULT_PAGE_SIZE`
     - `_JSON_INDENT`

2. **Move Path Helper Functions**
   - Move `_get_ingredients_dir()` → `usda_lib.py` (keep private, internal helper)
   - Move `_get_logs_dir()` → `usda_lib.py` (keep private, internal helper)
   - Keep as private functions since they are only used internally within the library module

3. **Move Utility Functions**
   - Move `_format_api_call_for_logging()` → `usda_lib.py` (keep private, internal helper)
   - Move `_save_error_log()` → `usda_lib.py` (keep private, internal helper)
   - Move `_get_data_type_priority()` → `usda_lib.py` (keep private, internal helper)
   - Move `_sort_foods_by_priority()` → `usda_lib.py` as `sort_foods_by_priority()` (public, may be useful externally)

### Success Criteria

- New `usda_lib.py` file exists with constants and utility functions
- No functionality changes, just code movement
- All moved functions work identically

---

## Phase 2: Refactor API Key Handling

### Tasks

1. **Create Custom Exception**
   - In `usda_lib.py`, create `class UsdaApiKeyError(Exception)`
   - This replaces `sys.exit()` calls

2. **Refactor `_get_api_key()`**
   - Move `_get_api_key()` → `usda_lib.py`
   - Change from `sys.exit(1)` to raising `UsdaApiKeyError`
   - Remove logger calls, use `print()` for error messages if needed
   - Function signature: `def get_api_key() -> str:`
   - Raises: `UsdaApiKeyError` if key not found

### Success Criteria

- `get_api_key()` raises exception instead of calling `sys.exit()`
- Exception message contains helpful information about setting the key
- No logger dependencies

---

## Phase 3: Move Core API Functions

### Tasks

1. **Move Search Functions**
   - Move `search_ingredient()` → `usda_lib.py`
     - Remove logger calls, use `print()` for informational messages
     - Keep error handling but use `print()` instead of `logger.error()`
   - Move `search_ingredient_prioritized()` → `usda_lib.py`
     - Replace `logger.info()` with `print()` for informational output
     - Replace `logger.warning()` with `print()` for warnings
     - Replace `logger.error()` with `print()` for errors

2. **Move Food Details Function**
   - Move `get_food_details()` → `usda_lib.py`
     - Replace logger calls with `print()`

3. **Update Function Signatures**
   - Remove `logger` parameters (no longer needed)
   - All functions should be pure (no side effects except file I/O and API calls)

### Success Criteria

- All API functions moved to `usda_lib.py`
- No logger dependencies
- Functions use `print()` for informational output
- Functions raise exceptions on errors (don't call `sys.exit()`)

---

## Phase 4: Move File I/O Functions

### Tasks

1. **Move File Operations**
   - Move `save_ingredient_file()` → `usda_lib.py`
     - Replace `logger.info()` with `print()` for success messages
     - Replace `logger.error()` with `print()` for errors
     - Keep `OSError` exception raising
   - Move `update_reverse_lookup()` → `usda_lib.py`
     - Replace `logger.warning()` with `print()` for warnings
     - Replace `logger.debug()` with `print()` for debug info (or remove if not needed)

2. **Ensure Pure Functions**
   - No `input()` calls
   - No user prompts
   - Functions take parameters and return values or raise exceptions

### Success Criteria

- File I/O functions moved to `usda_lib.py`
- No user interaction in library functions
- Functions use `print()` for informational output
- Exceptions raised instead of `sys.exit()`

---

## Phase 5: Refactor CLI Script

### Tasks

1. **Update `usda_lookup.py` Imports**
   - Import the `usda_lib` module (not individual functions/classes):
     ```python
     import usda_lib
     ```
   - Use module-qualified names when calling functions:
     - `usda_lib.get_api_key()`
     - `usda_lib.search_ingredient_prioritized()`
     - `usda_lib.get_food_details()`
     - `usda_lib.save_ingredient_file()`
     - `usda_lib.update_reverse_lookup()`
     - `usda_lib.sort_foods_by_priority()`
     - `usda_lib.UsdaApiKeyError` (exception class)

2. **Keep User Interaction Functions**
   - Keep `display_search_results()` in `usda_lookup.py` (interactive only)
   - Keep `get_user_selection()` in `usda_lookup.py` (interactive only)
   - These remain CLI-specific

3. **Update `main()` Function**
   - Wrap `usda_lib.get_api_key()` call in try/except for `usda_lib.UsdaApiKeyError`
   - On exception, print clear error message explaining what went wrong, include the actual exception message, and `sys.exit(1)` (no fallback)
   - Keep all existing interactive flow:
     - Display search results
     - Get user selection
     - Fetch details
     - Save file
     - Update lookup

4. **Remove Duplicate Code**
   - Delete all functions that were moved to `usda_lib.py`
   - Delete constants that were moved
   - Keep only CLI-specific code

5. **Update Error Handling**
   - Replace `sys.exit()` calls in library functions with exception handling in `main()`
   - When catching exceptions:
     - **No fallback behavior**: Exceptions should never be silently caught and ignored
     - **Clear error messages**: Print a clear message explaining what operation failed and why
     - **Include actual error**: Always include the actual exception message (e.g., `str(e)` or `e.args[0]`)
     - **Exit on error**: After printing error, call `sys.exit(1)` (no fallback)
   - Catch `requests.RequestException`:
     - Print clear message about API request failure
     - Include the actual exception message
     - Exit with code 1
   - Catch `OSError` from file operations:
     - Print clear message about file operation failure
     - Include the actual exception message
     - Exit with code 1
   - Catch `usda_lib.UsdaApiKeyError`:
     - Print clear message about missing API key
     - Include the actual exception message (which should contain setup instructions)
     - Exit with code 1

### Success Criteria

- `usda_lookup.py` imports from `usda_lib.py`
- Interactive CLI behavior unchanged
- No duplicate code between files
- All error handling properly catches exceptions from library

---

## Phase 6: Create MCP Server

### Tasks

1. **Install MCP Python SDK**
   - Activate the `meal_planner` virtualenv: `workon meal_planner`
   - **CRITICAL**: Confirm you're in the virtualenv before proceeding:
     - Check that the prompt shows `(meal_planner)` or verify with `which python3` points to the virtualenv
     - If you cannot confirm you're in the `meal_planner` virtualenv, terminate all work immediately and report the issue
   - Install MCP package: `pip install mcp`
   - Verify installation works

2. **Create MCP Server Script**
   - Create new file `nutrition/scripts/usda_mcp_server.py`
   - Import FastMCP and usda_lib:
     ```python
     from typing import Any
     from mcp.server import fastmcp
     import usda_lib
     import json
     ```
   - Initialize FastMCP server:
     ```python
     mcp = fastmcp.FastMCP("USDA Ingredient Lookup")
     ```
   - Create helper function to convert dicts to JSON strings:
     ```python
     def _dict_to_json_string(d: dict[str, Any]) -> str:
         """Convert a dictionary to a JSON string."""
         return json.dumps(d)
     ```

3. **Define MCP Tools**
   - Use `@mcp.tool()` decorator for each tool function
   - All tools should be `async` functions that return JSON strings
   - Error handling: Return structured dicts with `status`, `stdout`, `stderr` keys, then convert to JSON string
   
   - Create tool: `search_ingredient`
     - Decorator: `@mcp.tool(description="Search for ingredients in USDA FoodData Central database")`
     - Function signature: `async def search_ingredient(query: str) -> str:`
     - Parameters:
       - `query` (string, required): Search term for ingredient name
     - Returns: JSON string containing list of matching foods with FDC IDs, descriptions, and data types
     - Implementation:
       - Get API key: `api_key = usda_lib.get_api_key()` (will raise `UsdaApiKeyError` if missing)
       - Wrap in try/except
       - Call `usda_lib.search_ingredient_prioritized(query, api_key)`
       - Format results as dict with `status: "success"`, `stdout: ""`, `stderr: ""`, and food list in result
       - On exception: Return dict with `status: "failure"`, `stdout: ""`, `stderr: str(exception)`
       - Convert dict to JSON string using `_dict_to_json_string()`
   
   - Create tool: `get_ingredient_details`
     - Decorator: `@mcp.tool(description="Get full details for a specific ingredient by FDC ID")`
     - Function signature: `async def get_ingredient_details(fdc_id: int) -> str:`
     - Parameters:
       - `fdc_id` (integer, required): FoodData Central ID
     - Returns: JSON string containing full ingredient data including nutrition facts
     - Implementation:
       - Get API key: `api_key = usda_lib.get_api_key()` (will raise `UsdaApiKeyError` if missing)
       - Wrap in try/except
       - Call `usda_lib.get_food_details(fdc_id, api_key)`
       - Format as dict with `status: "success"`, `stdout: ""`, `stderr: ""`, and food data in result
       - On exception: Return dict with `status: "failure"`, `stdout: ""`, `stderr: str(exception)`
       - Convert dict to JSON string using `_dict_to_json_string()`
   
   - Create tool: `save_ingredient`
     - Decorator: `@mcp.tool(description="Save ingredient data to local file and update lookup database")`
     - Function signature: `async def save_ingredient(fdc_id: int, description: str = "") -> str:`
     - Parameters:
       - `fdc_id` (integer, required): FoodData Central ID
       - `description` (string, optional): Ingredient description (extracted from data if not provided)
     - Returns: JSON string with success message and file path
     - Implementation:
       - Get API key: `api_key = usda_lib.get_api_key()` (will raise `UsdaApiKeyError` if missing)
       - Wrap in try/except
       - Call `usda_lib.get_food_details(fdc_id, api_key)` to get data
       - Extract description from data if not provided
       - Call `usda_lib.save_ingredient_file()` and `usda_lib.update_reverse_lookup()`
       - Format as dict with `status: "success"`, `stdout: ""`, `stderr: ""`, and file path in result
       - On exception: Return dict with `status: "failure"`, `stdout: ""`, `stderr: str(exception)`
       - Convert dict to JSON string using `_dict_to_json_string()`

4. **Implement Server Entry Point**
   - At the bottom of the file, add:
     ```python
     if __name__ == "__main__":
         mcp.run(transport="stdio")
     ```
   - FastMCP automatically registers all `@mcp.tool()` decorated functions
   - No manual server instance creation or tool registration needed
   - Handle exceptions in tool handlers (as specified in step 3):
     - **No fallback behavior**: Exceptions should never be silently caught and ignored
     - **Clear error messages**: Return clear error messages explaining what operation failed and why
     - **Include actual error**: Always include the actual exception message in the error response
     - **Don't crash server**: Return error responses (as JSON strings) instead of raising exceptions

5. **Make Script Executable**
   - Add shebang: `#!/usr/bin/env python3`
   - Ask the user to make the script executable: `chmod +x nutrition/scripts/usda_mcp_server.py`

6. **Configure Cursor on macOS**
   - Ask the user to configure Cursor:
     - Open Cursor Settings (gear icon in upper right)
     - Navigate to: Settings > Features > MCP (or Tools & Integrations > MCP Tools)
     - Click "Add Custom MCP" or "+ Add New MCP Server"
     - Add configuration to `mcp.json`:
       ```json
       {
         "mcpServers": {
           "usda-lookup": {
             "command": "python3",
             "args": [
               "/absolute/path/to/nutrition/scripts/usda_mcp_server.py"
             ],
             "env": {
               "USDA_API_KEY": "${USDA_API_KEY}"
             }
           }
         }
       }
       ```
     - Replace `/absolute/path/to/` with actual absolute path to project root
     - Use `${USDA_API_KEY}` to reference environment variable (Cursor will expand it)
     - Save configuration
     - Restart Cursor

7. **Test MCP Server Integration**
   - After restarting Cursor, verify server appears in MCP servers list
   - Use Cursor's Composer to test:
     - Search for an ingredient: "Search for milk in USDA database"
     - Get ingredient details: "Get details for FDC ID 2705385"
     - Save an ingredient: "Save ingredient with FDC ID 2705385"
   - Verify tools are available and return correct results
   - Verify ingredient files are saved correctly
   - Verify lookup database is updated

### Success Criteria

- MCP server script exists and is executable
- Server exposes all three tools (search, get details, save)
- Tools return properly formatted JSON responses
- Cursor configuration file is set up correctly
- Server appears in Cursor's MCP servers list after restart
- All tools work correctly when called from Cursor
- Ingredient files are saved to correct location
- Lookup database is updated correctly

### Notes

- **FastMCP Pattern**: Use `fastmcp.FastMCP` instead of regular `Server` class. FastMCP automatically registers all `@mcp.tool()` decorated functions, making the code simpler.

- **Tool Functions**: All tools should be `async` functions decorated with `@mcp.tool()` that return JSON strings. Use the `_dict_to_json_string()` helper to convert structured dicts to JSON.

- **Response Format**: All tool responses should follow the pattern from `example_mcp_server.py`:
  - Success: `{"status": "success", "stdout": "", "stderr": "", ...other data...}`
  - Failure: `{"status": "failure", "stdout": "", "stderr": "error message"}`
  - Convert to JSON string before returning

- **Server Transport**: Use `stdio` transport (standard input/output) as it's the most common for command-line servers. Call `mcp.run(transport="stdio")` in the `if __name__ == "__main__"` block.

- **Error Handling**: MCP tools should catch exceptions and return error messages in a structured format:
  - **No fallback**: Never silently catch and ignore exceptions
  - **Clear messages**: Return clear error messages explaining what operation failed and why
  - **Include actual error**: Always include the actual exception message in the error response
  - **Don't crash server**: Return error responses (as JSON strings) instead of raising exceptions that crash the server
- **Environment Variables**: The `env` section in `mcp.json` allows passing environment variables to the server process
- **Path Requirements**: Use absolute paths in Cursor configuration to avoid path resolution issues
- **API Key**: The server will use the `USDA_API_KEY` environment variable, which should already be set in the user's shell

---

## Notes

- **Logger Removal**: Replace all `logger.info()`, `logger.warning()`, `logger.error()` with `print()` statements. Remove logging configuration entirely.

- **Print Statements**: Use `print()` for informational output that helps understand what's happening. Don't use `print()` for user prompts or instructions (those stay in CLI).

- **Exception Handling**: 
  - Library functions should raise exceptions (never catch and ignore)
  - CLI script should catch exceptions and handle them:
    - **No fallback**: Never silently catch and continue
    - **Clear messages**: Print clear error messages explaining what went wrong
    - **Include actual error**: Always include the actual exception message
    - **Exit on error**: Exit with appropriate code after printing error
  - MCP server should catch exceptions in tool handlers and return error responses (don't crash server)

- **Public vs Private Functions**: Follow Google Python Style Guide best practices. Functions that are used across files/modules should be public (no `_` prefix). Only mark functions as private if they are truly internal implementation details that won't be used outside the module. Path helpers and utility functions that might be useful to other modules should be public.

- **MCP Server**: Phase 6 creates an MCP server that imports `usda_lib` and exposes tools for AI agents to use programmatically. This enables Cursor (and other MCP-compatible tools) to interact with the USDA lookup functionality without needing to parse CLI output.

