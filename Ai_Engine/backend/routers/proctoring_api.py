import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

# Configure production-level logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI Router
router = APIRouter()

class ProctoringFlag(BaseModel):
    """
    Schema for incoming proctoring alerts from the client-side YOLOv8n model.
    """
    interview_id: str = Field(..., description="Unique identifier for the interview session.")
    flag_type: str = Field(..., description="Type of violation: 'multiple_people', 'no_person', 'cell_phone'.")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the event.")
    details: str = Field(default="", description="Additional context, bounding box coordinates, or confidence score.")

def _save_flag_to_database(flag_data: ProctoringFlag) -> None:
    """
    Simulates saving the security flag to a persistent HR database.
    Designed to run as a background task.
    """
    # TODO: Replace with actual database insertion logic (e.g., SQLAlchemy / MongoDB)
    logger.warning(
        f"🚨 SECURITY ALERT | Interview: {flag_data.interview_id} | "
        f"Violation: {flag_data.flag_type.upper()} | "
        f"Time: {flag_data.timestamp}"
    )

@router.post("/api/proctoring/flag")
async def receive_proctoring_flag(flag: ProctoringFlag, background_tasks: BackgroundTasks):
    """
    Receives lightweight proctoring flags from the client's local YOLO model.
    Delegates the database I/O to a background task to maintain high throughput.
    """
    try:
        # Add the saving function to FastAPI's background task queue
        background_tasks.add_task(_save_flag_to_database, flag)
        
        return {"status": "success", "message": "Proctoring flag registered successfully."}
        
    except Exception as e:
        logger.error(f"Failed to process proctoring flag: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while processing security flag.")
