import asyncio
import json
import uuid
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.config import settings
from app.services.parser import parse_document
from app.services.process_runner import process_manager
from app.services.generator import (
    generate_architecture_spec,
    refine_architecture_spec,
    run_generation_pipeline,
    get_generation_state,
    modify_generated_application
)

app = FastAPI(title="BRD-to-Application Copilot API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
def shutdown_event():
    """Ensure all spawned application processes are terminated on server shutdown."""
    process_manager.stop_all()

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "model": settings.LLM_MODEL,
        "base_url": settings.LLM_BASE_URL
    }

class GenerateArchitectureRequest(BaseModel):
    brd_text: str

class RefineArchitectureRequest(BaseModel):
    current_markdown: str
    instruction: str

class StartGenerationRequest(BaseModel):
    project_id: Optional[str] = None
    architecture: str

class ModifyRequest(BaseModel):
    project_id: str
    instruction: str

@app.post("/api/brd/parse")
async def parse_brd_file(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """Parse BRD from an uploaded file (PDF, DOCX, TXT) or raw form text."""
    if file and file.filename:
        content = await file.read()
        try:
            extracted = parse_document(file.filename, content)
            return {"text": extracted, "filename": file.filename}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    elif text and text.strip():
        return {"text": text.strip(), "filename": "Manual Entry"}
    else:
        raise HTTPException(status_code=400, detail="Please provide a valid document or text content.")

@app.post("/api/brd/generate-architecture")
async def generate_architecture_endpoint(payload: GenerateArchitectureRequest):
    """Screen 2: Generate detailed Functional & System Specification in Markdown from BRD."""
    if not payload.brd_text.strip():
        raise HTTPException(status_code=400, detail="BRD text is required.")
    try:
        markdown_spec = generate_architecture_spec(payload.brd_text)
        return {"architecture": markdown_spec}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Architecture generation failed: {str(e)}")

@app.post("/api/brd/refine-architecture")
async def refine_architecture_endpoint(payload: RefineArchitectureRequest):
    """Screen 2: Refine the architecture Markdown based on user input."""
    if not payload.instruction.strip():
        raise HTTPException(status_code=400, detail="Revision instruction is required.")
    try:
        updated_spec = refine_architecture_spec(payload.current_markdown, payload.instruction)
        return {"architecture": updated_spec}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

@app.post("/api/generate")
async def start_generation(payload: StartGenerationRequest, background_tasks: BackgroundTasks):
    """Screen 3: Start multi-agent application generation in the background."""
    project_id = payload.project_id or f"app_{uuid.uuid4().hex[:8]}"
    
    # Run the generation pipeline in background
    background_tasks.add_task(run_generation_pipeline, project_id, payload.architecture)
    
    return {
        "project_id": project_id,
        "status": "started",
        "message": "Multi-agent generation pipeline initialized."
    }

@app.get("/api/generation/status/{project_id}")
async def get_status(project_id: str):
    """Poll generation status."""
    return get_generation_state(project_id)

@app.get("/api/generation/stream/{project_id}")
async def stream_generation_events(project_id: str):
    """Server-Sent Events stream for real-time progress updates during generation."""
    async def event_generator():
        last_log_idx = 0
        while True:
            state = get_generation_state(project_id)
            logs = state.get("logs", [])
            new_logs = logs[last_log_idx:]
            
            data = {
                "status": state.get("status"),
                "step": state.get("step"),
                "port": state.get("port"),
                "new_logs": new_logs,
                "error": state.get("error")
            }
            last_log_idx = len(logs)
            yield f"data: {json.dumps(data)}\n\n"
            
            if state.get("status") in ("ready", "error"):
                break
            await asyncio.sleep(1.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/modify")
async def modify_application_endpoint(payload: ModifyRequest):
    """Screen 3: Apply modifications to running application and hot-reload."""
    try:
        result = modify_generated_application(payload.project_id, payload.instruction)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

