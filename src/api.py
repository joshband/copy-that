"""
FastAPI Backend for Generative UI Builder.

Provides REST API endpoints for image upload, analysis, and component generation.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional, Dict, Any
from pathlib import Path
import shutil
import uuid
from datetime import datetime
import json

from .generation_pipeline import GenerativeUISystem
from pydantic import BaseModel


# Create FastAPI app
app = FastAPI(
    title="Copy That - Generative UI Builder API",
    description="Generate complete UI design systems from reference images",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# In-memory storage for projects (use database in production)
projects = {}


class ProjectRequest(BaseModel):
    """Request model for creating a project."""
    name: str
    use_openai: bool = True


class GenerateRequest(BaseModel):
    """Request model for generating design system."""
    components: Optional[List[str]] = None
    export_formats: Optional[List[str]] = ['css', 'json', 'tailwind']


class ComponentRequest(BaseModel):
    """Request model for generating custom component."""
    component_type: str
    variant: Optional[str] = 'primary'
    size: Optional[str] = 'md'
    state: Optional[str] = 'default'


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Copy That API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "projects": "/projects",
            "upload": "/projects/{project_id}/upload",
            "analyze": "/projects/{project_id}/analyze",
            "generate": "/projects/{project_id}/generate",
            "export": "/projects/{project_id}/export"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/projects")
async def create_project(request: ProjectRequest):
    """Create a new project."""
    project_id = str(uuid.uuid4())

    project = {
        "id": project_id,
        "name": request.name,
        "created_at": datetime.now().isoformat(),
        "status": "created",
        "images": [],
        "use_openai": request.use_openai,
        "analysis": None,
        "design_system": None
    }

    projects[project_id] = project

    # Create project directories
    project_dir = OUTPUT_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    return {"project_id": project_id, "project": project}


@app.get("/projects")
async def list_projects():
    """List all projects."""
    return {"projects": list(projects.values())}


@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    return projects[project_id]


@app.post("/projects/{project_id}/upload")
async def upload_images(
    project_id: str,
    files: List[UploadFile] = File(...)
):
    """Upload reference images to a project."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed")

    project = projects[project_id]
    uploaded_images = []

    # Create upload directory for this project
    upload_dir = UPLOAD_DIR / project_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        file_path = upload_dir / f"{file_id}{file_ext}"

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image_data = {
            "id": file_id,
            "filename": file.filename,
            "path": str(file_path),
            "uploaded_at": datetime.now().isoformat()
        }

        uploaded_images.append(image_data)
        project["images"].append(image_data)

    project["status"] = "images_uploaded"

    return {
        "project_id": project_id,
        "uploaded": len(uploaded_images),
        "images": uploaded_images
    }


