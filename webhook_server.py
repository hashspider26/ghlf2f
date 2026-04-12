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
    replies = [] # List of (clean_msg, va_msg)
    
    # 1. Check for Contract Signed
    contract_tag = PROGRAMS['default']['webhook_tags'].get('contract_signed', 'signed')
    if contract_tag in tags or event_type == "contract_signed":
        success = sheets_service.update_onboarding_status(row_index, "R")
        if success:
            replies.append((
                "Contract Signed! ✍️", 
                f"✍️ **Contract Signed!**\nClient: {email}"
            ))

    # 2. Check for Course Access Tags
    course_tags = PROGRAMS['default']['webhook_tags']['course_access']
    if any(tag in tags for tag in course_tags):
        success = sheets_service.update_onboarding_status(row_index, "S")
        if success:
            replies.append((
                "The course has been sent to the mentee.", 
                f"🎓 **The course has been sent to the mentee.**\nClient: {email}"
            ))

    # 3. Send Individual Replies/Notifications for each event
    if replies:
        msg_id = sheets_service.get_message_tracking(email)
        from utils import send_public_notification
        for clean_text, va_text in replies:
            background_tasks.add_task(
                send_public_notification, 
                clean_text, 
                va_text=va_text,
                reply_to_message_id=msg_id
            )
            logger.info(f"Queued dual-group notification for {email}")
        
        if not msg_id:
            logger.warning(f"Onboarding detected for {email} but no msg_id found for original report. Sent to default groups.")

    return {"status": "success"}

@app.get("/health")
async def health():
    return {"status": "ok"}
