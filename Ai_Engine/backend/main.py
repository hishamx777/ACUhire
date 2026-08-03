import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import all modular routers
from routers.cv_router import router as cv_router
from routers.interview_router import router as interview_router
from routers.interview_ws import router as interview_ws_router
from routers.proctoring_api import router as proctoring_router

# Load environment variables (.env file)
load_dotenv()

# Configure production-level logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the main FastAPI application
app = FastAPI(
    title="AcuHire Core Engine",
    description="Enterprise-grade backend for AI-driven real-time interviews, CV processing, and security proctoring.",
    version="1.0.0"
)

# Configure Cross-Origin Resource Sharing (CORS) for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Note: Restrict this to your actual frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register application routers with descriptive tags for Swagger UI
app.include_router(cv_router, tags=["CV Analysis Pipeline"])
app.include_router(interview_router, tags=["Interview Setup & Management"])
app.include_router(interview_ws_router, tags=["Real-time Interview (WebSocket)"])
app.include_router(proctoring_router, tags=["Security & Proctoring"])

@app.get("/health", tags=["System Monitoring"])
async def health_check():
    """
    Health check endpoint for deployment monitoring.
    Used by load balancers and cloud providers to ensure the service is running.
    """
    return {"status": "healthy", "service": "AcuHire Core Engine is running smoothly."}

if __name__ == "__main__":
    import uvicorn
    # Using 0.0.0.0 allows external access, which is essential for deployment and network testing
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
