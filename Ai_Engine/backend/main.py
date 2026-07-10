from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# استدعاء الراوترز بتاعتنا
from routers.cv_router import router as cv_router
from routers.interview_router import router as interview_router

load_dotenv()

app = FastAPI(title="AcuHire Core Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ربط الراوترز بالسيرفر الأساسي
app.include_router(cv_router)
app.include_router(interview_router)

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)