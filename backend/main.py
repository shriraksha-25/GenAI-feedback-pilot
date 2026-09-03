from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.feedback import feedback_router


app = FastAPI(
    title="Product Feedback Intelligence API",
    description="Backend service for analysing customer feedback and supporting product planning.",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(feedback_router)


@app.get("/")
def home():
    return {
        "message": "Product Feedback Intelligence API is running",
        "status": "active"
    }


@app.get("/health")
def health_check():
    return {
        "service": "backend",
        "status": "healthy"
    }