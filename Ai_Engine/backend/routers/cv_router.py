import os
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, Field
from pipelines.cv_pipeline import RAGPipeline

router = APIRouter(
    prefix="/cv",
    tags=["CV Analysis System"]
)

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Initialize the RAG Engine
rag = RAGPipeline()

class AskPayload(BaseModel):
    question: str
    k: Optional[int] = Field(default=8, gt=0) 
    temperature: Optional[float] = Field(default=None, ge=0.0)

# --- Background Task Worker ---
def process_cv_background_task(pdf_path: str, job_description: str):
    print(f"Starting background evaluation for {pdf_path}...")
    result = rag.evaluate_single_cv(pdf_path, job_description)
    print(f"Evaluation finished for {pdf_path}. Score: {result.get('match_score')}")
    # الزميل بتاع الباك إند هيكتب هنا كود حفظ النتيجة في الداتا بيز

# --- The API Endpoint ---
@router.post("/apply")
async def apply_for_job(
    background_tasks: BackgroundTasks, 
    job_description: str = Form(...), 
    file: UploadFile = File(...)
):
    dest = DATA_DIR / file.filename
    async with aiofiles.open(dest, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    background_tasks.add_task(process_cv_background_task, str(dest), job_description)

    return {
        "status": "success",
        "message": "CV uploaded successfully. Evaluation is running in the background.",
        "filename": file.filename
    }

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/stats")
async def stats():
    return rag.stats()

@router.post("/reset")
async def reset():
    rag.reset_index()
    return {"message": "Vector store cleared."}

@router.post("/params")
async def update_params(k: Optional[int] = Form(None), temperature: Optional[float] = Form(None)):
    updated = rag.set_params(k=k, temperature=temperature)
    return {"updated": updated}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    dest = DATA_DIR / file.filename
    async with aiofiles.open(dest, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    summary = rag.add_file(str(dest))
    return {"message": "File ingested.", **summary}

@router.post("/ask")
async def ask(payload: AskPayload):
    if payload.k is not None or payload.temperature is not None:
        rag.set_params(k=payload.k, temperature=payload.temperature)
    res = rag.ask(payload.question)
    return res