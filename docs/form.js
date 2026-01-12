// Main form initialization and event handlers

function initializeForm() {
    log('Initializing workout form...');
    
    populateSessionDropdown();
    setupSessionChangeHandler();
    loadSavedToken();
    setupSettingsToggle();
    setupTokenChangeHandler();
    setupFormSubmitHandler();
    
    log('Form initialization complete');
}

function populateSessionDropdown() {
    if (typeof SESSIONS === 'undefined') {
        throw new Error('SESSIONS not found in embedded_data.js');
    }
    
    const sessionSelect = document.getElementById('sessionSelect');
    if (!sessionSelect) {
        throw new Error('Session select element not found');
    }
    
    const sessions = getAllSessions();
    
    sessions.forEach(session => {
        const option = document.createElement('option');
        option.value = session.name;
        if (!session.data.name) {
            throw new Error(`Session ${session.name} missing name field in data`);
        }
        option.textContent = session.data.name;
        sessionSelect.appendChild(option);
    });
    
    log(`Loaded ${sessions.length} sessions into dropdown`);
}

function getAllSessions() {
    const sessions = [];
    for (const sessionName in SESSIONS) {
        if (SESSIONS.hasOwnProperty(sessionName)) {
            sessions.push({
                name: sessionName,
                data: SESSIONS[sessionName]
            });
        }
    }
    return sessions;
}

function setupSessionChangeHandler() {
    const sessionSelect = document.getElementById('sessionSelect');
    if (!sessionSelect) {
        throw new Error('Session select element not found');
    }
    
    sessionSelect.addEventListener('change', () => {
        const selectedSession = sessionSelect.value;
        if (!selectedSession) {
            hideExercisesSection();
            return;
        }
        
        try {
            const sessionData = loadSession(selectedSession);
            populateExerciseForm(sessionData);
        } catch (error) {
            log(`Error loading session: ${error.message}`);
            showErrorMessage(error.message);
        }
    });
}

function hideExercisesSection() {
    const exercisesSection = document.getElementById('exercisesSection');
    if (exercisesSection) {
        exercisesSection.style.display = 'none';
    }
}

function showErrorMessage(message) {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.textContent = `Error: ${message}`;
        messageDiv.className = 'message error';
    }
}

function loadSavedToken() {
    const savedToken = loadToken();
    const patTokenInput = document.getElementById('patToken');
    const settingsToggle = document.getElementById('settingsToggle');
    const settingsContent = document.getElementById('settingsContent');
    
    if (savedToken && patTokenInput) {
        patTokenInput.value = savedToken;
        if (settingsToggle) {
            settingsToggle.textContent = 'Hide Settings';
        }
        if (settingsContent) {
            settingsContent.classList.add('visible');
        }
    }
}

function setupSettingsToggle() {
    const settingsToggle = document.getElementById('settingsToggle');
    const settingsContent = document.getElementById('settingsContent');
    
    if (!settingsToggle || !settingsContent) {
        return;
    }
    
    settingsToggle.addEventListener('click', () => {
        if (settingsContent.classList.contains('visible')) {
            settingsContent.classList.remove('visible');
            settingsToggle.textContent = 'Show Settings';
        } else {
            settingsContent.classList.add('visible');
            settingsToggle.textContent = 'Hide Settings';
        }
    });
}

function setupTokenChangeHandler() {
    const patTokenInput = document.getElementById('patToken');
    if (!patTokenInput) {
        return;
    }
    
    patTokenInput.addEventListener('change', () => {
        if (patTokenInput.value) {
            saveToken(patTokenInput.value);
        } else {
            clearToken();
        }
    });
}

function setupFormSubmitHandler() {
    const form = document.getElementById('workoutForm');
    if (!form) {
        throw new Error('Workout form element not found');
    }
    
    form.addEventListener('submit', handleFormSubmit);
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    log('=== Starting form submission ===');
    
    clearPreviousErrors();
    clearMessage();
    
    if (!validateFormInputs()) {
        log('Form validation failed');
        return;
    }
    
    const submitButton = document.getElementById('submitButton');
    if (!submitButton) {
        throw new Error('Submit button element not found');
    }
    
    const patTokenInput = document.getElementById('patToken');
    if (!patTokenInput) {
        throw new Error('PAT token input element not found');
    }
    
    const patToken = patTokenInput.value.trim();
    if (!patToken) {
        throw new Error('GitHub PAT token is required');
    }
    
    // Disable submit button and show loading state
    submitButton.disabled = true;
    submitButton.textContent = 'Submitting...';
    showLoadingMessage('Submitting workout to GitHub...');
    
    try {
        const workoutData = collectFormData();
        validateFormData(workoutData);
        
        log(`Form data collected: ${JSON.stringify(workoutData, null, 2)}`);
        
        saveTokenIfProvided();
        
        // Commit workout log to GitHub
        log('Committing workout log to GitHub...');
        const result = await commitWorkoutLog(patToken, workoutData);
        
        log(`Workout log committed successfully. Branch: ${result.branchName}, File: ${result.filename}`);
        
        if (!result.branchUrl) {
            throw new Error('GitHub API response missing branchUrl');
        }
        
        const successMessage = `Success! Workout log saved to branch: <a href="${result.branchUrl}" target="_blank">${result.branchName}</a>`;
        showSuccessMessage(successMessage);
        
        // Reset form after successful submission
        const form = document.getElementById('workoutForm');
        if (form) {
            form.reset();
            hideExercisesSection();
            log('Form reset after successful submission');
        }
    } catch (error) {
        log(`Error: ${error.message}`);
        showErrorMessage(error.message);
    } finally {
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.textContent = 'Submit Workout';
    }
}

