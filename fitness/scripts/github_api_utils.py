#!/usr/bin/env python3
"""GitHub API utility functions.

This module provides functions for interacting with the GitHub REST API,
including repository information, branch management, and file operations.
"""

import base64
from typing import Optional

import requests


def _validate_token(token: str) -> None:
    """Validate that token is not empty.
    
    Args:
        token: GitHub Personal Access Token.
        
    Raises:
        ValueError: If token is empty.
    """
    if not token:
        raise ValueError("GitHub token cannot be empty")


def _validate_repo(repo: str) -> None:
    """Validate repository format.
    
    Args:
        repo: Repository in format "owner/repo".
        
    Raises:
        ValueError: If repo is empty or format is invalid.
    """
    if not repo:
        raise ValueError("Repository name cannot be empty")
    
    if "/" not in repo:
        raise ValueError(f"Repository must be in format 'owner/repo', got: {repo}")


def _validate_not_empty(value: str, name: str) -> None:
    """Validate that a value is not empty.
    
    Args:
        value: Value to validate.
        name: Name of the value (for error messages).
        
    Raises:
        ValueError: If value is empty.
    """
    if not value:
        raise ValueError(f"{name} cannot be empty")


def _build_headers(token: str, include_content_type: bool = False) -> dict:
    """Build common HTTP headers for GitHub API requests.
    
    Args:
        token: GitHub Personal Access Token.
        include_content_type: Whether to include Content-Type header.
        
    Returns:
        Dictionary of HTTP headers.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    if include_content_type:
        headers["Content-Type"] = "application/json"
    
    return headers


def _extract_error_message(response: requests.Response) -> str:
    """Extract error message from API response.
    
    Args:
        response: HTTP response object.
        
    Returns:
        Error message string.
    """
    if response.content:
        error_data = response.json()
        if "message" in error_data:
            return error_data["message"]
    
    return f"Unknown error: {response.status_code}"


def _handle_401_error(repo: str) -> None:
    """Handle 401 Unauthorized errors.
    
    Args:
        repo: Repository name (for error message).
        
    Raises:
        ValueError: Always raises with 401 error message.
    """
    raise ValueError(f"Unauthorized: Invalid GitHub token or token lacks required permissions for repository {repo}")


def _handle_404_error(repo: str, context: str) -> None:
    """Handle 404 Not Found errors.
    
    Args:
        repo: Repository name (for error message).
        context: Additional context about what was not found.
        
    Raises:
        ValueError: Always raises with 404 error message.
    """
    raise ValueError(f"{context} not found: {repo}. Check that it exists and the token has access.")


def _handle_422_branch_exists_error(response: requests.Response, branch_name: str, repo: str) -> bool:
    """Handle 422 validation error for branch already exists case.
    
    Args:
        response: HTTP response object.
        branch_name: Name of the branch.
        repo: Repository name.
        
    Returns:
        True if branch already exists (error should be ignored), False otherwise.
        
    Raises:
        ValueError: If 422 error is not due to branch already existing.
    """
    if response.content:
        error_data = response.json()
        if "message" in error_data:
            error_message = error_data["message"]
            if "already exists" in error_message.lower():
                return True
            raise ValueError(f"Failed to create branch {branch_name} in {repo}: {response.status_code} - {error_message}")
    
    raise ValueError(f"Failed to create branch {branch_name} in {repo}: {response.status_code} - Validation error")


def _handle_422_file_error(response: requests.Response, path: str, repo: str) -> None:
    """Handle 422 validation error for file operations.
    
    Args:
        response: HTTP response object.
        path: File path.
        repo: Repository name.
        
    Raises:
        ValueError: Always raises with 422 error message.
    """
    if response.content:
        error_data = response.json()
        if "message" in error_data:
            error_message = error_data["message"]
            if "sha" in error_message.lower() or "same content" in error_message.lower():
                raise ValueError(f"File update failed: {error_message}. Ensure you provide the correct SHA for updates.")
            raise ValueError(f"Failed to create/update file {path} in {repo}: {response.status_code} - {error_message}")
    
    raise ValueError(f"Failed to create/update file {path} in {repo}: {response.status_code} - Validation error")


def _handle_generic_error(response: requests.Response, repo: str, context: str) -> None:
    """Handle generic API errors.
    
    Args:
        response: HTTP response object.
        repo: Repository name.
        context: Context about the operation that failed.
        
    Raises:
        ValueError: Always raises with error message.
    """
    error_message = _extract_error_message(response)
    raise ValueError(f"Failed {context} for {repo}: {response.status_code} - {error_message}")


def _parse_branch_ref_response(ref_data: dict) -> str:
    """Parse branch ref response and extract SHA.
    
    Args:
        ref_data: Branch ref data from GitHub API.
        
    Returns:
        SHA string of the branch's HEAD commit.
        
    Raises:
        ValueError: If response structure is invalid.
    """
    if "object" not in ref_data:
        raise ValueError("Invalid response from GitHub API: missing 'object' field in branch ref data")
    
    if "sha" not in ref_data["object"]:
        raise ValueError("Invalid response from GitHub API: missing 'sha' field in branch ref object")
    
    return ref_data["object"]["sha"]


def get_repo_info(token: str, repo: str) -> dict:
    """Get repository information including default branch.
    
    Args:
        token: GitHub Personal Access Token for authentication.
        repo: Repository in format "owner/repo" (e.g., "Brndn004/squatting_in_the_texting_rack").
        
    Returns:
        Dictionary containing repository information including 'default_branch'.
        
    Raises:
        ValueError: If token or repo is empty, or if repo format is invalid.
        requests.RequestException: If API request fails.
        ValueError: If API returns an error (401, 404, etc.) with clear error message.
    """
    _validate_token(token)
    _validate_repo(repo)
    
    api_url = f"https://api.github.com/repos/{repo}"
    headers = _build_headers(token)
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 401:
        _handle_401_error(repo)
    
    if response.status_code == 404:
        _handle_404_error(repo, "Repository")
    
    if not response.ok:
        _handle_generic_error(response, repo, "to get repository info")
    
    return response.json()


def get_branch_sha(token: str, repo: str, branch: str) -> str:
    """Get SHA of a branch's HEAD commit.
    
    Args:
        token: GitHub Personal Access Token for authentication.
        repo: Repository in format "owner/repo" (e.g., "Brndn004/squatting_in_the_texting_rack").
        branch: Branch name (e.g., "main", "master").
        
    Returns:
        SHA string of the branch's HEAD commit.
        
    Raises:
        ValueError: If token, repo, or branch is empty, or if repo format is invalid.
        requests.RequestException: If API request fails.
        ValueError: If API returns an error (401, 404, etc.) with clear error message.
    """
    _validate_token(token)
    _validate_repo(repo)
    _validate_not_empty(branch, "Branch name")
    
    api_url = f"https://api.github.com/repos/{repo}/git/ref/heads/{branch}"
    headers = _build_headers(token)
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 401:
        _handle_401_error(repo)
    
    if response.status_code == 404:
        raise ValueError(f"Branch not found: {branch} in repository {repo}. Check that the branch exists.")
    
    if not response.ok:
        _handle_generic_error(response, repo, f"to get branch SHA for {branch}")
    
    ref_data = response.json()
    return _parse_branch_ref_response(ref_data)


def create_branch(token: str, repo: str, branch_name: str, base_branch_sha: str) -> None:
    """Create a new branch from a base branch SHA.
    
    Args:
        token: GitHub Personal Access Token for authentication.
        repo: Repository in format "owner/repo" (e.g., "Brndn004/squatting_in_the_texting_rack").
        branch_name: Name of the new branch to create.
        base_branch_sha: SHA of the base branch to create from.
        
    Raises:
        ValueError: If token, repo, branch_name, or base_branch_sha is empty, or if repo format is invalid.
        requests.RequestException: If API request fails.
        ValueError: If API returns an error (401, 404, etc.) with clear error message.
        Note: If branch already exists (422 with "already exists" message), this is silently ignored.
    """
    _validate_token(token)
    _validate_repo(repo)
    _validate_not_empty(branch_name, "Branch name")
    _validate_not_empty(base_branch_sha, "Base branch SHA")
    
    api_url = f"https://api.github.com/repos/{repo}/git/refs"
    headers = _build_headers(token, include_content_type=True)
    
    request_body = {
        "ref": f"refs/heads/{branch_name}",
        "sha": base_branch_sha
    }
    
    response = requests.post(api_url, headers=headers, json=request_body)
    
    if response.status_code == 401:
        _handle_401_error(repo)
    
    if response.status_code == 404:
        raise ValueError(f"Repository or base branch not found: {repo}. Check that the repository exists and the base branch SHA is valid.")
    
    if response.status_code == 422:
        if _handle_422_branch_exists_error(response, branch_name, repo):
            return
    
    if not response.ok:
        _handle_generic_error(response, repo, f"to create branch {branch_name}")


def get_file_content(token: str, repo: str, path: str, branch: Optional[str] = None) -> dict:
    """Get file content from GitHub.
    
    Args:
        token: GitHub Personal Access Token for authentication.
        repo: Repository in format "owner/repo" (e.g., "Brndn004/squatting_in_the_texting_rack").
        path: File path in repository (e.g., "fitness/workout_logs/workout.json").
        branch: Optional branch name. If None, uses default branch.
        
    Returns:
        Dictionary containing file content information including 'content' (base64 encoded) and 'sha'.
        
    Raises:
        ValueError: If token, repo, or path is empty, or if repo format is invalid.
        requests.RequestException: If API request fails.
        ValueError: If API returns an error (401, 404, etc.) with clear error message.
    """
    _validate_token(token)
    _validate_repo(repo)
    _validate_not_empty(path, "File path")
    
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = _build_headers(token)
    
    params = {}
    if branch:
        params["ref"] = branch
    
    response = requests.get(api_url, headers=headers, params=params)
    
    if response.status_code == 401:
        _handle_401_error(repo)
    
    if response.status_code == 404:
        branch_info = f" on branch {branch}" if branch else ""
        raise ValueError(f"File not found: {path} in repository {repo}{branch_info}. Check that the file exists.")
    
    if not response.ok:
        _handle_generic_error(response, repo, f"to get file content for {path}")
    
    return response.json()


def create_or_update_file(
    token: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: str,
    sha: Optional[str] = None
) -> dict:
    """Create or update file via GitHub API.
    
    Important: Branch must already exist (use create_branch() first).
    If updating an existing file, provide the sha parameter.
    
    Args:
        token: GitHub Personal Access Token for authentication.
        repo: Repository in format "owner/repo" (e.g., "Brndn004/squatting_in_the_texting_rack").
        path: File path in repository (e.g., "fitness/workout_logs/workout.json").
        content: File content as a string (will be base64 encoded).
        message: Commit message.
        branch: Branch name (must already exist).
        sha: Optional SHA of existing file (required for updates, omit for new files).
        
    Returns:
        Dictionary containing commit information.
        
    Raises:
        ValueError: If token, repo, path, content, message, or branch is empty, or if repo format is invalid.
        requests.RequestException: If API request fails.
        ValueError: If API returns an error (401, 404, etc.) with clear error message.
    """
    _validate_token(token)
    _validate_repo(repo)
    _validate_not_empty(path, "File path")
    _validate_not_empty(content, "File content")
    _validate_not_empty(message, "Commit message")
    _validate_not_empty(branch, "Branch name")
    
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = _build_headers(token, include_content_type=True)
    
    content_bytes = content.encode("utf-8")
    content_base64 = base64.b64encode(content_bytes).decode("utf-8")
    
    request_body = {
        "message": message,
        "content": content_base64,
        "branch": branch
    }
    
    if sha:
        request_body["sha"] = sha
    
    response = requests.put(api_url, headers=headers, json=request_body)
    
    if response.status_code == 401:
        _handle_401_error(repo)
    
    if response.status_code == 404:
        raise ValueError(f"Branch not found: {branch} in repository {repo}. Branch must exist before creating files. Use create_branch() first.")
    
    if response.status_code == 422:
        _handle_422_file_error(response, path, repo)
    
    if not response.ok:
        _handle_generic_error(response, repo, f"to create/update file {path}")
    
    return response.json()
