// Form data collection - collect all form data into workout log JSON structure

function collectFormData() {
    const sessionName = getSelectedSessionName();
    const bodyweight = getBodyweight();
    const sessionData = loadSession(sessionName);
    const exercises = collectExercisesData(sessionData);
    
    const workoutData = {
        date: getCurrentDatetime(),
        session_name: sessionName,
        bodyweight_lb: bodyweight,
        exercises: exercises
    };
    
    log('Form data collected successfully');
    return workoutData;
}

function getSelectedSessionName() {
    const sessionSelect = document.getElementById('sessionSelect');
    if (!sessionSelect) {
        throw new Error('Session select element not found');
    }
    
    if (!sessionSelect.value) {
        throw new Error('Session must be selected');
    }
    
    return sessionSelect.value;
}

function getBodyweight() {
    const bodyweightInput = document.getElementById('bodyweight');
    if (!bodyweightInput) {
        throw new Error('Bodyweight input element not found');
    }
    
    const bodyweight = parseFloat(bodyweightInput.value);
    if (isNaN(bodyweight)) {
        throw new Error('Bodyweight must be a number');
    }
    
    if (bodyweight <= 0) {
        throw new Error('Bodyweight must be greater than 0');
    }
    
    return bodyweight;
}

function collectExercisesData(sessionData) {
    const exercisesContainer = document.getElementById('exercisesContainer');
    if (!exercisesContainer) {
        throw new Error('Exercises container element not found');
    }
    
    const exercises = [];
    const exerciseDivs = exercisesContainer.querySelectorAll('.exercise');
    
    exerciseDivs.forEach((exerciseDiv, exerciseIndex) => {
        const exerciseName = getExerciseNameFromDiv(exerciseDiv, exerciseIndex);
        const sessionExercise = getSessionExercise(sessionData, exerciseIndex);
        const sets = collectSetsData(exerciseDiv, exerciseIndex, sessionExercise.sets);
        
        exercises.push({
            exercise_name: exerciseName,
            sets: sets
        });
    });
    
    return exercises;
}

function getExerciseNameFromDiv(exerciseDiv, exerciseIndex) {
    const exerciseName = exerciseDiv.getAttribute('data-exercise-name');
    if (!exerciseName) {
        throw new Error(`Exercise div at index ${exerciseIndex} missing data-exercise-name attribute`);
    }
    return exerciseName;
}

function getSessionExercise(sessionData, exerciseIndex) {
    const sessionExercise = sessionData.exercises[exerciseIndex];
    if (!sessionExercise) {
        throw new Error(`Session exercise at index ${exerciseIndex} not found`);
    }
    return sessionExercise;
}

function collectSetsData(exerciseDiv, exerciseIndex, numSets) {
    const sets = [];
    
    for (let setIndex = 0; setIndex < numSets; setIndex++) {
        const reps = getSetReps(exerciseDiv, exerciseIndex, setIndex);
        const lb = getSetWeight(exerciseDiv, exerciseIndex, setIndex);
        
        sets.push({
            reps: reps,
            lb: lb
        });
    }
    
    return sets;
}

function getSetReps(exerciseDiv, exerciseIndex, setIndex) {
    const repsInput = exerciseDiv.querySelector(`input[data-set-index="${setIndex}"][data-field="reps"]`);
    if (!repsInput) {
        throw new Error(`Reps input not found for exercise ${exerciseIndex}, set ${setIndex}`);
    }
    
    const reps = parseInt(repsInput.value, 10);
    if (isNaN(reps)) {
        throw new Error(`Reps must be a number for exercise ${exerciseIndex}, set ${setIndex}`);
    }
    
    if (reps < 0) {
        throw new Error(`Reps must be >= 0 for exercise ${exerciseIndex}, set ${setIndex}`);
    }
    
    return reps;
}

function getSetWeight(exerciseDiv, exerciseIndex, setIndex) {
    const weightInput = exerciseDiv.querySelector(`input[data-set-index="${setIndex}"][data-field="lb"]`);
    if (!weightInput) {
        throw new Error(`Weight input not found for exercise ${exerciseIndex}, set ${setIndex}`);
    }
    
    const lb = parseFloat(weightInput.value);
    if (isNaN(lb)) {
        throw new Error(`Weight must be a number for exercise ${exerciseIndex}, set ${setIndex}`);
    }
    
    if (lb < 0) {
        throw new Error(`Weight must be >= 0 for exercise ${exerciseIndex}, set ${setIndex}`);
    }
    
    return lb;
}
