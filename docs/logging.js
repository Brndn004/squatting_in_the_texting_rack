// Logging functionality (replicate MVP pattern)

function log(message) {
    const logsContent = document.getElementById('logsContent');
    if (!logsContent) {
        console.log(message);
        return;
    }
    
    const logsSection = document.getElementById('logs');
    if (!logsSection) {
        console.log(message);
        return;
    }
    
    logsSection.classList.add('visible');
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.textContent = `[${timestamp}] ${message}`;
    logsContent.appendChild(logEntry);
    logsContent.scrollTop = logsContent.scrollHeight;
    console.log(`[${timestamp}] ${message}`);
}
