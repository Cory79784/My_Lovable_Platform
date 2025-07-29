import os
import json
import random
import zipfile
import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import subprocess
import tempfile
import shutil
from pathlib import Path

router = APIRouter()

class ProjectInfo(BaseModel):
    project_name: str
    status: str
    files: List[str]
    main_file: Optional[str] = None

# Base directory for generated projects
BASE_PROJECTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../gpt_projects"))

def get_project_path(project_name: str) -> str:
    """Get the full path to a project directory"""
    return os.path.join(BASE_PROJECTS_DIR, project_name)

def get_project_files(project_path: str) -> List[str]:
    """Get list of files in a project directory"""
    if not os.path.exists(project_path):
        return []
    
    files = []
    for root, dirs, filenames in os.walk(project_path):
        # Skip node_modules and other build directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', '.next', 'build', '.git'] and not d.startswith('.')]
        
        for filename in filenames:
            # Skip hidden files and common build artifacts
            if not filename.startswith('.') and filename not in ['__pycache__']:
                rel_path = os.path.relpath(os.path.join(root, filename), project_path)
                files.append(rel_path)
    return files

def find_main_file(project_path: str) -> Optional[str]:
    """Find the main entry file for the project"""
    common_main_files = [
        'index.html', 'main.html', 'app.html',
        'main.py', 'app.py', 'index.py',
        'main.js', 'app.js', 'index.js',
        'main.ts', 'app.ts', 'index.ts',
        'package.json', 'requirements.txt'
    ]
    
    for file in common_main_files:
        if os.path.exists(os.path.join(project_path, file)):
            return file
    return None

@router.get("/projects")
async def list_projects():
    """List all generated projects"""
    try:
        projects = []
        if os.path.exists(BASE_PROJECTS_DIR):
            for project_name in os.listdir(BASE_PROJECTS_DIR):
                project_path = get_project_path(project_name)
                if os.path.isdir(project_path):
                    files = get_project_files(project_path)
                    main_file = find_main_file(project_path)
                    
                    projects.append(ProjectInfo(
                        project_name=project_name,
                        status="completed" if files else "empty",
                        files=files,
                        main_file=main_file
                    ))
        
        return {"projects": [p.dict() for p in projects]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_name}")
async def get_project_info(project_name: str):
    """Get information about a specific project"""
    try:
        project_path = get_project_path(project_name)
        if not os.path.exists(project_path):
            raise HTTPException(status_code=404, detail="Project not found")
        
        files = get_project_files(project_path)
        main_file = find_main_file(project_path)
        
        return ProjectInfo(
            project_name=project_name,
            status="completed" if files else "empty",
            files=files,
            main_file=main_file
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_name}/files")
async def get_project_files_list(project_name: str):
    """Get list of files in a project"""
    try:
        project_path = get_project_path(project_name)
        if not os.path.exists(project_path):
            raise HTTPException(status_code=404, detail="Project not found")
        
        files = get_project_files(project_path)
        return {"files": files}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_name}/files/{file_path:path}")
