from fastapi import FastAPI

from routers.feedback import feedback_router


app = FastAPI(
    title="Product Feedback Intelligence API",
    description="Backend service for analysing customer feedback and supporting product planning.",
    version="0.1.0"
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