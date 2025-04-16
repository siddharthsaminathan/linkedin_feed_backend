from database import SessionLocal, Job, init_db
from datetime import datetime

def test_database():
    print("Initializing database...")
    init_db()
    
    print("Creating test job...")
    db = SessionLocal()
    try:
        test_job = Job(
            job_id="TEST001",
            headline="Test Job",
            description="This is a test job",
            webpage_url="https://example.com",
            number_of_vacancies=1,
            employer={"name": "Test Company"},
            workplace_address={"city": "Test City"},
            must_have={"skills": []},
            nice_to_have={"skills": []},
            employment_type="Full-time",
            salary_type="Monthly",
            scope_of_work={"min": 100, "max": 100},
            working_hours_type="Full-time"
        )
        
        db.add(test_job)
        db.commit()
        print("Test job added successfully!")
        
        print("Querying test job...")
        job = db.query(Job).filter(Job.job_id == "TEST001").first()
        if job:
            print(f"Found job: {job.headline}")
        else:
            print("Job not found")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_database() 