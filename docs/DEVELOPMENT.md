# Development Guide

This guide explains how to set up and use a local development server for quick iteration on the workout tracker form.

## Local Development Server Setup

### Starting the Server

1. Navigate to the `docs/` directory:
   ```bash
   cd docs
   ```

2. Start Python's built-in HTTP server on port 8000:
   ```bash
   python3 -m http.server 8000
   ```

3. The server will start and display a message like:
   ```
   Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
   ```

**Note:** The server does NOT need to be restarted when files change. Just refresh your browser to see updates.

### Accessing from Laptop

- Open your browser and navigate to:
  - `http://localhost:8000/index.html`
  - Or simply `http://localhost:8000/` (if index.html is the default)

### Accessing from Phone

To access the form from your phone on the same Wi-Fi network:

1. **Find your computer's IP address:**
   - **Mac/Linux:** Run `ifconfig` in terminal and look for your Wi-Fi interface (usually `en0` or `wlan0`). Find the `inet` address (e.g., `192.168.1.100`).
   - **Windows:** Run `ipconfig` in command prompt and look for IPv4 Address under your Wi-Fi adapter.

2. **On your phone's browser**, navigate to:
   - `http://<ip-address>:8000/index.html`
   - Example: `http://192.168.1.100:8000/index.html`

3. **Important:** Both your computer and phone must be on the same Wi-Fi network.

## Quick Iteration Workflow

1. **Start the local server** (see above)
2. **Open the form** in your browser (`http://localhost:8000/index.html`)
3. **Make changes** to HTML, CSS, or JavaScript files
4. **Refresh the browser** - no need to restart the server
5. **Test your changes** immediately
6. **Repeat** as needed

This workflow allows for very fast iteration since you don't need to restart the server or deploy to GitHub Pages for every change.

## When to Use Local Server vs GitHub Pages

### Use Local Server For:
- **Quick iteration** - Testing changes rapidly during development
- **Debugging** - Using browser developer tools to debug issues
- **Initial development** - Building new features before they're ready for production
- **Testing on phone** - Quick testing on mobile devices via local network

### Use GitHub Pages For:
- **Production deployment** - When features are complete and ready for real-world use
- **Testing CORS** - Verifying GitHub API integration works correctly from GitHub Pages origin
- **Final validation** - Ensuring everything works in the production environment
- **Real workouts** - Actually recording workouts (not just testing)

## Recommendations

1. **Test locally first** - Use the local server for faster iteration during development
2. **Test on phone via local network** - Verify mobile usability before deploying
3. **Deploy to GitHub Pages** - For final testing and production use
4. **Keep server running** - Leave the server running while developing, just refresh browser for changes

## Troubleshooting

### Server won't start
- Make sure port 8000 is not already in use
- Try a different port: `python3 -m http.server 8080` (then use port 8080 in URLs)

### Can't access from phone
- Verify both devices are on the same Wi-Fi network
- Check firewall settings - may need to allow incoming connections on port 8000
- Try accessing from laptop first to verify server is running
- Double-check the IP address is correct

### Changes not appearing
- Make sure you saved the file
- Hard refresh the browser (Ctrl+Shift+R or Cmd+Shift+R)
- Check browser console for JavaScript errors
- Verify you're editing the correct file
