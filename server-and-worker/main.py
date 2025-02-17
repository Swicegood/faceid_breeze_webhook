from fastapi import FastAPI, Request
from redis import Redis
from rq import Queue

# Create FastAPI instance
app = FastAPI()

# Connect to Redis running at "redis:6379" (the hostname might differ depending on your setup)
redis_conn = Redis(host="redis", port=6379)
queue = Queue(connection=redis_conn)

@app.post("/webhook")
async def webhook_listener(request: Request):
    """
    Webhook endpoint to receive a FaceID and any other payload data.
    The FaceID is fetched from the request headers as an example.
    The payload can also be parsed from the request body if needed.
    """
    face_id = request.headers.get("FaceID", "unknown")  # Fallback if header is missing
    payload = await request.json()  # Parse JSON body
    
    # Enqueue a job for background processing.
    # Replace "process_attendance" with the actual function name that should handle your job.
    queue.enqueue("worker.process_attendance", face_id, payload)
    
    return {"status": "ok", "message": "Webhook received and enqueued."} 