async def get_project_file(project_name: str, file_path: str):
    """Get a specific file from a project"""
    try:
        project_path = get_project_path(project_name)
        full_file_path = os.path.join(project_path, file_path)
        
        # Security check: ensure the file is within the project directory
        if not os.path.abspath(full_file_path).startswith(os.path.abspath(project_path)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not os.path.exists(full_file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(full_file_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_name}/preview")
async def get_project_preview(project_name: str):
    """Get project preview HTML"""
    project_path = os.path.join(BASE_PROJECTS_DIR, project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if it's a Vite project
    package_json_path = os.path.join(project_path, "package.json")
    vite_config_path = os.path.join(project_path, "vite.config.ts")
    
    if os.path.exists(package_json_path) and os.path.exists(vite_config_path):
        # For Vite projects, serve the actual built project
        dist_path = os.path.join(project_path, "dist")
        index_html_path = os.path.join(dist_path, "index.html")
        
        if os.path.exists(index_html_path):
            # Serve the built project
            with open(index_html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Rewrite asset paths to point to our backend
            content = content.replace('src="/', f'src="/api/projects/{project_name}/dist/')
            content = content.replace('href="/', f'href="/api/projects/{project_name}/dist/')
            
            return HTMLResponse(content=content)
        else:
            # If no built project, create a preview page with instructions
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{project_name} Preview</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        background: #0f0f23; 
                        min-height: 100vh; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        color: white; 
                    }}
                    .container {{
                        text-align: center;
                        max-width: 600px;
                        padding: 40px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    }}
                    .icon {{
                        font-size: 4rem;
                        margin-bottom: 20px;
                    }}
                    h1 {{
                        font-size: 2.5rem;
                        margin-bottom: 15px;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    }}
                    p {{
                        font-size: 1.2rem;
                        margin-bottom: 30px;
                        opacity: 0.9;
                        line-height: 1.6;
                    }}
                    .tech-stack {{
                        display: flex;
                        justify-content: center;
                        gap: 15px;
                        flex-wrap: wrap;
                        margin-top: 30px;
                    }}
                    .tech-badge {{
                        background: rgba(255, 255, 255, 0.2);
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-size: 0.9rem;
                        backdrop-filter: blur(5px);
                    }}
                    .note {{
                        margin-top: 30px;
                        padding: 20px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 10px;
                        font-size: 0.9rem;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">⚛️</div>
                    <h1>{project_name}</h1>
                    <p>A Vite React project</p>
                    
                    <div class="tech-stack">
                        <span class="tech-badge">Vite</span>
                        <span class="tech-badge">React</span>
                        <span class="tech-badge">TypeScript</span>
                        <span class="tech-badge">Tailwind CSS</span>
                    </div>
                    
                    <div class="note">
                        <strong>Note:</strong> This is a Vite React project. To run it locally, use:<br>
                        <code>npm install && npm run dev</code>
                    </div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
    
    # For regular HTML projects, serve the index.html if it exists
    index_path = os.path.join(project_path, "index.html")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    
    # If no index.html, create a simple file list
    files = []
    for root, dirs, filenames in os.walk(project_path):
        # Skip node_modules and other build directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', '.next', 'build', '.git'] and not d.startswith('.')]
        
        for filename in filenames:
            if not filename.startswith('.') and filename not in ['__pycache__']:
                rel_path = os.path.relpath(os.path.join(root, filename), project_path)
                files.append(rel_path)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{project_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ padding: 5px 0; border-bottom: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <h1>Project: {project_name}</h1>
        <h2>Files:</h2>
        <ul>
            {''.join(f'<li>{file}</li>' for file in sorted(files))}
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.delete("/projects/{project_name}")
async def delete_project(project_name: str):
    """Delete a project"""
    try:
        project_path = get_project_path(project_name)
        if not os.path.exists(project_path):
            raise HTTPException(status_code=404, detail="Project not found")
        
        shutil.rmtree(project_path)
        return {"message": f"Project {project_name} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/projects/{project_name}/serve")
async def serve_project(project_name: str):
    """Start a local server for a project (if it's a web project)"""
    try:
        project_path = get_project_path(project_name)
        if not os.path.exists(project_path):
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if it's a web project (has HTML files)
        html_files = [f for f in get_project_files(project_path) if f.endswith('.html')]
        if not html_files:
            raise HTTPException(status_code=400, detail="No HTML files found in project")
        
        # For now, return the preview URL
        # In a real implementation, you might start a local server
        return {
            "message": "Project ready for preview",
            "preview_url": f"/api/projects/{project_name}/preview"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/community-projects")
async def get_community_projects():
    """Get list of community projects from gpt_projects folder"""
    try:
        projects = []
        
        print(f"Scanning directory: {BASE_PROJECTS_DIR}")
        
        # Define community projects (only show actual, complete projects)
        community_projects = [
            "sample-portfolio",
            "todo-app", 
            "weather-dashboard",
            "crypto-trade-template-2397-main"
        ]
        
        # Scan only community projects
        for project_name in community_projects:
            project_path = get_project_path(project_name)
            print(f"Checking community project: {project_name} at {project_path}")
            
            if os.path.isdir(project_path):
                # Check if project has proper web files for preview
                has_index_html = os.path.exists(os.path.join(project_path, "index.html"))
                has_dist = os.path.exists(os.path.join(project_path, "dist"))
                has_package_json = os.path.exists(os.path.join(project_path, "package.json"))
                
                # Check if it's a Vite/Next.js project that needs building
                is_vite_project = has_package_json and os.path.exists(os.path.join(project_path, "vite.config.ts"))
                is_nextjs_project = has_package_json and os.path.exists(os.path.join(project_path, "next.config.js"))
                
                # Project is previewable if it has index.html, dist directory, or is a buildable project
                is_previewable = has_index_html or has_dist or is_vite_project or is_nextjs_project
                
                print(f"  Project {project_name}: has_index_html={has_index_html}, has_dist={has_dist}, is_previewable={is_previewable}")
                
                # Read main_prompt for description
                prompt_path = os.path.join(project_path, "main_prompt")
                description = "A community project"
                if os.path.exists(prompt_path):
                    try:
                        with open(prompt_path, 'r', encoding='utf-8') as f:
                            prompt_content = f.read().strip()
                            description = prompt_content[:100] + "..." if len(prompt_content) > 100 else prompt_content
                    except:
                        pass
                
                # Create project data
                project_data = {
                    "id": project_name,
                    "name": project_name.replace("-", " ").title(),
                    "description": description,
                    "category": "Website",
                    "remixes": f"{random.randint(100, 9999)} Remixes",
                    "thumbnail": f"/api/projects/preview/{project_name}" if is_previewable else None,
                    "author": "Community",
                    "has_web_files": is_previewable,
                    "project_path": project_name,
                    "is_previewable": is_previewable
                }
                projects.append(project_data)
                print(f"  Added community project: {project_name} (previewable: {is_previewable})")
        
        print(f"Total community projects found: {len(projects)}")
        return projects
        
    except Exception as e:
        print(f"Error getting community projects: {e}")
        return [] 

@router.get("/projects/{project_name}/download")
async def download_project(project_name: str):
    """Download project as ZIP file including all files"""
    project_path = os.path.join(BASE_PROJECTS_DIR, project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(project_path):
            # Skip node_modules and other large directories for faster download
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git'] and not d.startswith('.')]
            
            for file in files:
                # Skip large files that aren't essential
                if file in ['package-lock.json', 'bun.lockb']:
                    continue
                    
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, project_path)
                zip_file.write(file_path, arc_name)
    
    zip_buffer.seek(0)
    
    return FileResponse(
        io.BytesIO(zip_buffer.getvalue()),
        media_type='application/zip',
        filename=f"{project_name}.zip"
    )

@router.get("/projects/{project_name}/dist/{file_path:path}")
async def get_project_dist_file(project_name: str, file_path: str):
    """Serve files from the dist directory of a project"""
    project_path = os.path.join(BASE_PROJECTS_DIR, project_name)
    dist_file_path = os.path.join(project_path, "dist", file_path)
    
    if not os.path.exists(dist_file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(dist_file_path) 