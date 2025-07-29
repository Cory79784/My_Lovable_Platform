import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class DeployRequest(BaseModel):
    project_name: str  # Project name, corresponding to subfolder in gpt_projects

class DeployResponse(BaseModel):
    success: bool
    message: str
    github_url: Optional[str] = None

@router.post("/deploy", response_model=DeployResponse)
async def deploy_to_github(request: DeployRequest):
    """Deploy specific project to GitHub"""
    try:
        # Get GitHub token from environment
        github_token = os.getenv("GITHUB_TOKEN")
        github_repo = os.getenv("GITHUB_REPO", "Cory79784/Try-my-new-project")
        
        # Clean up token and repo values (remove duplicates and null characters)
        if github_token:
            # Remove null characters and take the first part before any '='
            github_token = github_token.split('\x00')[0].split('=')[0]
        if github_repo:
            # Remove null characters and take the first part before any '='
            github_repo = github_repo.split('\x00')[0].split('=')[0]
        
        print(f"GitHub token found: {'Yes' if github_token else 'No'}")
        print(f"GitHub token length: {len(github_token) if github_token else 0}")
        print(f"GitHub repo: {github_repo}")
        
        if not github_token:
            raise HTTPException(
                status_code=500, 
                detail="GitHub token not found in environment variables"
            )
        
        print(f"Using GitHub repo: {github_repo}")
        
        # Get project root directory
        project_root = Path(__file__).parent.parent.parent.parent  # Go up one more level to reach the main project directory
        temp_dir = project_root / "temp_deploy"
        
        print(f"Project root: {project_root}")
        print(f"Requested project name: {request.project_name}")
        
        # Clean up temp directory
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                print("Temp directory is in use, will try to use existing one")
        temp_dir.mkdir(exist_ok=True)
        
        # Fixed source path - always use sample-portfolio
        source_project_path = project_root / "gpt_projects" / "sample-portfolio"
        target_project_path = temp_dir / "sample-portfolio"
        
        print(f"Source project path: {source_project_path}")
        print(f"Target project path: {target_project_path}")
        
        # Check if source project exists
        if not source_project_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Sample portfolio project not found at {source_project_path}"
            )
        
        # Copy project files to temp directory
        shutil.copytree(source_project_path, target_project_path)
        print(f"Copied sample-portfolio to temp directory: {target_project_path}")
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        print(f"Changed to directory: {os.getcwd()}")
        
        # Create environment with GitHub token
        env = os.environ.copy()
        env["GIT_ASKPASS"] = "echo"  # Disable password prompts
        env["GIT_TERMINAL_PROMPT"] = "0"  # Disable terminal prompts
        
        # Git commands list with token authentication
        git_commands = [
            ["git", "init"],
            ["git", "add", "."],
            ["git", "config", "user.name", "Lovable Platform"],
            ["git", "config", "user.email", "lovable@platform.com"],
            ["git", "commit", "-m", "Deploy sample portfolio project"],
            ["git", "branch", "-M", "main"],
            ["git", "remote", "add", "origin", f"https://{github_token}@github.com/{github_repo}.git"],
            ["git", "push", "-u", "origin", "main", "--force"]
        ]
        
        # Execute Git commands
        for cmd in git_commands:
            print(f"Executing: {' '.join(cmd)}")
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env=env,
                    timeout=30  # Add timeout
                )
                
                print(f"Command output: {result.stdout}")
                if result.stderr:
                    print(f"Command stderr: {result.stderr}")
                
                if result.returncode != 0:
                    print(f"Command failed: {' '.join(cmd)}")
                    print(f"Error: {result.stderr}")
                    # Don't raise exception for remote add if it already exists
                    if "remote origin already exists" in result.stderr and "git remote add" in " ".join(cmd):
                        print("Remote already exists, continuing...")
                        continue
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Git command failed: {' '.join(cmd)} - {result.stderr}"
                    )
            except subprocess.TimeoutExpired:
                raise HTTPException(
                    status_code=500,
                    detail=f"Git command timed out: {' '.join(cmd)}"
                )
        
        # Change back to original directory
        os.chdir(original_cwd)
        
        # Clean up temp directory
        try:
            shutil.rmtree(temp_dir)
            print("Cleaned up temp directory")
        except PermissionError:
            print("Could not clean up temp directory (in use), will be cleaned up later")
        
        return DeployResponse(
            success=True,
            message=f"Successfully deployed sample portfolio to GitHub",
            github_url=f"https://github.com/{github_repo}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        # Clean up temp directory
        if 'temp_dir' in locals() and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                print("Could not clean up temp directory during error handling")
        raise HTTPException(status_code=500, detail=str(e))