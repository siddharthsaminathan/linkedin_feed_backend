from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from jobtech_client import JobTechClient
from typing import Optional, Dict, Any, List
import logging
from sqlalchemy.orm import Session
from database import init_db, get_db, Job
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="JobTech API Client")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the client
client = JobTechClient()

# Initialize database
init_db()

@app.get("/search")
async def search_jobs(
    query: Optional[str] = Query(None, description="Search query"),
    offset: int = Query(0, description="Pagination offset"),
    limit: int = Query(10, description="Number of results per page"),
    occupation: Optional[str] = Query(None, description="Occupation filter"),
    municipality: Optional[str] = Query(None, description="Municipality filter"),
    region: Optional[str] = Query(None, description="Region filter"),
    employment_type: Optional[str] = Query(None, description="Employment type filter"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Search for jobs using the JobTech API and store results in database"""
    try:
        logger.info(f"Search request - query: {query}, offset: {offset}, limit: {limit}")
        
        # Build search parameters
        search_params = {
            "query": query,
            "offset": offset,
            "limit": limit
        }
        
        # Add optional filters if provided
        if occupation:
            search_params["occupation"] = occupation
        if municipality:
            search_params["municipality"] = municipality
        if region:
            search_params["region"] = region
        if employment_type:
            search_params["employment_type"] = employment_type
            
        # Get results from JobTech API
        result = client.search_jobs(**search_params)
        logger.debug(f"Search result: {result}")
        
        # Store jobs in database
        if "hits" in result:
            for hit in result["hits"]:
                # Check if job already exists
                existing_job = db.query(Job).filter(Job.job_id == hit["id"]).first()
                if existing_job:
                    # Update existing job
                    for key, value in hit.items():
                        if hasattr(existing_job, key):
                            setattr(existing_job, key, value)
                    existing_job.updated_at = datetime.utcnow()
                else:
                    # Create new job
                    job_data = {
                        "job_id": hit["id"],
                        "external_id": hit.get("external_id"),
                        "original_id": hit.get("original_id"),
                        "headline": hit.get("headline", ""),
                        "description": hit.get("description", {}).get("text", ""),
                        "webpage_url": hit.get("webpage_url", ""),
                        "logo_url": hit.get("logo_url"),
                        "application_deadline": datetime.fromisoformat(hit["application_deadline"]) if hit.get("application_deadline") else None,
                        "number_of_vacancies": hit.get("number_of_vacancies", 1),
                        "employer": hit.get("employer", {}),
                        "workplace_address": hit.get("workplace_address", {}),
                        "must_have": hit.get("must_have", {}),
                        "nice_to_have": hit.get("nice_to_have", {}),
                        "employment_type": hit.get("employment_type", {}).get("label", ""),
                        "salary_type": hit.get("salary_type", {}).get("label", ""),
                        "salary_description": hit.get("salary_description", ""),
                        "duration": hit.get("duration", {}).get("label", ""),
                        "working_hours_type": hit.get("working_hours_type", {}).get("label", ""),
                        "scope_of_work": hit.get("scope_of_work", 100)
                    }
                    new_job = Job(**job_data)
                    db.add(new_job)
            
            # Commit changes to database
            db.commit()
        
        return result
    except Exception as e:
        logger.error(f"Error in search_jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs")
async def get_jobs(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get jobs from local database"""
    try:
        jobs = db.query(Job).offset(skip).limit(limit).all()
        return [job.__dict__ for job in jobs]
    except Exception as e:
        logger.error(f"Error in get_jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get a specific job ad by ID from local database"""
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            # If not found in local DB, fetch from JobTech API
            result = client.get_job_ad(job_id)
            # Store in database
            job_data = {
                "job_id": result["id"],
                "external_id": result.get("external_id"),
                "original_id": result.get("original_id"),
                "headline": result.get("headline", ""),
                "description": result.get("description", {}).get("text", ""),
                "webpage_url": result.get("webpage_url", ""),
                "logo_url": result.get("logo_url"),
                "application_deadline": datetime.fromisoformat(result["application_deadline"]) if result.get("application_deadline") else None,
                "number_of_vacancies": result.get("number_of_vacancies", 1),
                "employer": result.get("employer", {}),
                "workplace_address": result.get("workplace_address", {}),
                "must_have": result.get("must_have", {}),
                "nice_to_have": result.get("nice_to_have", {}),
                "employment_type": result.get("employment_type", {}).get("label", ""),
                "salary_type": result.get("salary_type", {}).get("label", ""),
                "salary_description": result.get("salary_description", ""),
                "duration": result.get("duration", {}).get("label", ""),
                "working_hours_type": result.get("working_hours_type", {}).get("label", ""),
                "scope_of_work": result.get("scope_of_work", 100)
            }
            job = Job(**job_data)
            db.add(job)
            db.commit()
        return job.__dict__
    except Exception as e:
        logger.error(f"Error in get_job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job/{job_id}/logo")
async def get_job_logo(job_id: str):
    """Get the logo for a specific job ad"""
    try:
        logger.info(f"Get logo request - job_id: {job_id}")
        logo_data = client.get_job_logo(job_id)
        return {"logo": logo_data}
    except Exception as e:
        logger.error(f"Error in get_job_logo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/suggestions")
async def get_suggestions(
    query: Optional[str] = Query(None, description="Search query for suggestions"),
    limit: int = Query(10, description="Maximum number of suggestions"),
    contextual: bool = Query(True, description="Whether to use contextual suggestions")
) -> Dict[str, Any]:
    """Get search suggestions/typeahead results"""
    try:
        if not query:
            return {"suggestions": []}
            
        logger.info(f"Get suggestions request - query: {query}, limit: {limit}, contextual: {contextual}")
        result = client.get_suggestions(query=query, limit=limit, contextual=contextual)
        logger.debug(f"Suggestions result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in get_suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001) 