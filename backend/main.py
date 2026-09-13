from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.feedback import feedback_router
from backend.routers.insights import insights_router
from database.connection import (
    connect_to_mongodb,
    close_mongodb_connection,
    get_database,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await connect_to_mongodb()
        print("MongoDB connected to FastAPI")
    except Exception as error:
        print(f"MongoDB connection unavailable: {error}")

    yield

    await close_mongodb_connection()
    print("MongoDB connection closed")


app = FastAPI(
    title="Product Feedback Intelligence API",
    description=(
        "Backend service for analysing customer feedback "
        "and supporting product planning."
    ),
    version="0.2.0",
    lifespan=lifespan,
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
app.include_router(insights_router)


@app.get("/")
def home():
    return {
        "message": "Product Feedback Intelligence API is running",
        "status": "active",
    }


@app.get("/health")
def health_check():
    try:
        get_database()
        database_status = "connected"
    except RuntimeError:
        database_status = "unavailable"

    return {
        "service": "backend",
        "status": "healthy",
        "database_status": database_status,
    }