from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Query
from sheets_service import sheets_service
from config import PROGRAMS, WEBHOOK_SECRET, CLOSERS_GROUP_ID
from utils import logger, send_telegram_reply
from database import get_message_tracking

app = FastAPI()

@app.get("/")
async def home():
    return {"status": "online", "message": "Telegram Automation Webhook Server is running!"}

@app.post("/ghl-webhook")
async def ghl_webhook(request: Request, background_tasks: BackgroundTasks, token: str = Query(None)):
    """Processes incoming webhooks from GoHighLevel with token security."""
    
    if token != WEBHOOK_SECRET:
        logger.warning(f"Unauthorized webhook attempt with token: {token}")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    logger.info(f"Webhook received: {payload}")
    
    email = payload.get("email")
    tags = payload.get("tags", [])
    event_type = payload.get("type", "")

    if not email:
        return {"status": "ignored", "reason": "no_email"}

    # Find row in sheets
    row_index = sheets_service.find_row_by_email(email)
    if not row_index:
        logger.warning(f"Webhook received for {email} but no sheet row found.")
        return {"status": "ignored", "reason": "row_not_found"}

    # Process Onboarding Events
    onboarded = False
    
    # Check for Contract Signed
    if "signed" in tags or event_type == "contract_signed":
        sheets_service.update_onboarding_status(row_index, "R")
        onboarded = True

    # Check for Course Access Tags
    course_tags = PROGRAMS['default']['webhook_tags']['course_access']
    if any(tag in tags for tag in course_tags):
        sheets_service.update_onboarding_status(row_index, "S")
        onboarded = True

    # Send Notification to Closers Group (using local memory)
    if onboarded:
        msg_id = get_message_tracking(email)
        if msg_id:
            background_tasks.add_task(
                send_telegram_reply, 
                CLOSERS_GROUP_ID, 
                msg_id, 
                "this has been onboarded!"
            )
            logger.info(f"Queued onboarding reply for {email} using local memory.")

    return {"status": "success"}

@app.get("/health")
async def health():
    return {"status": "ok"}
