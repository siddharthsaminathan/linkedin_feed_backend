from database import SessionLocal, Job

def remove_test_jobs():
    db = SessionLocal()
    try:
        # Remove jobs with TEST in their job_id
        test_jobs = db.query(Job).filter(Job.job_id.like('TEST%')).all()
        count = 0
        for job in test_jobs:
            db.delete(job)
            count += 1
        
        db.commit()
        print(f"Successfully removed {count} test jobs from the database.")
        
    except Exception as e:
        print(f"Error removing test jobs: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    remove_test_jobs() 