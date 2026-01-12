// GitHub API integration functions (replicate MVP pattern)

const REPO_OWNER = 'Brndn004';
const REPO_NAME = 'squatting_in_the_texting_rack';

async function getDefaultBranch(token) {
    if (!token) {
        throw new Error('GitHub token cannot be empty');
    }
    
    log('Getting default branch from repository...');
    const apiUrl = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`;
    log(`Fetching repository info from: ${apiUrl}`);
    
    const response = await fetch(apiUrl, {
        headers: {
            'Authorization': `token ${token}`,
            'Accept': 'application/vnd.github.v3+json'
        }
    });
    
    log(`Repository info response status: ${response.status}`);
    
    if (!response.ok) {
        const errorData = await response.json();
        log(`Error getting repo info: ${JSON.stringify(errorData)}`);
        
        if (response.status === 401) {
            throw new Error(`Unauthorized: Invalid GitHub token or token lacks required permissions for repository ${REPO_OWNER}/${REPO_NAME}`);
        }
        
        if (response.status === 404) {
            throw new Error(`Repository not found: ${REPO_OWNER}/${REPO_NAME}. Check that it exists and the token has access.`);
        }
        
        if (!errorData.message) {
            throw new Error(`Failed to get repo info: ${response.status} - API error response missing message field. Full response: ${JSON.stringify(errorData)}`);
        }
        throw new Error(`Failed to get repo info: ${response.status} - ${errorData.message}`);
    }
    
    const repoData = await response.json();
    
    if (!repoData.default_branch) {
        throw new Error('Repository response missing default_branch field');
    }
    
    const defaultBranch = repoData.default_branch;
    log(`Default branch: ${defaultBranch}`);
    return defaultBranch;
}

async function getBranchSha(token, branchName) {
    if (!token) {
        throw new Error('GitHub token cannot be empty');
    }
    
    if (!branchName) {
        throw new Error('Branch name cannot be empty');
    }
    
    log(`Getting SHA for branch: ${branchName}`);
    const apiUrl = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/git/ref/heads/${branchName}`;
    log(`Fetching branch ref from: ${apiUrl}`);
    
    const response = await fetch(apiUrl, {
        headers: {
            'Authorization': `token ${token}`,
            'Accept': 'application/vnd.github.v3+json'
        }
    });
    
    log(`Branch ref response status: ${response.status}`);
    
    if (!response.ok) {
        const errorData = await response.json();
        log(`Error getting branch SHA: ${JSON.stringify(errorData)}`);
        
        if (response.status === 401) {
            throw new Error(`Unauthorized: Invalid GitHub token or token lacks required permissions for repository ${REPO_OWNER}/${REPO_NAME}`);
        }
        
        if (response.status === 404) {
            throw new Error(`Branch not found: ${branchName} in repository ${REPO_OWNER}/${REPO_NAME}. Check that the branch exists.`);
        }
        
        if (!errorData.message) {
            throw new Error(`Failed to get branch SHA: ${response.status} - API error response missing message field. Full response: ${JSON.stringify(errorData)}`);
        }
        throw new Error(`Failed to get branch SHA: ${response.status} - ${errorData.message}`);
    }
    
    const refData = await response.json();
    
    if (!refData.object) {
        throw new Error('Invalid response from GitHub API: missing object field in branch ref data');
    }
    
    if (!refData.object.sha) {
        throw new Error('Invalid response from GitHub API: missing sha field in branch ref object');
    }
    
    const sha = refData.object.sha;
    log(`Branch SHA: ${sha.substring(0, 7)}...`);
    return sha;
}

async function createBranch(token, branchName, baseBranchSha) {
    if (!token) {
        throw new Error('GitHub token cannot be empty');
    }
    
    if (!branchName) {
        throw new Error('Branch name cannot be empty');
    }
    
    if (!baseBranchSha) {
        throw new Error('Base branch SHA cannot be empty');
    }
    
    log(`Creating new branch: ${branchName} from SHA: ${baseBranchSha.substring(0, 7)}...`);
    const apiUrl = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/git/refs`;
    log(`POST request to: ${apiUrl}`);
    
    const requestBody = {
        ref: `refs/heads/${branchName}`,
        sha: baseBranchSha
    };
    log(`Request body: ${JSON.stringify(requestBody)}`);
    
    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Authorization': `token ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.v3+json'
        },
        body: JSON.stringify(requestBody)
    });
    
    log(`Create branch response status: ${response.status}`);
    
    if (!response.ok) {
        const errorData = await response.json();
        log(`Create branch response: ${JSON.stringify(errorData)}`);
        
        if (response.status === 401) {
            throw new Error(`Unauthorized: Invalid GitHub token or token lacks required permissions for repository ${REPO_OWNER}/${REPO_NAME}`);
        }
        
        if (response.status === 404) {
            throw new Error(`Repository or base branch not found: ${REPO_OWNER}/${REPO_NAME}. Check that the repository exists and the base branch SHA is valid.`);
        }
        
        // If branch already exists, that's okay - continue
        if (response.status === 422) {
            if (!errorData.message) {
                throw new Error(`Failed to create branch: ${response.status} - API error response missing message field. Full response: ${JSON.stringify(errorData)}`);
            }
            const errorMessage = errorData.message;
            if (errorMessage.toLowerCase().includes('already exists')) {
                log(`Branch already exists, continuing...`);
                return;
            }
        }
        
        if (!errorData.message) {
            throw new Error(`Failed to create branch: ${response.status} - API error response missing message field. Full response: ${JSON.stringify(errorData)}`);
        }
        throw new Error(`Failed to create branch: ${response.status} - ${errorData.message}`);
    } else {
        log(`Branch created successfully`);
    }
}

