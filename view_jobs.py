from database import SessionLocal, Job
from sqlalchemy import desc
import json

def view_jobs(limit=10):
    db = SessionLocal()
    try:
        # Get the most recent jobs
        jobs = db.query(Job).order_by(desc(Job.created_at)).limit(limit).all()
        
        print(f"\nFound {len(jobs)} jobs in the database:")
        print("-" * 80)
        
        for job in jobs:
            print(f"\nJob ID: {job.job_id}")
            print(f"Headline: {job.headline}")
            print(f"Employer: {job.employer.get('name', 'N/A')}")
            print(f"Location: {job.workplace_address.get('municipality', 'N/A')}")
            print(f"Employment Type: {job.employment_type}")
            print(f"Application Deadline: {job.application_deadline}")
            print(f"Created At: {job.created_at}")
            print("-" * 80)
            
    finally:
        db.close()

if __name__ == "__main__":
    view_jobs(limit=10)  # View the 10 most recent jobs 