
import datetime
import requests
from redis import Redis
from rq import Queue
import os
import sys
sys.path.append('./pyBreezeChMS')
from breeze import breeze
import os
api_key = os.environ['API_KEY']
import logging
import time
# Create a BreezeApi object and pass in the url and api key

breeze_api = breeze.BreezeApi(
    breeze_url='https://iskconofnc.breezechms.com',
    api_key=api_key)

# Redis configuration
REDIS_HOST = "192.168.0.71"
REDIS_PORT = 6379

# Example schedule for demo purposes:
# This maps days of the week and time ranges (HH:MM) to a mock event ID
EVENT_SCHEDULE = {
    "Monday": {
        ("03:00", "7:30:00"): "event_id_1",
    },
    "Tuesday": {
        ("03:00", "7:30:00"): "event_id_1",
    },
    "Wednesday": {
        ("03:00", "7:30:00"): "event_id_1",
    },
    "Thursday": {
        ("03:00", "7:30:00"): "event_id_1",
    },
    "Friday": {
        ("03:00", "7:30:00"): "event_id_1",
    },
    "Saturday": {
        ("03:00", "7:30:00"): "event_id_1",
    },
    "Sunday": {
        ("03:00", "7:30:00"): "event_id_1",
        ("16:00", "19:30:00"): "event_id_2",
    },
    # Add other days/times as needed
}

def get_event_id(current_time, current_day):
    """
    Returns an event_id from the EVENT_SCHEDULE based on the current
    day of week and time. Returns None if no match is found.
    """
    # Convert day name to match schedule dictionary keys
    day_name = current_day.strftime("%A")  # e.g., "Monday"
    time_str = current_time.strftime("%H:%M")  # e.g., "09:30"
    
    events_for_day = EVENT_SCHEDULE.get(day_name, {})
    for (start, end), event_id in events_for_day.items():
        if start <= time_str < end:
            return event_id
    return None

def submit_attendance(face_id, event_id):
    """
    Example function sending attendance data to a BreezeChms-like endpoint.
    """
    if not event_id:
        logging.info(f"No event_id determined for FaceID={face_id}; skipping attendance.")
        return
    
    events = breeze_api.get_events()
    event = next((event for event in events if event['id'] == event_id), None)
    if not event:
        logging.info(f"Event not found for FaceID={face_id}, event_id={event_id}; skipping attendance.")
        return
    
    # Get the event details
    event_name = event['name']
    event_date = event['date']
    event_time = event['time']
    
    # Create the attendance record  \

    people = breeze_api.get_people()
    person = next((person for person in people if person['id'] == face_id), None)
    if not person:
        logging.info(f"Person not found for FaceID={face_id}; skipping attendance.")
        return

    time.sleep(3.5)
    # Create the attendance record
    attendance = breeze_api.event_check_in(person_id=person['id'], event_instance_id=event_id)
    logging.info(f"Successfully submitted attendance for FaceID={face_id}, event_id={event_id}")


def process_attendance(face_id, payload):
    """
    Main worker function. Called by RQ (from main.py's queue.enqueue).
    1. Determine the current time/day.
    2. Find the appropriate event_id from EVENT_SCHEDULE.
    3. Submit an attendance record to the BreezeChms API.ß
    """
    now = datetime.datetime.now()  # local time; adjust timezone if needed
    event_id = get_event_id(now, now)
    submit_attendance(face_id, event_id)

# If you want to run a worker programmatically from this module,
# you can initialize a worker here.
if __name__ == "__main__":
    # Example: Start an RQ worker for this queue
    redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT)
    q = Queue(connection=redis_conn)
    logging.info("Worker started. Waiting for jobs...")
    # Note: Typically you'd run "rq worker" from the command line instead.
    # Or you can implement a custom RQ worker loop here. 