async function createFile(token, filePath, content, branchName, message) {
    if (!token) {
        throw new Error('GitHub token cannot be empty');
    }
    
    if (!filePath) {
        throw new Error('File path cannot be empty');
    }
    
    if (!content) {
        throw new Error('File content cannot be empty');
    }
    
    if (!branchName) {
        throw new Error('Branch name cannot be empty');
    }
    
    if (!message) {
        throw new Error('Commit message cannot be empty');
    }
    
    log(`Creating file: ${filePath} on branch: ${branchName}`);
    log(`File content length: ${content.length} characters`);
    log(`Commit message: ${message}`);
    
    const contentBase64 = btoa(unescape(encodeURIComponent(content)));
    log(`Base64 encoded content length: ${contentBase64.length} characters`);
    
    const apiUrl = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`;
    log(`PUT request to: ${apiUrl}`);
    
    const requestBody = {
        message: message,
        content: contentBase64,
        branch: branchName
    };
    log(`Request body keys: ${Object.keys(requestBody).join(', ')}`);
    
    const response = await fetch(apiUrl, {
        method: 'PUT',
        headers: {
            'Authorization': `token ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.v3+json'
        },
        body: JSON.stringify(requestBody)
    });
    
    log(`Create file response status: ${response.status}`);
    
    if (!response.ok) {
        const errorData = await response.json();
        log(`Error creating file: ${JSON.stringify(errorData)}`);
        
        if (response.status === 401) {
            throw new Error(`Unauthorized: Invalid GitHub token or token lacks required permissions for repository ${REPO_OWNER}/${REPO_NAME}`);
        }
        
        if (response.status === 404) {
            throw new Error(`Branch not found: ${branchName} in repository ${REPO_OWNER}/${REPO_NAME}. Branch must exist before creating files. Use createBranch() first.`);
        }
        
        if (response.status === 422) {
            if (!errorData.message) {
                throw new Error(`Failed to create/update file ${filePath} in ${REPO_OWNER}/${REPO_NAME}: ${response.status} - API error response missing message field. Full response: ${JSON.stringify(errorData)}`);
            }
            const errorMessage = errorData.message;
            if (errorMessage.toLowerCase().includes('sha') || errorMessage.toLowerCase().includes('same content')) {
                throw new Error(`File update failed: ${errorMessage}. Ensure you provide the correct SHA for updates.`);
            }
            throw new Error(`Failed to create/update file ${filePath} in ${REPO_OWNER}/${REPO_NAME}: ${response.status} - ${errorMessage}`);
        }
        
        if (!errorData.message) {
            throw new Error(`GitHub API error: ${response.status} - API error response missing message field. Full response: ${JSON.stringify(errorData)}`);
        }
        throw new Error(`GitHub API error: ${response.status} - ${errorData.message}`);
    }
    
    const result = await response.json();
    
    if (!result.commit) {
        throw new Error('Invalid response from GitHub API: missing commit field in file creation response');
    }
    
    if (!result.commit.sha) {
        throw new Error('Invalid response from GitHub API: missing commit.sha field in file creation response');
    }
    
    log(`File created successfully. Commit SHA: ${result.commit.sha.substring(0, 7)}...`);
    
    if (result.content && result.content.html_url) {
        log(`File URL: ${result.content.html_url}`);
    }
    
    return result;
}

async function commitWorkoutLog(token, workoutData) {
    if (!token) {
        throw new Error('GitHub token cannot be empty');
    }
    
    if (!workoutData) {
        throw new Error('Workout data cannot be null or undefined');
    }
    
    log('=== Starting workout log commit ===');
    log(`Workout data: ${JSON.stringify(workoutData, null, 2)}`);
    
    // Generate filename: YYYY-MM-DD-<unix epoch seconds>_workout.json
    const dateStr = workoutData.date;
    if (!dateStr) {
        throw new Error('Workout data missing date field');
    }
    
    const filename = `${dateStr}_workout.json`;
    const filePath = `fitness/workout_logs/${filename}`;
    log(`Generated filename: ${filename}`);
    log(`File path: ${filePath}`);
    
    // Convert workout data to JSON string
    const jsonContent = JSON.stringify(workoutData, null, 2);
    log(`JSON content generated (${jsonContent.length} characters)`);
    
    // Generate branch name from timestamp: workout-YYYY-MM-DD-<unix epoch seconds>
    const branchName = `workout-${dateStr}`;
    log(`Branch name: ${branchName}`);
    
    // Follow MVP pattern for branch creation:
    // 1. Get default branch name
    log('Step 1: Getting default branch...');
    const defaultBranch = await getDefaultBranch(token);
    
    // 2. Get default branch SHA
    log('Step 2: Getting default branch SHA...');
    const defaultBranchSha = await getBranchSha(token, defaultBranch);
    
    // 3. Create new branch
    log('Step 3: Creating new branch...');
    await createBranch(token, branchName, defaultBranchSha);
    
    // 4. Create file on new branch
    log('Step 4: Creating file on new branch...');
    const commitMessage = `Add workout log: ${filename}`;
    await createFile(token, filePath, jsonContent, branchName, commitMessage);
    
    log('=== Workout log commit completed successfully ===');
    return {
        branchName: branchName,
        filePath: filePath,
        filename: filename
    };
}
