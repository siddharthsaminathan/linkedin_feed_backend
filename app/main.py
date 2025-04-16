from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db
from .feed_service import LinkedInFeedService
from pydantic import BaseModel
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LinkedIn Feed API",
    description="Backend API for LinkedIn-like feed application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize feed service
feed_service = None

class JobRoleRequest(BaseModel):
    role_name: str
    rss_url: str

@app.on_event("startup")
async def startup_event():
    global feed_service
    db = next(get_db())
    feed_service = LinkedInFeedService(db)
    feed_service.start_scheduler()
    logger.info("Feed service initialized and scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    if feed_service:
        feed_service.stop_scheduler()
        logger.info("Feed service stopped")

@app.post("/job-roles/")
async def add_job_role(role: JobRoleRequest, db: Session = Depends(get_db)):
    """Add a new job role to monitor"""
    if not feed_service:
        raise HTTPException(status_code=500, detail="Feed service not initialized")
    
    feed_service.add_job_role(role.role_name, role.rss_url)
    return {"message": f"Job role {role.role_name} added successfully"}

@app.get("/job-roles/")
async def get_job_roles():
    """Get all monitored job roles"""
    if not feed_service:
        raise HTTPException(status_code=500, detail="Feed service not initialized")
    
    return {"job_roles": list(feed_service.job_roles.keys())}

@app.delete("/job-roles/{role_name}")
async def remove_job_role(role_name: str):
    """Remove a job role from monitoring"""
    if not feed_service:
        raise HTTPException(status_code=500, detail="Feed service not initialized")
    
    if role_name not in feed_service.job_roles:
        raise HTTPException(status_code=404, detail="Job role not found")
    
    del feed_service.job_roles[role_name]
    return {"message": f"Job role {role_name} removed successfully"}

@app.post("/feeds/fetch")
async def fetch_feeds_now():
    """Manually trigger feed fetching"""
    if not feed_service:
        raise HTTPException(status_code=500, detail="Feed service not initialized")
    
    feed_service.fetch_all_feeds()
    return {"message": "Feed fetching completed"}

@app.get("/")
async def root():
    return {"message": "Welcome to LinkedIn Feed API"} 