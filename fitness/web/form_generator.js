// Form generation - dynamically create exercise input fields

function populateExerciseForm(sessionData) {
    if (!sessionData) {
        throw new Error('Session data cannot be null or undefined');
    }
    
    if (!sessionData.exercises) {
        throw new Error('Session data missing exercises array');
    }
    
    if (!Array.isArray(sessionData.exercises)) {
        throw new Error('Session exercises must be an array');
    }
    
    const exercisesContainer = document.getElementById('exercisesContainer');
    if (!exercisesContainer) {
        throw new Error('Exercises container element not found');
    }
    
    const exercisesSection = document.getElementById('exercisesSection');
    if (!exercisesSection) {
        throw new Error('Exercises section element not found');
    }
    
    exercisesContainer.innerHTML = '';
    
    if (sessionData.exercises.length === 0) {
        exercisesSection.style.display = 'none';
        log('No exercises in session');
        return;
    }
    
    exercisesSection.style.display = 'block';
    
    sessionData.exercises.forEach((exercise, exerciseIndex) => {
        if (!exercise.exercise_name) {
            throw new Error(`Exercise at index ${exerciseIndex} missing exercise_name`);
        }
        
        if (typeof exercise.sets !== 'number' || exercise.sets <= 0) {
            throw new Error(`Exercise at index ${exerciseIndex} has invalid sets value: ${exercise.sets}`);
        }
        
        const exerciseName = getExerciseName(exercise.exercise_name);
        const numSets = exercise.sets;
        
        const exerciseDiv = createExerciseElement(exerciseName, exercise.exercise_name, exerciseIndex, numSets);
        exercisesContainer.appendChild(exerciseDiv);
    });
    
    log(`Populated ${sessionData.exercises.length} exercises with form inputs`);
}

function createExerciseElement(exerciseName, exerciseNameKey, exerciseIndex, numSets) {
    const exerciseDiv = document.createElement('div');
    exerciseDiv.className = 'exercise';
    exerciseDiv.setAttribute('data-exercise-name', exerciseNameKey);
    
    const exerciseNameDiv = document.createElement('div');
    exerciseNameDiv.className = 'exercise-name';
    exerciseNameDiv.textContent = exerciseName;
    exerciseDiv.appendChild(exerciseNameDiv);
    
    for (let setIndex = 0; setIndex < numSets; setIndex++) {
        const setDiv = createSetElement(exerciseIndex, setIndex);
        exerciseDiv.appendChild(setDiv);
    }
    
    return exerciseDiv;
}

function createSetElement(exerciseIndex, setIndex) {
    const setDiv = document.createElement('div');
    setDiv.className = 'set';
    
    const setLabel = document.createElement('div');
    setLabel.className = 'set-label';
    setLabel.textContent = `Set ${setIndex + 1}:`;
    setDiv.appendChild(setLabel);
    
    const repsInput = createNumberInput('reps', exerciseIndex, setIndex, '1');
    const repsLabel = document.createElement('label');
    repsLabel.textContent = 'Reps:';
    repsLabel.style.marginRight = '5px';
    repsLabel.appendChild(repsInput);
    setDiv.appendChild(repsLabel);
    
    const weightInput = createNumberInput('lb', exerciseIndex, setIndex, '0.1');
    const weightLabel = document.createElement('label');
    weightLabel.textContent = 'Weight (lb):';
    weightLabel.style.marginRight = '5px';
    weightLabel.appendChild(weightInput);
    setDiv.appendChild(weightLabel);
    
    return setDiv;
}

function createNumberInput(field, exerciseIndex, setIndex, step) {
    const input = document.createElement('input');
    input.type = 'number';
    input.className = 'set-input';
    input.min = '0';
    input.step = step;
    input.required = true;
    input.setAttribute('data-exercise-index', exerciseIndex);
    input.setAttribute('data-set-index', setIndex);
    input.setAttribute('data-field', field);
    return input;
}
