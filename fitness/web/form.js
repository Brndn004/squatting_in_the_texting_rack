// Basic form validation and settings toggle
// Full form logic will be added in Phase 5

const settingsToggle = document.getElementById('settingsToggle');
const settingsContent = document.getElementById('settingsContent');
const patTokenInput = document.getElementById('patToken');

if (!settingsToggle) {
    throw new Error('Settings toggle element not found');
}

if (!settingsContent) {
    throw new Error('Settings content element not found');
}

if (!patTokenInput) {
    throw new Error('PAT token input element not found');
}

// Load token from localStorage if available
const savedToken = localStorage.getItem('github_pat_token');
if (savedToken) {
    patTokenInput.value = savedToken;
    settingsToggle.textContent = 'Hide Settings';
    settingsContent.classList.add('visible');
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

// Save token to localStorage when changed
patTokenInput.addEventListener('change', () => {
    if (patTokenInput.value) {
        localStorage.setItem('github_pat_token', patTokenInput.value);
    } else {
        localStorage.removeItem('github_pat_token');
    }
});

// Basic form validation
const form = document.getElementById('workoutForm');
if (!form) {
    throw new Error('Workout form element not found');
}

form.addEventListener('submit', (e) => {
    e.preventDefault();
    
    // Clear previous errors
    document.querySelectorAll('.error').forEach(el => {
        el.textContent = '';
    });
    
    let isValid = true;
    
    // Validate PAT token
    const patToken = patTokenInput.value.trim();
    if (!patToken) {
        const patTokenError = document.getElementById('patTokenError');
        if (!patTokenError) {
            throw new Error('PAT token error element not found');
        }
        patTokenError.textContent = 'GitHub PAT token is required';
        isValid = false;
    }
    
    // Validate session
    const sessionSelect = document.getElementById('sessionSelect');
    if (!sessionSelect) {
        throw new Error('Session select element not found');
    }
    if (!sessionSelect.value) {
        const sessionSelectError = document.getElementById('sessionSelectError');
        if (!sessionSelectError) {
            throw new Error('Session select error element not found');
        }
        sessionSelectError.textContent = 'Please select a session';
        isValid = false;
    }
    
    // Validate bodyweight
    const bodyweightInput = document.getElementById('bodyweight');
    if (!bodyweightInput) {
        throw new Error('Bodyweight input element not found');
    }
    const bodyweight = parseFloat(bodyweightInput.value);
    if (isNaN(bodyweight)) {
        const bodyweightError = document.getElementById('bodyweightError');
        if (!bodyweightError) {
            throw new Error('Bodyweight error element not found');
        }
        bodyweightError.textContent = 'Bodyweight must be a number';
        isValid = false;
    } else if (bodyweight <= 0) {
        const bodyweightError = document.getElementById('bodyweightError');
        if (!bodyweightError) {
            throw new Error('Bodyweight error element not found');
        }
        bodyweightError.textContent = 'Bodyweight must be greater than 0';
        isValid = false;
    }
    
    // Validate exercises (will be implemented in Phase 5)
    const exercisesContainer = document.getElementById('exercisesContainer');
    if (!exercisesContainer) {
        throw new Error('Exercises container element not found');
    }
    if (exercisesContainer.children.length === 0) {
        isValid = false;
    }
    
    if (!isValid) {
        return;
    }
    
    // Form submission will be handled in Phase 5
    console.log('Form validation passed (submission logic in Phase 5)');
});
