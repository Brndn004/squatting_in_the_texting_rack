// Form data validation

function validateFormData(data) {
    if (!data) {
        throw new Error('Form data cannot be null or undefined');
    }
    
    validateDate(data.date);
    validateSessionName(data.session_name);
    validateBodyweight(data.bodyweight_lb);
    validateExercises(data.exercises);
    
    log('Form data validation passed');
}

function validateDate(date) {
    if (!date) {
        throw new Error('Form data missing date field');
    }
    
    if (typeof date !== 'string') {
        throw new Error('Form data date must be a string');
    }
}

function validateSessionName(sessionName) {
    if (!sessionName) {
        throw new Error('Form data missing session_name field');
    }
    
    if (typeof sessionName !== 'string') {
        throw new Error('Form data session_name must be a string');
    }
}

function validateBodyweight(bodyweight) {
    if (typeof bodyweight !== 'number') {
        throw new Error('Form data bodyweight_lb must be a number');
    }
    
    if (bodyweight <= 0) {
        throw new Error('Form data bodyweight_lb must be greater than 0');
    }
}

function validateExercises(exercises) {
    if (!exercises) {
        throw new Error('Form data missing exercises array');
    }
    
    if (!Array.isArray(exercises)) {
        throw new Error('Form data exercises must be an array');
    }
    
    if (exercises.length === 0) {
        throw new Error('Form data exercises array cannot be empty');
    }
    
    exercises.forEach((exercise, exerciseIndex) => {
        validateExercise(exercise, exerciseIndex);
    });
}

function validateExercise(exercise, exerciseIndex) {
    if (!exercise.exercise_name) {
        throw new Error(`Exercise at index ${exerciseIndex} missing exercise_name`);
    }
    
    if (!exercise.sets) {
        throw new Error(`Exercise at index ${exerciseIndex} missing sets array`);
    }
    
    if (!Array.isArray(exercise.sets)) {
        throw new Error(`Exercise at index ${exerciseIndex} sets must be an array`);
    }
    
    if (exercise.sets.length === 0) {
        throw new Error(`Exercise at index ${exerciseIndex} sets array cannot be empty`);
    }
    
    exercise.sets.forEach((set, setIndex) => {
        validateSet(set, exerciseIndex, setIndex);
    });
}

function validateSet(set, exerciseIndex, setIndex) {
    if (typeof set.reps !== 'number') {
        throw new Error(`Exercise ${exerciseIndex}, set ${setIndex} reps must be a number`);
    }
    
    if (set.reps < 0) {
        throw new Error(`Exercise ${exerciseIndex}, set ${setIndex} reps must be >= 0`);
    }
    
    if (typeof set.lb !== 'number') {
        throw new Error(`Exercise ${exerciseIndex}, set ${setIndex} lb must be a number`);
    }
    
    if (set.lb < 0) {
        throw new Error(`Exercise ${exerciseIndex}, set ${setIndex} lb must be >= 0`);
    }
}
