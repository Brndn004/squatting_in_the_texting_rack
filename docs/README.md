# Workout Tracker Setup Guide

This guide explains how to set up and use the Workout Tracker form for recording workouts from your mobile device.

## Quick Start

1. **Set up GitHub Pages** - See "GitHub Pages Setup" section below
2. **Generate a GitHub Personal Access Token (PAT)** - See instructions below
3. **Open the form** on GitHub Pages: `https://brndn004.github.io/squatting_in_the_texting_rack/index.html`
4. **Enter your PAT token** in the Settings section
5. **Record your workout** - Select session, enter bodyweight, fill in exercises
6. **Submit** - Your workout data will be saved to GitHub automatically

## GitHub Pages Setup

Before you can use the form, you need to enable GitHub Pages:

1. Go to your repository: `https://github.com/Brndn004/squatting_in_the_texting_rack`
2. Click **Settings** tab (top navigation)
3. Click **Pages** in the left sidebar
4. Under **Source**, select **"Deploy from a branch"**
5. Select your branch (e.g., `main` or your feature branch)
6. Select **`/docs`** as the folder
7. Click **Save**
8. Wait 1-2 minutes for GitHub Pages to deploy

After deployment, your form will be accessible at:
```
https://brndn004.github.io/squatting_in_the_texting_rack/index.html
```

## Generating a GitHub Personal Access Token (PAT)

A Personal Access Token is required to authenticate with GitHub's API and save your workout data.

### Steps:

1. **Go to GitHub.com** and sign in to your account
2. **Navigate to Settings:**
   - Click your profile picture (top right)
   - Click "Settings"
3. **Go to Developer settings:**
   - Scroll down in the left sidebar
   - Click "Developer settings"
4. **Go to Personal access tokens:**
   - Click "Personal access tokens"
   - Click "Tokens (classic)"
5. **Generate new token:**
   - Click "Generate new token (classic)"
   - Give it a name (e.g., "Workout Tracker")
   - Select expiration (recommend 90 days or "No expiration" for convenience)
   - **Select scope:** Check `repo` (Full control of private repositories)
     - This gives the token permission to create branches and files in your repository
   - Click "Generate token" at the bottom
6. **Copy the token immediately:**
   - GitHub will show your token once
   - Copy it and save it somewhere safe
   - **Important:** You won't be able to see it again after leaving this page

### Security Notes:

- **Keep your token private** - Don't share it or commit it to version control
- **Token expiration** - If your token expires, you'll need to generate a new one
- **Revoking tokens** - You can revoke tokens anytime in GitHub Settings → Developer settings → Personal access tokens

## Using the Form

### Local Development (For Testing)

If you want to test changes locally before deploying:

1. **Start local server:**
   ```bash
   cd docs
   python3 -m http.server 8000
   ```

2. **Access from laptop:**
   - Open `http://localhost:8000/index.html`

3. **Access from phone:**
   - Find your computer's IP address (`ifconfig` on Mac/Linux, `ipconfig` on Windows)
   - Open `http://<ip-address>:8000/index.html` on your phone
   - Both devices must be on the same Wi-Fi network

See `docs/DEVELOPMENT.md` for more details on local development.

### Production (GitHub Pages)

The form is hosted on GitHub Pages for production use:

**URL:** `https://brndn004.github.io/squatting_in_the_texting_rack/index.html`

1. **Open the URL** in your mobile browser
2. **Enter your PAT token** in the Settings section (click "Show Settings")
3. **Select a session** from the dropdown
4. **Enter your bodyweight** in pounds
5. **Fill in exercise data:**
   - For each exercise, enter reps and weight for each set
   - Sets are pre-defined by the session (you can't add/remove sets)
6. **Click "Submit Workout"**
7. **Wait for confirmation** - You'll see a success message when the workout is saved

### Token Storage

- Your PAT token is saved in your browser's localStorage
- It persists across browser sessions
- You only need to enter it once (unless you clear browser data)
- The token is stored locally on your device (not sent anywhere except GitHub API)


## Troubleshooting

### Form won't load
- **Check URL** - Make sure you're using the correct GitHub Pages URL
- **Check GitHub Pages** - Verify GitHub Pages is enabled in repository settings
- **Wait a few minutes** - After enabling GitHub Pages, it may take 1-2 minutes to deploy

### "Unauthorized" error when submitting
- **Check token** - Verify your PAT token is correct and not expired
- **Check token permissions** - Token must have `repo` scope
- **Regenerate token** - If unsure, generate a new token and try again

### "Repository not found" error
- **Check repository name** - Verify the repository exists and is accessible
- **Check token permissions** - Token must have access to the repository

### Network errors
- **Check internet connection** - Form requires internet to submit data
- **Check CORS** - GitHub API supports CORS from GitHub Pages (should work automatically)
- **Try again** - Network issues are usually temporary

### Can't see logs
- **Click "Show Logs"** - Logs section may be hidden by default
- **Check browser console** - Open browser developer tools (F12) to see detailed logs

### Data not appearing on GitHub
- **Check branch** - Workout data is saved to a new branch (format: `workout-YYYY-MM-DD-<timestamp>`)
- **Check file path** - Files are saved to `fitness/workout_logs/` directory
- **Check filename** - Format: `YYYY-MM-DD-<unix epoch seconds>_workout.json`
- **Wait a moment** - GitHub API operations may take a few seconds

### Form fields not populating
- **Check embedded_data.js** - Make sure `embedded_data.js` is up-to-date
- **Regenerate embedded data** - Run `fitness/scripts/generate_embedded_data.py` if routines/sessions changed
- **Hard refresh** - Clear browser cache and reload (Ctrl+Shift+R or Cmd+Shift+R)

## Verifying Your Workout Was Saved

After submitting a workout:

1. **Go to GitHub.com** and navigate to your repository
2. **Check branches** - Look for a new branch named `workout-YYYY-MM-DD-<timestamp>`
3. **Navigate to the branch** - Switch to the new branch
4. **Check `fitness/workout_logs/`** - Your workout file should be there
5. **View the file** - Click on the JSON file to see your workout data

## Support

For issues or questions:
- Check the logs section on the form (click "Show Logs" if hidden)
- Check browser console for detailed error messages
- Review `docs/DEVELOPMENT.md` for development-related questions

## Next Steps

- **Phase 11:** Testing and refinement based on real-world use
- **Phase 12:** Additional documentation and maintenance notes
