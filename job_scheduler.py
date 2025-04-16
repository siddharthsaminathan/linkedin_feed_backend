from database import SessionLocal, Job, init_db
from jobtech_client import JobTechClient
from datetime import datetime, timedelta
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_jobs():
    """Search for new jobs and update existing ones"""
    db = SessionLocal()
    client = JobTechClient()
    
    try:
        # Search for data engineer jobs
        search_params = {
            "query": "data engineer",
            "limit": 50
        }
        
        response = client.search_jobs(**search_params)
        jobs_data = response.get('hits', [])
        
        updated_count = 0
        new_count = 0
        
        for job_data in jobs_data:
            # Check if job already exists
            existing_job = db.query(Job).filter(Job.job_id == job_data['id']).first()
            
            if existing_job:
                # Update existing job
                for key, value in job_data.items():
                    if hasattr(existing_job, key):
                        setattr(existing_job, key, value)
                existing_job.last_updated = datetime.utcnow()
                updated_count += 1
            else:
                # Create new job
                new_job = Job(
                    job_id=job_data['id'],
                    headline=job_data.get('headline'),
                    description=job_data.get('description', {}).get('text', ''),
                    webpage_url=job_data.get('webpage_url'),
                    logo_url=job_data.get('logo_url'),
                    application_deadline=datetime.fromisoformat(job_data['application_deadline'].replace('Z', '+00:00')) if job_data.get('application_deadline') else None,
                    number_of_vacancies=job_data.get('number_of_vacancies', 1),
                    employer=job_data.get('employer', {}),
                    workplace_address=job_data.get('workplace_address', {}),
                    must_have=job_data.get('must_have', {}),
                    nice_to_have=job_data.get('nice_to_have', {}),
                    employment_type=job_data.get('employment_type', {}).get('label'),
                    salary_type=job_data.get('salary_type', {}).get('label'),
                    salary_description=job_data.get('salary_description'),
                    duration=job_data.get('duration', {}).get('label'),
                    working_hours_type=job_data.get('working_hours_type', {}).get('label'),
                    scope_of_work=job_data.get('scope_of_work', {}),
                    last_updated=datetime.utcnow()
                )
                db.add(new_job)
                new_count += 1
        
        db.commit()
        logger.info(f"Job update completed: {new_count} new jobs added, {updated_count} jobs updated")
        
    except Exception as e:
        logger.error(f"Error updating jobs: {str(e)}")
        db.rollback()
    finally:
        db.close()

def cleanup_old_jobs(days=7):
    """Remove jobs that haven't been updated in the specified number of days"""
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_jobs = db.query(Job).filter(Job.last_updated < cutoff_date).all()
        
        count = 0
        for job in old_jobs:
            db.delete(job)
            count += 1
        
        db.commit()
        logger.info(f"Cleanup completed: {count} old jobs removed")
        
    except Exception as e:
        logger.error(f"Error cleaning up old jobs: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 job_scheduler.py [update|cleanup]")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == "update":
        update_jobs()
    elif command == "cleanup":
        cleanup_old_jobs()
    else:
        print("Invalid command. Use 'update' or 'cleanup'") 