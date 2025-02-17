from fastapi import FastAPI, Request
from redis import Redis
from rq import Queue
import logging


# Redis configuration
REDIS_HOST = "192.168.0.71"
REDIS_PORT = 6379

# Create FastAPI instance
app = FastAPI()

# Connect to Redis running at "redis:6379" (the hostname might differ depending on your setup)
redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT)
queue = Queue(connection=redis_conn)

@app.post("/webhook")
async def webhook_listener(request: Request):
    """
    Webhook endpoint to receive a FaceID and any other payload data.
    The FaceID is fetched from the request headers as an example.
    The payload can also be parsed from the request body if needed.
    """
    payload = await request.json()  # Parse JSON body
    face_id = payload.get("face_id", "unknown")


    logging.info(f"Webhook: {payload}")
    # Enqueue a job for background processing.
    # Replace "process_attendance" with the actual function name that should handle your job.
    queue.enqueue("worker.process_attendance", face_id, payload)
    logging.info(f"Webhook received and enqueued for FaceID={face_id}")


    return {"status": "ok", "message": "Webhook received and enqueued."} 