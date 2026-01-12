# Mobile Workout Tracker Implementation Plan

This document outlines the step-by-step phases for implementing a lightweight mobile workout tracker that allows recording workout data from a phone browser and committing it directly to GitHub.

## Overview

The system will enable recording actual workout performance data (sets achieved, reps achieved, weight used, bodyweight) from a mobile browser. Data will be stored as JSON files in a `workout_logs/` directory and committed to GitHub via the GitHub REST API. No server infrastructure is required - just a static HTML form hosted on GitHub Pages.

**Important: The UI does not need to be impressive or polished.** This is a simple form filler - functional and usable is the goal. Focus on making it easy to enter data quickly, not on making it look fancy. Basic HTML form elements, minimal styling, and straightforward functionality are perfectly acceptable.

## Phase 0: Prove Out End-to-End (MVP)

### Goal:
Create an absolute bare-minimum proof-of-concept to validate the entire workflow works before building the full system.

### Tasks:
1. **Set up local development server**
   - Create `fitness/web/` directory
   - Instructions: Run `python3 -m http.server 8000` from `fitness/web/` directory
   - Find computer's IP address on local network (e.g., `ifconfig` on Mac/Linux, `ipconfig` on Windows)
   - Access from phone: `http://<ip-address>:8000/mvp.html`
   - Both devices must be on same Wi-Fi network

