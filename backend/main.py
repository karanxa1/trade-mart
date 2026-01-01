# Trade Mart Backend - FastAPI Application
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
import os

from .routes import (
    auth_router,
    products_router,
    cart_router,
    orders_router,
    messages_router,
    offers_router,
    admin_router
)
from .models import init_firestore_data

app = FastAPI(
    title="Trade Mart API",
    description="Backend API for Trade Mart - Second-Hand Marketplace",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth_router)

# Logging Configuration
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("backend.log")
    ]
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Path: {request.url.path} Method: {request.method} Status: {response.status_code} Duration: {process_time:.4f}s")
    
    # Ensure CORS headers are always present
    origin = request.headers.get("origin")
    if origin in ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(messages_router)
app.include_router(offers_router)
app.include_router(admin_router)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'images', 'products')
if os.path.exists(UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.on_event("startup")
async def startup_event():
    try:
        init_firestore_data()
    except Exception as e:
        print(f"Error initializing Firestore: {e}")

@app.get("/")
async def root():
    return {
        "message": "Trade Mart API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.options("/{full_path:path}")
async def options_handler(full_path: str, request: Request):
    """Handle OPTIONS preflight requests"""
    origin = request.headers.get("origin")
    if origin in ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]:
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
            }
        )
    return Response(status_code=200)
