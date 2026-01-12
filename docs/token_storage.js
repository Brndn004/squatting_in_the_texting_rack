// localStorage token management

function saveToken(token) {
    if (!token) {
        throw new Error('Token cannot be empty');
    }
    localStorage.setItem('github_pat_token', token);
    log('Token saved to localStorage');
}

function loadToken() {
    const token = localStorage.getItem('github_pat_token');
    if (!token) {
        return null;
    }
    return token;
}

function clearToken() {
    localStorage.removeItem('github_pat_token');
    log('Token cleared from localStorage');
}