2. **Set up GitHub Personal Access Token (PAT)**
   - Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a name (e.g., "Workout Tracker MVP")
   - Select scope: `repo` (full control of private repositories)
   - Generate token and copy it immediately (you won't see it again)
   - Save it somewhere safe temporarily

3. **Get PAT onto phone (choose easiest method for you)**
   
   **Option A: Email it to yourself (Easiest)**
   - Copy the PAT token from GitHub
   - Open your email (Gmail, Outlook, etc.) on your computer
   - Compose new email to yourself
   - Paste PAT in the email body (subject: "GitHub PAT for testing")
   - Send email
   - Open email app on phone
   - Open the email you just sent
   - Long-press on the PAT token → Select All → Copy
   - Paste into the form on phone
   
   **Option B: AirDrop (Mac + iPhone - Very Easy)**
   - Copy the PAT token from GitHub
   - Open Notes app on Mac
   - Create new note, paste PAT
   - Right-click note → Share → AirDrop
   - Select your iPhone
   - On iPhone: Open Notes app, find the note
   - Long-press PAT → Copy
   - Paste into the form
   
   **Option C: iMessage/Text Message (Mac + iPhone)**
   - Copy the PAT token from GitHub
   - Open Messages app on Mac
   - Send message to yourself (your own phone number)
   - Paste PAT in message, send
   - On iPhone: Open Messages, find your message
   - Long-press PAT → Copy
   - Paste into the form
   
   **Option D: Cloud Notes App (Works cross-platform)**
   - Copy the PAT token from GitHub
   - Open Notes app (iCloud), Google Keep, or similar cloud note app on computer
   - Create new note, paste PAT
   - Open same app on phone
   - Note should sync automatically
   - Long-press PAT → Copy
   - Paste into the form
   
   **Option E: Password Manager (If you use one)**
   - Copy the PAT token from GitHub
   - Open password manager (1Password, LastPass, Bitwarden, etc.) on computer
   - Create new login/item: Name it "GitHub PAT MVP", paste token as password
   - Open password manager app on phone
   - Find the item, copy the password/token
   - Paste into the form
   
   **Option F: Manual typing (Last resort - annoying but works)**
   - Have GitHub PAT page open on computer
   - Open form on phone
   - Carefully type PAT character by character
   - Double-check for typos before submitting
   
   **Recommendation:** Use Option A (email) or Option B (AirDrop if Mac+iPhone) - they're the fastest and least error-prone.

4. **Create minimal HTML form (`fitness/web/mvp.html`)**
   - Single text input field (for string)
   - Single number input field (for integer)
   - PAT token input field
   - Submit button
   - Absolute minimum - no styling needed

5. **Add minimal JavaScript**
   - Collect form data: `{string: "...", integer: ...}`
   - Get PAT from input field
   - Convert to JSON
   - Generate branch name from timestamp (e.g., `mvp-test-<timestamp>`)
   - Call GitHub API to create file on new branch
   - Use GitHub REST API: `PUT /repos/{owner}/{repo}/contents/{path}`
   - File path: `fitness/mvp_test/{timestamp}_test.json`
   - Show success/error message

6. **Test end-to-end**
   - Start local server: `python3 -m http.server 8000` from `fitness/web/`
   - Open `http://<ip-address>:8000/mvp.html` on phone
   - Enter PAT token in form
   - Enter a string and integer (e.g., "test" and 123)
   - Submit form
   - Verify on GitHub (laptop/browser): new branch created with the data file
   - Confirm the workflow works before proceeding

### Deliverables:
- `fitness/web/mvp.html` - Minimal proof-of-concept form
- Local development server running and accessible from phone
- PAT token set up and accessible on phone
- Can submit string:integer data from phone
- Data appears as new branch on GitHub
- Validates the core concept works

**Note:** This is a throwaway MVP to prove the concept. Once validated, proceed to Phase 1+ to build the real system.

---

## Phase 1: Workout Log Schema Definition

### Tasks:
1. **Create `workout_log_schema.json`**
   - Create `fitness/schemas/workout_log_schema.json` with JSON Schema specification
   - Define structure:
     - `date` (string, datetime format YYYY-MM-DD-<unix epoch seconds>, required)
     - `session_name` (string, required) - References a session file in `sessions/` directory
     - `bodyweight_lb` (number, required) - Bodyweight in pounds (flat structure, not nested)
     - `exercises` (array, required) - List of exercises performed:
       - `exercise_name` (string, required) - References an exercise file in `exercises/` directory
       - `sets` (array, required) - Array of sets performed:
         - `reps` (integer, required) - Number of reps completed
         - `lb` (number, required) - Weight used in pounds

2. **Create `workout_logs/` directory**
   - Create `fitness/workout_logs/` directory for storing workout log files
   - Filename format: `YYYY-MM-DD-<unix epoch seconds>_workout.json`

### Deliverables:
- `fitness/schemas/workout_log_schema.json` - Workout log schema file
- `fitness/workout_logs/` directory created
- Schema defines workout log structure

---

## Phase 2: Validation Script for Workout Logs

### Tasks:
1. **Create `fitness/scripts/validate_workout_log.py`**
   - Create validation script for workout log files
   - When run as a script, validates ALL workout log files in `fitness/workout_logs/` directory
   - Structure the script with free functions and a `main()` dispatcher
   - Validation checks:
     - Schema validation using `workout_log_schema.json`
     - Verify `session_name` references exist in `sessions/` directory
     - Verify `exercise_name` references exist in `exercises/` directory
     - Validate datetime format (YYYY-MM-DD-<unix epoch seconds>)
     - Validate numeric ranges:
       - `bodyweight_lb` > 0
       - `lb` (weight) >= 0 for each set (allows 0 for skipped sets)
       - `reps` >= 0 for each set (allows 0 for skipped sets)
   - Use `print` statements (no logging)
   - Raise hard exceptions (no defaults or fallbacks)

2. **Test validation script**
   - Create a sample workout log file
   - Run validation script to ensure it works correctly
   - Test with invalid data to ensure errors are caught

### Deliverables:
- `fitness/scripts/validate_workout_log.py` - Validation script for workout logs
- Script validates all files in `workout_logs/` directory when run
- Validation includes schema validation and reference checking

---

## Phase 3: GitHub API Helper Functions

### Tasks:
1. **Create `fitness/scripts/github_api_utils.py`**
   - Create utility module for GitHub API operations
   - Functions:
     - `get_repo_info(token: str, repo: str) -> dict` - Get repository information (including default branch)
     - `get_branch_sha(token: str, repo: str, branch: str) -> str` - Get SHA of a branch's HEAD commit
     - `create_branch(token: str, repo: str, branch_name: str, base_branch_sha: str) -> None` - Create a new branch from a base branch SHA (required before creating files on new branch)
     - `get_file_content(token: str, repo: str, path: str, branch: str = None) -> dict` - Get file content from GitHub
     - `create_or_update_file(token: str, repo: str, path: str, content: str, message: str, branch: str, sha: str | None = None) -> dict` - Create or update file via GitHub API. **Important:** Branch must already exist (use `create_branch` first). If updating existing file, provide `sha` parameter.
   - Handle API errors gracefully (raise hard exceptions with clear messages)
   - Include proper type hints and docstrings
   - Use `requests` library for HTTP calls
   - Handle authentication via PAT token
   - **Note:** GitHub does NOT automatically create branches when creating files. You must create the branch first using `create_branch()`, then create the file on that branch.

2. **Add error handling**
   - Handle 401 (unauthorized) errors
   - Handle 404 (not found) errors
   - Handle 422 (validation) errors - including "branch already exists" (which is okay)
   - Provide clear error messages for each case

### Deliverables:
- `fitness/scripts/github_api_utils.py` - GitHub API utility module
- Functions handle branch creation and file creation/updates via GitHub REST API
- Proper error handling with clear messages
- Branch creation pattern matches MVP implementation

---

## Phase 4: HTML Form Structure and UI

### Tasks:
1. **Create `fitness/web/index.html`**
   - Create a simple, functional HTML form - no fancy styling needed
   - Structure:
     - Settings section (collapsible) for GitHub PAT entry
     - Routine/Session selector dropdown
     - Bodyweight input field
     - Dynamic exercise list (populated from selected session)
     - For each exercise:
       - Exercise name display
       - Number of sets from session schema (fixed, not dynamic)
       - For each set: reps input, weight input
     - Submit button
   - Keep it simple:
     - Basic HTML form elements (no need for fancy components)
     - Minimal CSS - just enough to make it usable on mobile
     - Large enough touch targets for mobile (basic requirement)
     - Readable text (default browser font is fine)
   - Use semantic HTML5 elements
   - Avoid complex styling, animations, or visual flourishes

2. **Add basic form validation script**
   - Create `fitness/web/form.js` with basic form validation
   - Basic client-side validation before submission
   - Required field checking
   - Numeric validation (positive numbers only)
   - Simple error messages (plain text is fine)
   - Settings toggle functionality
   - localStorage integration for PAT token (save/load)

### Deliverables:
- `fitness/web/index.html` - Simple, functional HTML form
- `fitness/web/form.js` - Basic form validation and settings management
- Form includes all necessary input fields
- Works on mobile browsers (basic usability)
- Basic client-side validation

---

## Phase 5: JavaScript for Form Logic

### Tasks:
1. **Create modular JavaScript files** (organized into separate files for maintainability)
   - `fitness/web/logging.js` - Logging functionality (replicates MVP pattern)
     - `log(message)` - Appends timestamped messages to logs section and console
   - `fitness/web/date_utils.js` - Date/time utilities
     - `getCurrentDatetime()` - Generate current datetime in format: `YYYY-MM-DD-<unix epoch seconds>`
   - `fitness/web/token_storage.js` - localStorage token management
     - `saveToken(token)` - Save PAT to localStorage
     - `loadToken()` - Load PAT from localStorage
     - `clearToken()` - Clear PAT from localStorage
   - `fitness/web/data_loader.js` - Data loading from embedded_data.js
     - `loadRoutines()` - Load routines from embedded_data.js
     - `loadSession(sessionName)` - Load session data from embedded_data.js
     - `getExerciseName(exerciseName)` - Get human-readable exercise name
   - `fitness/web/form_generator.js` - Dynamic form generation
     - `populateExerciseForm(sessionData)` - Dynamically create exercise input fields based on session schema (number of sets comes from session, not user-configurable)
     - Helper functions for creating exercise and set elements
   - `fitness/web/form_collector.js` - Form data collection
     - `collectFormData()` - Collect all form data into workout log JSON structure
     - Helper functions for collecting session, bodyweight, and exercise data
   - `fitness/web/form_validator.js` - Form data validation
     - `validateFormData(data)` - Validate collected data before submission
     - Helper functions for validating each data field
   - `fitness/web/form.js` - Main form initialization and event handlers
     - `initializeForm()` - Initialize form on page load
     - Form state management (show/hide settings, update exercise form on session change)
     - Form submission handler

2. **Update `fitness/web/index.html`**
   - Add script tags for all JavaScript modules (in correct dependency order)
   - Logs section already added in Phase 4

3. **Logging functionality (replicate MVP pattern)**
   - Log all major operations:
     - Form submission start
     - Data collection steps
     - API calls (URLs, status codes, responses) - will be added in Phase 6
     - Branch creation steps - will be added in Phase 6
     - File creation steps - will be added in Phase 6
     - Success/error states
   - This logging proved invaluable in MVP for debugging - replicate the pattern

### Deliverables:
- Modular JavaScript files for form logic and data collection
- localStorage integration for PAT token
- Dynamic form generation based on session data
- Form validation and data collection
- Comprehensive logging system matching MVP implementation
- Well-organized code structure for maintainability

---

## Phase 6: GitHub API Integration

### Tasks:
1. **Add GitHub API commit functionality**
   - Function: `commitWorkoutLog(token, workoutData) -> Promise`
     - Generate filename: `YYYY-MM-DD-<unix epoch seconds>_workout.json`
     - Convert workout data to JSON string
     - Generate branch name from timestamp (e.g., `workout-YYYY-MM-DD-<unix epoch seconds>`)
     - **Important:** Follow MVP pattern for branch creation:
       1. Get default branch name using `getDefaultBranch()` (replicate MVP `getDefaultBranch` function)
       2. Get default branch SHA using `getBranchSha()` (replicate MVP `getBranchSha` function)
       3. Create new branch using `createBranch()` (replicate MVP `createBranch` function)
       4. Create file on new branch using `createFile()` (replicate MVP `createFile` function)
     - **GitHub does NOT automatically create branches** - you must create the branch first, then create the file
     - Handle API response and errors
   - Note: Session and routine data is loaded from embedded_data.js (no API calls needed for reading)
   - Use `fetch()` API for HTTP requests
   - CORS works correctly from GitHub Pages (validated in MVP)

2. **Add error handling and user feedback**
   - Display success message after successful commit
   - Display error messages for API failures
   - Show loading states during API calls
   - Handle network errors gracefully
   - Log all API operations to the logs section (replicate MVP logging pattern)

### Deliverables:
- GitHub API integration functions
- Branch creation and file creation via GitHub REST API (following MVP pattern)
- Error handling and user feedback
- Loading states and success/error messages
- Comprehensive logging of all API operations

---

## Phase 7: Embedded Data Generation

### Tasks:
1. **Create `fitness/scripts/generate_embedded_data.py`**
   - Script that reads all routines from `fitness/routines/` directory
   - Reads all sessions from `fitness/sessions/` directory
   - Reads all exercises from `fitness/exercises/` directory
   - Generates JavaScript object with all this data
   - Outputs to `fitness/web/embedded_data.js` as a separate file (for clean git diffs)
   - Format: `const ROUTINES = {...}; const SESSIONS = {...}; const EXERCISES = {...};`

2. **Update HTML to load embedded data**
   - Add `<script src="embedded_data.js"></script>` to `fitness/web/index.html`
   - Form will read from these JavaScript objects instead of making API calls

3. **Create `fitness/scripts/validate_html_up_to_date.py`**
   - Validation script that checks if `embedded_data.js` is up-to-date
   - Compares current JSON files (routines/sessions/exercises) with what's in `embedded_data.js`
   - Raises hard exception with clear error message if data is out of sync
   - Can be run manually when needed (no automatic enforcement)
   - Use `print` statements (no logging)
   - Raise hard exceptions (no defaults or fallbacks)

4. **Manual regeneration workflow**
   - When routines/sessions/exercises change, manually run `generate_embedded_data.py`
   - Script updates `embedded_data.js` file
   - Optionally run `validate_html_up_to_date.py` to verify it's correct
   - Commit both the JSON changes and updated `embedded_data.js`
   - No automatic validation/up-to-date checking needed for now

### Deliverables:
- `fitness/scripts/generate_embedded_data.py` - Script to generate embedded data
- `fitness/scripts/validate_html_up_to_date.py` - Script to validate embedded data is current
- `fitness/web/embedded_data.js` - JavaScript file with all routines/sessions/exercises
- HTML form loads data from embedded JavaScript objects
- No API calls needed for reading routine/session data

---

## Phase 8: Local Development Server Setup

### Tasks:
1. **Set up local development server for quick iteration**
   - Simple instructions for running local server:
     - Python: `python3 -m http.server 8000` (from `fitness/web/` directory)
     - Uses Python's built-in HTTP server (no additional dependencies needed)
     - **Note:** Server does NOT need to be restarted when files change - just refresh browser
   - Document how to access:
     - **From laptop:** `http://localhost:8000/index.html` (or just `http://localhost:8000/` if index.html is default)
     - **From phone:** Find computer's IP address on local network, then access `http://<ip-address>:8000/index.html`
     - Both devices must be on same Wi-Fi network
   - **Recommendation:** Test locally on laptop first (faster iteration), then test on phone via local network or GitHub Pages

2. **Add development instructions**
   - Create `fitness/web/DEVELOPMENT.md` with:
     - How to start local server
     - How to access from laptop vs phone
     - Quick iteration workflow (edit → refresh browser → test)
     - When to use local server vs GitHub Pages

### Deliverables:
- Local development server setup documented
- Can quickly test changes locally before deploying
- Form accessible from laptop and phone on local network
- Development workflow validated (matches MVP workflow)

---

## Phase 9: GitHub Pages Setup (Production Deployment)

### Tasks:
1. **Configure GitHub Pages**
   - Enable GitHub Pages in repository settings
   - Go to Settings → Pages
   - Under "Source", select "Deploy from a branch"
   - Select your branch (e.g., `brandon/form_for_phone` or merge to `main` first)
   - Select `/ (root)` as the folder (GitHub Pages only offers root/ or docs/)
   - Click Save
   - **Note:** Even though you select "root", files in `fitness/web/` will be accessible at `https://<username>.github.io/<repo>/fitness/web/index.html`
   - Wait 1-2 minutes for GitHub Pages to build and deploy
   - Verify site is accessible at the expected URL

2. **Update HTML for GitHub Pages**
   - Ensure all paths are relative (already done if using relative paths like `embedded_data.js`)
   - Test that form works when hosted on GitHub Pages
   - Verify CORS works correctly (GitHub API allows requests from GitHub Pages - validated in MVP)

3. **Add README for setup instructions**
   - Create `fitness/web/README.md` with:
     - Instructions for generating GitHub PAT
     - How to use the form (both local dev and production)
     - GitHub Pages URL format
     - Troubleshooting tips

### Deliverables:
- GitHub Pages site is live and accessible
- Form works correctly when hosted
- Setup documentation for users
- Can use GitHub Pages URL for real workouts, local server for quick testing
- Deployment process validated (matches MVP deployment)

---

## Phase 10: Testing and Refinement

### Tasks:
1. **Test on mobile device**
   - Test via local development server first (quick iteration)
   - Test via GitHub Pages (production deployment)
   - Open form on actual phone browser
   - Test form entry and submission
   - Verify data is committed correctly to GitHub
   - Test with different sessions and exercises
   - Test error scenarios (invalid token, network failure, etc.)

2. **Fix any critical usability issues**
   - Fix any bugs that prevent data entry
   - Ensure form is functional (not necessarily pretty)
   - Make sure error messages are clear enough to understand
   - Only fix things that actually break functionality

3. **Add minimal convenience features (only if truly helpful)**
   - Remember last used session (simple localStorage)
   - Pre-fill bodyweight from last entry (optional, simple)
   - Skip fancy features - keep it simple

### Deliverables:
- Form tested and working on mobile devices
- Critical bugs fixed
- Minimal convenience features (only if they significantly help)

---

## Phase 11: Documentation and Maintenance

### Tasks:
1. **Create user documentation**
   - Write `fitness/web/USER_GUIDE.md`:
     - How to generate a GitHub PAT
     - How to enter the PAT in the form
     - How to record a workout
     - How to verify data was saved
     - Troubleshooting common issues

2. **Create developer documentation**
   - Document the GitHub API integration approach
   - Document the data structure
   - Document how to update the form if schema changes
   - Document how to add new features

3. **Add maintenance notes**
   - Document PAT expiration handling
   - Document how to regenerate embedded_data.js when routines/sessions change (run `generate_embedded_data.py`)
   - Document version compatibility

### Deliverables:
- User guide for end users
- Developer documentation
- Maintenance notes

---

## Technical Notes

- **GitHub API Authentication**: Uses Personal Access Token (PAT) stored in browser localStorage
- **File Storage**: Workout logs stored in `fitness/workout_logs/` directory with format `YYYY-MM-DD-<unix epoch seconds>_workout.json`
- **Data Format**: JSON files matching `workout_log_schema.json` (uses flat `bodyweight_lb` field, not nested object)
- **JavaScript Structure**: Modular design with separate files:
  - `logging.js` - Logging functionality
  - `date_utils.js` - Date/time utilities
  - `token_storage.js` - localStorage token management
  - `data_loader.js` - Data loading from embedded_data.js
  - `form_generator.js` - Dynamic form generation
  - `form_collector.js` - Form data collection
  - `form_validator.js` - Form data validation
  - `form.js` - Main form initialization and event handlers
- **Hosting**: 
  - **Local Development**: Use Python's built-in HTTP server (`python3 -m http.server 8000` from `fitness/web/` directory) for quick iteration. No need to restart server when files change - just refresh browser.
  - **Production**: Static HTML form hosted on GitHub Pages (free, no server required) for real-world use. Access at `https://<username>.github.io/<repo>/fitness/web/index.html` when deployed from root.
- **CORS**: GitHub API supports CORS for GitHub Pages origins (validated in MVP)
- **Error Handling**: All errors raise hard exceptions with clear messages (no defaults or fallbacks)
- **Mobile Optimization**: Form designed for basic mobile usability - large enough touch targets, readable text. No fancy UI needed - simple form filler is the goal.
- **Validation**: Both client-side (JavaScript) and server-side (Python validation script) validation
- **Security**: PAT stored in localStorage (acceptable risk for personal tool, mitigated by phone security)
- **Logging**: Comprehensive logging system on the page (replicate MVP pattern) - logs all operations with timestamps, very helpful for debugging
- **Branch Creation**: **Critical:** GitHub does NOT automatically create branches when creating files. You must:
  1. Get default branch name
  2. Get default branch SHA
  3. Create new branch from that SHA
  4. Then create file on the new branch
  This pattern was validated in MVP and must be replicated in all GitHub API operations.
- **Language**: Use JavaScript (not TypeScript) for simplicity - validated in MVP as sufficient for this project

---

## Future Enhancements (Optional - Only if Actually Needed)

These are optional features that could be added later if they prove useful. Don't implement these unless there's a clear need:
- Add dynamic sets functionality (allow adding/removing sets per exercise, not just using session schema)
- Add workout history viewing (fetch and display past workouts)
- Add progress tracking (compare workouts over time)
- Add export functionality (download workout data as CSV/JSON)
- Add offline support (store workouts locally, sync when online)
- Add exercise search/autocomplete
- Add weight/rep suggestions based on previous workouts
- Add rest timer between sets
- Add workout templates/pre-sets

## Security Enhancements (Optional - Only if Needed)

These are optional security improvements that could be added if token storage security becomes a concern:
- **Encrypted localStorage**: Encrypt PAT token before storing in localStorage, decrypt on load. Note: Encryption key must be stored somewhere (often defeats the purpose), adds complexity, and still vulnerable if key is accessible.
- **Browser Password Manager**: Use browser's native password manager for PAT token storage. Pros: Uses browser's secure storage, can sync across devices. Cons: Requires JavaScript to read it back (not always reliable), browser-dependent behavior, may not auto-fill reliably.
- **Hybrid: Encrypted + user-provided key**: User provides a passphrase, encrypt token with it before storing. Pros: Token encrypted with user secret, persists across sessions, more secure than plain localStorage. Cons: User must remember/enter passphrase each time, adds complexity, still vulnerable if passphrase is compromised.

**Note:** Current localStorage approach is acceptable for personal tool use case. These enhancements add complexity and may not provide significant security benefit for a single-user personal application.

**Remember: Keep it simple. A basic form that works is better than a fancy form that's hard to maintain.**
