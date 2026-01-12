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
    
    const totalExercises = sessionData.exercises.length;
    
    sessionData.exercises.forEach((exercise, exerciseIndex) => {
        if (!exercise.exercise_name) {
            throw new Error(`Exercise at index ${exerciseIndex} missing exercise_name`);
        }
        
        if (typeof exercise.sets !== 'number' || exercise.sets <= 0) {
            throw new Error(`Exercise at index ${exerciseIndex} has invalid sets value: ${exercise.sets}`);
        }
        
        if (typeof exercise.reps !== 'number' || exercise.reps < 0) {
            throw new Error(`Exercise at index ${exerciseIndex} has invalid reps value: ${exercise.reps}`);
        }
        
        if (typeof exercise.percent_1rm !== 'number' || exercise.percent_1rm <= 0 || exercise.percent_1rm > 1) {
            throw new Error(`Exercise at index ${exerciseIndex} has invalid percent_1rm value: ${exercise.percent_1rm}`);
        }
        
        const exerciseName = getExerciseName(exercise.exercise_name);
        const exerciseData = getExerciseData(exercise.exercise_name);
        const numSets = exercise.sets;
        const reps = exercise.reps;
        const percent1rm = exercise.percent_1rm;
        const exerciseNumber = exerciseIndex + 1;
        
        const exerciseDiv = createExerciseElement(exerciseName, exercise.exercise_name, exerciseIndex, numSets, reps, percent1rm, exerciseData, exerciseNumber, totalExercises);
        exercisesContainer.appendChild(exerciseDiv);
    });
    
    log(`Populated ${sessionData.exercises.length} exercises with form inputs`);
}

function createExerciseElement(exerciseName, exerciseNameKey, exerciseIndex, numSets, reps, percent1rm, exerciseData, exerciseNumber, totalExercises) {
    if (typeof exerciseNumber !== 'number' || exerciseNumber < 1) {
        throw new Error(`Invalid exercise number: ${exerciseNumber}`);
    }
    
    if (typeof totalExercises !== 'number' || totalExercises < 1) {
        throw new Error(`Invalid total exercises: ${totalExercises}`);
    }
    
    if (!exerciseData['1rm']) {
        throw new Error(`Exercise '${exerciseNameKey}' missing 1rm field`);
    }
    
    if (!('lb' in exerciseData['1rm'])) {
        throw new Error(`Exercise '${exerciseNameKey}' missing 1rm.lb field`);
    }
    
    if (typeof exerciseData['1rm'].lb !== 'number') {
        throw new Error(`Exercise '${exerciseNameKey}' 1rm.lb must be a number`);
    }
    
    const oneRm = exerciseData['1rm'].lb;
    const weight = percent1rm * oneRm;
    
    const exerciseDiv = document.createElement('div');
    exerciseDiv.className = 'exercise';
    exerciseDiv.setAttribute('data-exercise-name', exerciseNameKey);
    
    const exerciseNameDiv = document.createElement('div');
    exerciseNameDiv.className = 'exercise-name';
    exerciseNameDiv.textContent = `${exerciseNumber}/${totalExercises} ${exerciseName} - 1RM of ${oneRm} lb`;
    exerciseDiv.appendChild(exerciseNameDiv);
    
    for (let setIndex = 0; setIndex < numSets; setIndex++) {
        const setDiv = createSetElement(exerciseIndex, setIndex, reps, weight);
        exerciseDiv.appendChild(setDiv);
    }
    
    return exerciseDiv;
}

function createSetElement(exerciseIndex, setIndex, reps, weight) {
    if (typeof reps !== 'number' || reps < 0) {
        throw new Error(`Invalid reps value for exercise ${exerciseIndex}, set ${setIndex}: ${reps}`);
    }
    
    if (typeof weight !== 'number' || weight < 0) {
        throw new Error(`Invalid weight value for exercise ${exerciseIndex}, set ${setIndex}: ${weight}`);
    }
    
    const setDiv = document.createElement('div');
    setDiv.className = 'set';
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `set-checkbox-${exerciseIndex}-${setIndex}`;
    checkbox.setAttribute('data-exercise-index', exerciseIndex);
    checkbox.setAttribute('data-set-index', setIndex);
    checkbox.addEventListener('change', function() {
        checkbox.checked = checkbox.checked;
    });
    setDiv.appendChild(checkbox);
    
    const setLabel = document.createElement('div');
    setLabel.className = 'set-label';
    setLabel.textContent = `Set ${setIndex + 1}:`;
    setDiv.appendChild(setLabel);
    
    const repsInput = createNumberInput('reps', exerciseIndex, setIndex, '1');
    repsInput.value = reps.toString();
    const repsLabel = document.createElement('label');
    repsLabel.textContent = 'Reps:';
    repsLabel.style.marginRight = '5px';
    repsLabel.appendChild(repsInput);
    setDiv.appendChild(repsLabel);
    
    const weightInput = createNumberInput('lb', exerciseIndex, setIndex, '0.1');
    weightInput.value = weight.toFixed(1);
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