@app.post("/projects/{project_id}/analyze")
async def analyze_project(project_id: str, background_tasks: BackgroundTasks):
    """Analyze uploaded images and extract visual DNA."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]

    if not project["images"]:
        raise HTTPException(status_code=400, detail="No images uploaded")

    # Use first image for analysis (could merge multiple in future)
    image_path = project["images"][0]["path"]

    try:
        # Initialize system
        system = GenerativeUISystem(use_openai=project["use_openai"])

        # Analyze reference image
        visual_dna = system.analyze_reference(image_path, include_ai=project["use_openai"])

        # Store results
        project["analysis"] = {
            "visual_dna": visual_dna,
            "ai_analysis": system.ai_analysis,
            "analyzed_at": datetime.now().isoformat()
        }

        project["status"] = "analyzed"

        # Store system for later use
        projects[f"{project_id}_system"] = system

        return {
            "project_id": project_id,
            "status": "analyzed",
            "visual_dna": visual_dna,
            "ai_analysis": system.ai_analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/projects/{project_id}/generate")
async def generate_design_system(project_id: str, request: GenerateRequest):
    """Generate design system from analysis."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]

    if not project["analysis"]:
        raise HTTPException(status_code=400, detail="Project not analyzed. Run analysis first.")

    try:
        # Get stored system or create new one
        system_key = f"{project_id}_system"
        if system_key in projects:
            system = projects[system_key]
        else:
            raise HTTPException(status_code=400, detail="System not found. Re-run analysis.")

        # Generate design system
        project_dir = OUTPUT_DIR / project_id
        component_library = system.generate_design_system(output_dir=project_dir)

        # Export in requested formats
        exported = system.export_design_system(
            output_dir=project_dir,
            formats=request.export_formats
        )

        # Get summary
        summary = system.get_summary()

        project["design_system"] = {
            "library": component_library.to_dict(),
            "exported_files": {k: str(v) for k, v in exported.items()},
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        }

        project["status"] = "generated"

        return {
            "project_id": project_id,
            "status": "generated",
            "summary": summary,
            "component_library": component_library.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/projects/{project_id}/components")
async def list_components(project_id: str):
    """List all generated components."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]

    if not project["design_system"]:
        raise HTTPException(status_code=400, detail="Design system not generated")

    library = project["design_system"]["library"]

    return {
        "project_id": project_id,
        "components": library.get("components", {})
    }


@app.get("/projects/{project_id}/components/{component_type}")
async def get_component(project_id: str, component_type: str):
    """Get specific component family."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]

    if not project["design_system"]:
        raise HTTPException(status_code=400, detail="Design system not generated")

    library = project["design_system"]["library"]
    components = library.get("components", {})

    if component_type not in components:
        raise HTTPException(status_code=404, detail=f"Component '{component_type}' not found")

    return {
        "project_id": project_id,
        "component_type": component_type,
        "component": components[component_type]
    }


@app.get("/projects/{project_id}/components/{component_type}/{variant_key}")
async def get_component_variant(project_id: str, component_type: str, variant_key: str):
    """Get specific component variant SVG."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]

    if not project["design_system"]:
        raise HTTPException(status_code=400, detail="Design system not generated")

    library = project["design_system"]["library"]
    components = library.get("components", {})

    if component_type not in components:
        raise HTTPException(status_code=404, detail=f"Component '{component_type}' not found")

    component = components[component_type]
    variants = component.get("variants", {})

    if variant_key not in variants:
        raise HTTPException(status_code=404, detail=f"Variant '{variant_key}' not found")

    return variants[variant_key]


@app.get("/projects/{project_id}/tokens")
async def get_design_tokens(project_id: str, format: str = 'json'):
    """Get design tokens in specified format."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]

    if not project["design_system"]:
        raise HTTPException(status_code=400, detail="Design system not generated")

    # Get token file
    project_dir = OUTPUT_DIR / project_id / 'tokens'

    if format == 'json':
        token_file = project_dir / 'tokens.json'
    elif format == 'css':
        token_file = project_dir / 'tokens.css'
    elif format == 'tailwind':
        token_file = project_dir / 'tailwind.config.js'
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    if not token_file.exists():
        raise HTTPException(status_code=404, detail="Token file not found")

    return FileResponse(
        token_file,
        media_type='application/json' if format == 'json' else 'text/plain',
        filename=token_file.name
    )


@app.post("/projects/{project_id}/export")
async def export_design_system(project_id: str, format: str = 'zip'):
    """Export complete design system as downloadable file."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]

    if not project["design_system"]:
        raise HTTPException(status_code=400, detail="Design system not generated")

    # Create zip file of entire project
    project_dir = OUTPUT_DIR / project_id
    zip_path = OUTPUT_DIR / f"{project_id}.zip"

    shutil.make_archive(str(zip_path.with_suffix('')), 'zip', project_dir)

    return FileResponse(
        zip_path,
        media_type='application/zip',
        filename=f"{project['name']}-design-system.zip"
    )


@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project and all its files."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete files
    upload_dir = UPLOAD_DIR / project_id
    output_dir = OUTPUT_DIR / project_id

    if upload_dir.exists():
        shutil.rmtree(upload_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)

    # Remove from memory
    del projects[project_id]
    system_key = f"{project_id}_system"
    if system_key in projects:
        del projects[system_key]

    return {"status": "deleted", "project_id": project_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
