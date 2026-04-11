from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Query
from sheets_service import sheets_service
from config import PROGRAMS, WEBHOOK_SECRET, CLOSERS_GROUP_ID
from utils import logger, send_telegram_reply

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
    replies = []
    
    # 1. Check for Contract Signed
    contract_tag = PROGRAMS['default']['webhook_tags'].get('contract_signed', 'signed')
    if contract_tag in tags or event_type == "contract_signed":
        success = sheets_service.update_onboarding_status(row_index, "R")
        if success:
            replies.append("Contract Signed! ✍️")

    # 2. Check for Course Access Tags
    course_tags = PROGRAMS['default']['webhook_tags']['course_access']
    if any(tag in tags for tag in course_tags):
        success = sheets_service.update_onboarding_status(row_index, "S")
        if success:
            replies.append("Course Access Granted! 🎓")

    # 3. Send Individual Replies for each event
    if replies:
        msg_id = sheets_service.get_message_tracking(email)
        if msg_id:
            for reply_text in replies:
                background_tasks.add_task(
                    send_telegram_reply, 
                    CLOSERS_GROUP_ID, 
                    msg_id, 
                    reply_text
                )
                logger.info(f"Queued onboarding reply: '{reply_text}' for {email}")
        else:
            logger.warning(f"Onboarding detected for {email} but no msg_id found for reply.")

    return {"status": "success"}

@app.get("/health")
async def health():
    return {"status": "ok"}
