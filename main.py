import os
import sys

# Force absolute path resolution of project root for cloud environments
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import engine, get_db_status, Base
from backend.schemas import DatabaseStatusResponse

# Import Decoupled Face Analyzer Modules
from backend import scanner
from backend import history
from backend import analytics

# Initialize FastAPI Root Application
app = FastAPI(
    title="AI Face Analyzer - Main Application Suite",
    description="Decoupled Modular Enterprise Suite for Computer Vision Face Scanning & Analytics.",
    version="3.0.0"
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Storage Folders in Root (for uploads and scans)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(ROOT_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount Image static server
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Dynamic DB Initializer
@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        print("Face analysis database tables initialized successfully.")
    except Exception as e:
        print(f"Error during database schema initialization: {e}")

# Register APIRouters
app.include_router(scanner.router)
app.include_router(history.router)
app.include_router(analytics.router)

# Expose global DB status check
@app.get("/api/db-status", response_model=DatabaseStatusResponse)
def db_status():
    """Get status of active PostgreSQL database / SQLite fallback."""
    return get_db_status()


# ==========================================================================
# MULTI-PAGE FRONTEND ROUTER (HTML WEB LINKS)
# ==========================================================================

FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

@app.get("/")
@app.get("/scanner")
def serve_scanner():
    """Serves the main interactive Face Scanner HTML dashboard."""
    index_path = os.path.join(FRONTEND_DIR, "scanner.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Scanner UI module not found inside frontend/ directory."}

@app.get("/history")
def serve_history():
    """Serves the History logs list HTML module."""
    index_path = os.path.join(FRONTEND_DIR, "history.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "History UI module not found inside frontend/ directory."}

@app.get("/analytics")
def serve_analytics():
    """Serves the Chart.js visual statistics HTML module."""
    index_path = os.path.join(FRONTEND_DIR, "analytics.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Analytics UI module not found inside frontend/ directory."}
