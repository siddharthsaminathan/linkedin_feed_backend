from database import SessionLocal, Job
from datetime import datetime
import json
import sys

def add_jobs_from_json(json_data):
    db = SessionLocal()
    try:
        # Parse JSON data
        jobs_data = json.loads(json_data)
        
        # If the data is a single job, convert it to a list
        if isinstance(jobs_data, dict):
            jobs_data = [jobs_data]
        
        added_count = 0
        for job_data in jobs_data:
            # Convert string dates to datetime objects if they exist
            if 'application_deadline' in job_data and job_data['application_deadline']:
                job_data['application_deadline'] = datetime.fromisoformat(job_data['application_deadline'].replace('Z', '+00:00'))
            
            # Create Job instance
            job = Job(**job_data)
            db.add(job)
            added_count += 1
        
        db.commit()
        print(f"Successfully added {added_count} jobs to the database!")
        
    except Exception as e:
        db.rollback()
        print(f"Error adding jobs: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 add_jobs_from_json.py 'JSON_DATA'")
        sys.exit(1)
    
    json_data = sys.argv[1]
    add_jobs_from_json(json_data) 