function clearPreviousErrors() {
    document.querySelectorAll('.error').forEach(el => {
        el.textContent = '';
    });
}

function clearMessage() {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.textContent = '';
        messageDiv.className = '';
    }
}

function validateFormInputs() {
    let isValid = true;
    const errors = [];
    
    if (!validatePatToken()) {
        isValid = false;
        errors.push('GitHub PAT token is required');
    }
    
    if (!validateSession()) {
        isValid = false;
        errors.push('Please select a session');
    }
    
    if (!validateBodyweightInput()) {
        isValid = false;
        errors.push('Bodyweight validation failed');
    }
    
    if (!validateExercisesPresent()) {
        isValid = false;
        errors.push('No exercises found');
    }
    
    if (!isValid) {
        const errorMessage = 'Validation failed: ' + errors.join(', ');
        log(errorMessage);
        showErrorMessage(errorMessage);
    }
    
    return isValid;
}

function validatePatToken() {
    const patTokenInput = document.getElementById('patToken');
    if (!patTokenInput) {
        throw new Error('PAT token input element not found');
    }
    
    const patToken = patTokenInput.value.trim();
    if (!patToken) {
        const patTokenError = document.getElementById('patTokenError');
        if (patTokenError) {
            patTokenError.textContent = 'GitHub PAT token is required';
        }
        // Show settings section if hidden so user can see the error
        const settingsContent = document.getElementById('settingsContent');
        const settingsToggle = document.getElementById('settingsToggle');
        if (settingsContent && !settingsContent.classList.contains('visible')) {
            settingsContent.classList.add('visible');
            if (settingsToggle) {
                settingsToggle.textContent = 'Hide Settings';
            }
        }
        return false;
    }
    
    return true;
}

function validateSession() {
    const sessionSelect = document.getElementById('sessionSelect');
    if (!sessionSelect) {
        throw new Error('Session select element not found');
    }
    
    if (!sessionSelect.value) {
        const sessionSelectError = document.getElementById('sessionSelectError');
        if (sessionSelectError) {
            sessionSelectError.textContent = 'Please select a session';
        }
        return false;
    }
    
    return true;
}

function validateBodyweightInput() {
    const bodyweightInput = document.getElementById('bodyweight');
    if (!bodyweightInput) {
        throw new Error('Bodyweight input element not found');
    }
    
    const bodyweight = parseFloat(bodyweightInput.value);
    if (isNaN(bodyweight)) {
        const bodyweightError = document.getElementById('bodyweightError');
        if (bodyweightError) {
            bodyweightError.textContent = 'Bodyweight must be a number';
        }
        return false;
    }
    
    if (bodyweight <= 0) {
        const bodyweightError = document.getElementById('bodyweightError');
        if (bodyweightError) {
            bodyweightError.textContent = 'Bodyweight must be greater than 0';
        }
        return false;
    }
    
    return true;
}

function validateExercisesPresent() {
    const exercisesContainer = document.getElementById('exercisesContainer');
    if (!exercisesContainer) {
        throw new Error('Exercises container element not found');
    }
    
    if (exercisesContainer.children.length === 0) {
        return false;
    }
    
    return true;
}

function saveTokenIfProvided() {
    const patTokenInput = document.getElementById('patToken');
    if (!patTokenInput) {
        return;
    }
    
    const patToken = patTokenInput.value.trim();
    if (patToken) {
        saveToken(patToken);
    }
}

function showSuccessMessage(message) {
    const messageDiv = document.getElementById('message');
    if (!messageDiv) {
        throw new Error('Message div element not found');
    }
    messageDiv.innerHTML = message;
    messageDiv.className = 'message success';
}

function showLoadingMessage(message) {
    const messageDiv = document.getElementById('message');
    if (!messageDiv) {
        throw new Error('Message div element not found');
    }
    messageDiv.textContent = message;
    messageDiv.className = 'message';
    messageDiv.style.color = '#0066cc';
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        initializeForm();
    } catch (error) {
        console.error('Initialization error:', error);
        log(`Initialization error: ${error.message}`);
    }
});
