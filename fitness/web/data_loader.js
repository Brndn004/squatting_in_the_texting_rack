// Data loading functions for routines, sessions, and exercises

function loadRoutines() {
    if (typeof ROUTINES === 'undefined') {
        throw new Error('ROUTINES not found in embedded_data.js');
    }
    
    if (typeof ROUTINES !== 'object' || ROUTINES === null) {
        throw new Error('ROUTINES must be an object');
    }
    
    const routines = [];
    for (const routineName in ROUTINES) {
        if (ROUTINES.hasOwnProperty(routineName)) {
            routines.push({
                name: routineName,
                data: ROUTINES[routineName]
            });
        }
    }
    
    log(`Loaded ${routines.length} routines`);
    return routines;
}

function loadSession(sessionName) {
    if (!sessionName) {
        throw new Error('Session name cannot be empty');
    }
    
    if (typeof SESSIONS === 'undefined') {
        throw new Error('SESSIONS not found in embedded_data.js');
    }
    
    if (typeof SESSIONS !== 'object' || SESSIONS === null) {
        throw new Error('SESSIONS must be an object');
    }
    
    if (!(sessionName in SESSIONS)) {
        throw new Error(`Session '${sessionName}' not found in SESSIONS`);
    }
    
    const sessionData = SESSIONS[sessionName];
    
    if (!sessionData) {
        throw new Error(`Session data for '${sessionName}' is null or undefined`);
    }
    
    if (!sessionData.exercises) {
        throw new Error(`Session '${sessionName}' missing exercises array`);
    }
    
    if (!Array.isArray(sessionData.exercises)) {
        throw new Error(`Session '${sessionName}' exercises must be an array`);
    }
    
    log(`Loaded session: ${sessionName} with ${sessionData.exercises.length} exercises`);
    return sessionData;
}

function getExerciseName(exerciseName) {
    if (!exerciseName) {
        throw new Error('Exercise name cannot be empty');
    }
    
    if (typeof EXERCISES === 'undefined') {
        throw new Error('EXERCISES not found in embedded_data.js');
    }
    
    if (typeof EXERCISES !== 'object' || EXERCISES === null) {
        throw new Error('EXERCISES must be an object');
    }
    
    if (!(exerciseName in EXERCISES)) {
        throw new Error(`Exercise '${exerciseName}' not found in EXERCISES`);
    }
    
    const exerciseData = EXERCISES[exerciseName];
    
    if (!exerciseData) {
        throw new Error(`Exercise data for '${exerciseName}' is null or undefined`);
    }
    
    if (!exerciseData.name) {
        throw new Error(`Exercise '${exerciseName}' missing name field`);
    }
    
    return exerciseData.name;
}

function getExerciseData(exerciseName) {
    if (!exerciseName) {
        throw new Error('Exercise name cannot be empty');
    }
    
    if (typeof EXERCISES === 'undefined') {
        throw new Error('EXERCISES not found in embedded_data.js');
    }
    
    if (typeof EXERCISES !== 'object' || EXERCISES === null) {
        throw new Error('EXERCISES must be an object');
    }
    
    if (!(exerciseName in EXERCISES)) {
        throw new Error(`Exercise '${exerciseName}' not found in EXERCISES`);
    }
    
    const exerciseData = EXERCISES[exerciseName];
    
    if (!exerciseData) {
        throw new Error(`Exercise data for '${exerciseName}' is null or undefined`);
    }
    
    return exerciseData;
}
