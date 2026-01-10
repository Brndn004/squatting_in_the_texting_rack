"""An MCP server for ADP dev container commands.
Instead of having the Cursor agent run commands for you, this MCP server
provides a set of tools for the Cursor agent to use.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
from typing import Any, List

from mcp.server import fastmcp

# Initialize FastMCP server.
mcp = fastmcp.FastMCP("ADP Dev Docker Commands")

def _dict_to_json_string(d: dict[str, Any]) -> str:
    """Convert a dictionary to a JSON string."""
    return json.dumps(d)


def _run_command(command: List[str], cwd: str, passthrough_errors: bool) -> dict[str, Any]:
    """Run a command and return the result as a dictionary.

    Args:
        command: The command to run as a list of strings.
        cwd: The working directory to run the command in.
        passthrough_errors: If True, provide the full stdout and stderr instead
            of returning just "failure". Useful when you expect the subprocess
            call to return a non-zero exit code and need the output, for
            instance if a Bazel test fails.

    Returns:
        A dictionary containing stdout, stderr, and status.
    """
    try:
        # For reasons not entirely clear to me, if we try to capture the output here
        # the process hangs. Use temporary files for stdout and stderr to avoid it.
        stdout = ""
        stderr = ""
        with tempfile.TemporaryFile(mode="w+t") as stdout_file:
            with tempfile.TemporaryFile(mode="w+t") as stderr_file:
                completed_process = subprocess.run(
                    command,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    text=True,
                    check=not passthrough_errors,
                    cwd=cwd,
                )

                # Read output from temporary files.
                stdout_file.seek(0)
                stderr_file.seek(0)
                stdout = stdout_file.read()
                stderr = stderr_file.read()

        # Create an output structured as json for the agent to read.
        result = {"stdout": stdout, "stderr": stderr, "status": "failure"}
        if completed_process.returncode == 0:
            result["status"] = "success"
    except Exception as e:
        result = {
            "stdout": "",
            "stderr": str(e),
            "status": "failure",
        }

    return result


@mcp.tool(
    description=(
        "Run a Bazel test by directly calling `docker exec` on the specified "
        "container. This will execute the test using the provided Bazel target. "
        "For example, '//adp/sim/base:time_test'. You should check the "
        "`success` key in the returned JSON string to determine if the function "
        "call was successful. You also need to check the `stdout` key in the "
        "returned JSON string to determine if the tests passed or failed."
        ""
        "This should usually be run in a container named *_dev, e.g. "
        "applied_dev. If no container named *_dev exists, ask the user which "
        "container to use."
    )
)
async def bazel_test(bazel_target: str, docker_name: str) -> str:
    """Run a Bazel test inside the specified container.

    Args:
        bazel_target: The Bazel target to test, e.g. '//adp/sim/base:time_test'.
        docker_name: The name of the docker container to execute the command in.

    Returns:
        A JSON string containing the result of the command.
    """
    user = os.getlogin()
    command = [
        "docker",
        "exec",
        "-t",
        "-u",
        user,
        docker_name,
        "bash",
        "-e",
        "-c",
        f"bazel test {bazel_target}",
    ]
    passthrough_errors = True
    cwd = pathlib.Path.cwd()
    result = _run_command(command, cwd, passthrough_errors)
    return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get the current working directory of the MCP server process. This can "
        "be useful for debugging path-related issues."
    )
)
async def get_cwd() -> str:
    """Get the current working directory of the server process."""
    cwd = pathlib.Path.cwd()
    result = {
        "cwd": str(cwd),
        "status": "success",
    }
    return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Use this tool to run arbitrary commands inside a Docker container. "
        "This will execute the command using `docker exec` on the specified "
        "container."
        ""
        "You should use this tool when you need to run commands inside a "
        "development container (e.g., primary_dev, applied_dev)."
        ""
        "The command will be executed in the specified working directory "
        "inside the container. The user will be set to the current host user."
        ""
        "If you expect the command to return a non-zero exit code, set "
        "passthrough_errors to True to capture all output."
    )
)
async def run_in_container(
    command: List[str], docker_name: str, cwd: str, passthrough_errors: bool
) -> str:
    """Run an arbitrary command inside a Docker container.

    Args:
        command: The command to run as a list of strings.
        docker_name: The name of the docker container to execute the command in.
        cwd: The working directory to run the command in (inside the container).
        passthrough_errors: If True, provide the full stdout and stderr instead
            of returning just "failure".

    Returns:
        A JSON string containing the result of the command.
    """
    user = os.getlogin()
    # Join command list into a single string for bash -c
    command_str = " ".join(command)
    docker_command = [
        "docker",
        "exec",
        "-t",
        "-u",
        user,
        "-w",
        cwd,
        docker_name,
        "bash",
        "-e",
        "-c",
        command_str,
    ]
    result = _run_command(docker_command, pathlib.Path.cwd(), passthrough_errors)
    return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get the current Git branch name. Useful for determining which PR branch "
        "you're working on when looking up PR comments."
    )
)
async def get_current_branch() -> str:
    """Get the current Git branch name."""
    command = ["git", "branch", "--show-current"]
    cwd = pathlib.Path.cwd()
    result = _run_command(command, str(cwd), passthrough_errors=True)
    return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get the remote origin URL for the current Git repository. Useful for "
        "determining the GitHub repository when looking up PR information."
    )
)
async def get_git_remote_origin() -> str:
    """Get the remote origin URL."""
    command = ["git", "remote", "get-url", "origin"]
    cwd = pathlib.Path.cwd()
    result = _run_command(command, str(cwd), passthrough_errors=True)
    return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "List pull requests for the current repository using GitHub CLI. "
        "You can filter by state (open, closed, merged) and other criteria. "
        "Requires 'gh' CLI to be installed and authenticated."
    )
)
async def list_pull_requests(
    state: str = "open", 
    limit: int = 30,
    author: str = "",
    head: str = ""
) -> str:
    """List pull requests using GitHub CLI.
    
    Args:
        state: PR state filter (open, closed, merged, all)
        limit: Maximum number of PRs to return
        author: Filter by PR author
        head: Filter by head branch name
    """
    command = ["gh", "pr", "list", "--state", state, "--limit", str(limit)]
    
    if author:
        command.extend(["--author", author])
    if head:
        command.extend(["--head", head])
    
    # Add JSON output for easier parsing
    command.extend(["--json", "number,title,author,headRefName,state,url"])
    
    cwd = pathlib.Path.cwd()
    result = _run_command(command, str(cwd), passthrough_errors=True)
    return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get detailed information about a specific pull request using GitHub CLI. "
        "Requires the PR number and 'gh' CLI to be installed and authenticated."
    )
)
async def get_pull_request_details(pr_number: int) -> str:
    """Get detailed PR information including comments.
    
    Args:
        pr_number: The pull request number
    """
    command = [
        "gh", "pr", "view", str(pr_number), 
        "--json", "number,title,body,author,state,headRefName,baseRefName,url,comments"
    ]
    
    cwd = pathlib.Path.cwd()
    result = _run_command(command, str(cwd), passthrough_errors=True)
    return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get review comments for a specific pull request using GitHub CLI. "
        "These are the line-by-line code review comments, not general PR comments. "
        "Requires the PR number and 'gh' CLI to be installed and authenticated."
    )
)
async def get_pr_review_comments(pr_number: int) -> str:
    """Get review comments for a specific PR.
    
    Args:
        pr_number: The pull request number
    """
    command = [
        "gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/comments",
        "--jq", ".[].body"
    ]
    
    cwd = pathlib.Path.cwd()
    result = _run_command(command, str(cwd), passthrough_errors=True)
    return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Get all reviews for a specific pull request using GitHub CLI. "
        "This includes overall PR reviews (approve, request changes, comment) "
        "with their associated comments. Requires the PR number and 'gh' CLI."
    )
)
async def get_pr_reviews(pr_number: int) -> str:
    """Get all reviews for a specific PR.
    
    Args:
        pr_number: The pull request number
    """
    command = [
        "gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/reviews"
    ]
    
    cwd = pathlib.Path.cwd()
    result = _run_command(command, str(cwd), passthrough_errors=True)
    return _dict_to_json_string(result)


@mcp.tool(
    description=(
        "Find the pull request number for the current branch using GitHub CLI. "
        "Useful when you know you're on a PR branch but need to find the PR number "
        "to fetch comments."
    )
)
async def find_pr_for_current_branch() -> str:
    """Find the PR number for the current branch."""
    # First get current branch
    branch_command = ["git", "branch", "--show-current"]
    cwd = pathlib.Path.cwd()
    branch_result = _run_command(branch_command, str(cwd), passthrough_errors=True)
    
    if branch_result["status"] != "success":
        return _dict_to_json_string(branch_result)
    
    branch_name = branch_result["stdout"].strip()
    
    # Then find PR for this branch
    pr_command = [
        "gh", "pr", "list", "--head", branch_name, 
        "--json", "number,title,state", "--limit", "1"
    ]
    
    pr_result = _run_command(pr_command, str(cwd), passthrough_errors=True)
    return _dict_to_json_string(pr_result)


@mcp.tool(
    description=(
        "Get the GitHub repository owner and name from the current Git remote. "
        "Parses the remote URL to extract owner/repo format needed for GitHub API calls."
    )
)
async def get_github_repo_info() -> str:
    """Get GitHub repository owner and name."""
    command = ["git", "remote", "get-url", "origin"]
    cwd = pathlib.Path.cwd()
    result = _run_command(command, str(cwd), passthrough_errors=True)
    
    if result["status"] == "success":
        url = result["stdout"].strip()
        # Parse GitHub URL to extract owner/repo
        # Handle both SSH (git@github.com:owner/repo.git) and HTTPS (https://github.com/owner/repo.git)
        if "github.com" in url:
            if url.startswith("git@"):
                # SSH format: git@github.com:owner/repo.git
                repo_part = url.split(":")[-1].replace(".git", "")
            else:
                # HTTPS format: https://github.com/owner/repo.git
                repo_part = url.split("github.com/")[-1].replace(".git", "")
            
            if "/" in repo_part:
                owner, repo = repo_part.split("/", 1)
                result["owner"] = owner
                result["repo"] = repo
            else:
                result["error"] = "Could not parse owner/repo from URL"
        else:
            result["error"] = "Not a GitHub repository"
    
    return _dict_to_json_string(result)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
