#!/bin/bash

# Get the absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create the cron jobs
# Run job updates daily at 8:00 AM
(crontab -l 2>/dev/null; echo "0 8 * * * cd $SCRIPT_DIR && python3 job_scheduler.py update") | crontab -

# Run cleanup daily at 9:00 AM
(crontab -l 2>/dev/null; echo "0 9 * * * cd $SCRIPT_DIR && python3 job_scheduler.py cleanup") | crontab -

echo "Scheduler has been set up successfully!"
echo "Jobs will be updated daily at 8:00 AM"
echo "Old jobs will be cleaned up daily at 9:00 AM" 