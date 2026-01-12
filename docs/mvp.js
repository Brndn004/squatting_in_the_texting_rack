const REPO_OWNER = 'Brndn004';
const REPO_NAME = 'squatting_in_the_texting_rack';

function log(message) {
    const logsContent = document.getElementById('logsContent');
    if (!logsContent) {
        console.log(message);
        return;
    }
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.textContent = `[${timestamp}] ${message}`;
    logsContent.appendChild(logEntry);
    logsContent.scrollTop = logsContent.scrollHeight;
    console.log(`[${timestamp}] ${message}`);
}

async function getDefaultBranch(token) {
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
        throw new Error(`Failed to get repo info: ${response.status} - ${errorData.message || JSON.stringify(errorData)}`);
    }
    
    const repoData = await response.json();
    const defaultBranch = repoData.default_branch;
    log(`Default branch: ${defaultBranch}`);
    return defaultBranch;
}

async function getBranchSha(token, branchName) {
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
        throw new Error(`Failed to get branch SHA: ${response.status} - ${errorData.message || JSON.stringify(errorData)}`);
    }
    
    const refData = await response.json();
    const sha = refData.object.sha;
    log(`Branch SHA: ${sha.substring(0, 7)}...`);
    return sha;
}

async function createBranch(token, branchName, baseBranchSha) {
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
        // If branch already exists, that's okay
        if (response.status !== 422 || !errorData.message?.includes('already exists')) {
            throw new Error(`Failed to create branch: ${response.status} - ${errorData.message || JSON.stringify(errorData)}`);
        }
        log(`Branch already exists, continuing...`);
    } else {
        log(`Branch created successfully`);
    }
}

async function createFile(token, filePath, content, branchName, message) {
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
        throw new Error(`GitHub API error: ${response.status} - ${errorData.message || JSON.stringify(errorData)}`);
    }
    
    const result = await response.json();
    log(`File created successfully. Commit SHA: ${result.commit.sha.substring(0, 7)}...`);
    log(`File URL: ${result.content.html_url}`);
}

async function submitForm(token, stringValue, integerValue) {
    log('=== Starting form submission ===');
    log(`String value: "${stringValue}"`);
    log(`Integer value: ${integerValue}`);
    
    // Collect form data
    const formData = {
        string: stringValue,
        integer: integerValue
    };
    log(`Form data collected: ${JSON.stringify(formData)}`);
    
    // Convert to JSON
    const jsonContent = JSON.stringify(formData, null, 2);
    log(`JSON content generated (${jsonContent.length} characters)`);
    
    // Generate timestamp and branch name
    const timestamp = Math.floor(Date.now() / 1000);
    log(`Generated timestamp: ${timestamp}`);
    const branchName = `mvp-test-${timestamp}`;
    const fileName = `${timestamp}_test.json`;
    const filePath = `fitness/mvp_test/${fileName}`;
    log(`Branch name: ${branchName}`);
    log(`File name: ${fileName}`);
    log(`File path: ${filePath}`);
    
    // Get default branch
    log('Step 1: Getting default branch...');
    const defaultBranch = await getDefaultBranch(token);
    
    // Get default branch SHA
    log('Step 2: Getting default branch SHA...');
    const defaultBranchSha = await getBranchSha(token, defaultBranch);
    
    // Create new branch
    log('Step 3: Creating new branch...');
    await createBranch(token, branchName, defaultBranchSha);
    
    // Create file on new branch
    log('Step 4: Creating file on new branch...');
    await createFile(token, filePath, jsonContent, branchName, `MVP test: ${fileName}`);
    
    log('=== Form submission completed successfully ===');
    return branchName;
}

document.addEventListener('DOMContentLoaded', () => {
    log('Page loaded, initializing form...');
    
    const form = document.getElementById('testForm');
    if (!form) {
        log('ERROR: Form element not found');
        throw new Error('Form element not found');
    }
    log('Form element found');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        log('Form submit event triggered');
        
        const stringInput = document.getElementById('stringInput');
        const integerInput = document.getElementById('integerInput');
        const patInput = document.getElementById('patInput');
        const messageDiv = document.getElementById('message');
        
        if (!stringInput || !integerInput || !patInput || !messageDiv) {
            log('ERROR: Required form elements not found');
            throw new Error('Required form elements not found');
        }
        log('All form elements found');
        
        const stringValue = stringInput.value;
        const integerValue = parseInt(integerInput.value);
        const patToken = patInput.value;
        
        log(`PAT token length: ${patToken.length} characters`);
        log(`PAT token starts with: ${patToken.substring(0, 4)}...`);
        
        messageDiv.textContent = 'Submitting...';
        messageDiv.style.color = 'blue';
        log('Displaying "Submitting..." message');
        
        try {
            const branchName = await submitForm(patToken, stringValue, integerValue);
            messageDiv.textContent = `Success! File created on branch: ${branchName}`;
            messageDiv.style.color = 'green';
            log(`Success message displayed for branch: ${branchName}`);
            
            // Reset form
            form.reset();
            log('Form reset');
            
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            log(`ERROR caught: ${errorMessage}`);
            messageDiv.textContent = `Error: ${errorMessage}`;
            messageDiv.style.color = 'red';
            log('Error message displayed');
        }
    });
    
    log('Form event listener attached, ready for submission');
});
