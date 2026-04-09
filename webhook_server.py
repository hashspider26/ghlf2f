from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from sheets_service import sheets_service
from config import PROGRAMS, WEBHOOK_SECRET
from utils import logger

app = FastAPI()

@app.post("/ghl-webhook")
async def ghl_webhook(request: Request, background_tasks: BackgroundTasks, token: str = Query(None)):
    """Processes incoming webhooks from GoHighLevel with token security."""
    
    # Simple Token Validation
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

    # Check for Contract Signed
    if "signed" in tags or event_type == "contract_signed":
        background_tasks.add_task(sheets_service.update_onboarding_status, row_index, "R")

    # Check for Course Access Tags
    course_tags = PROGRAMS['default']['webhook_tags']['course_access']
    if any(tag in tags for tag in course_tags):
        background_tasks.add_task(sheets_service.update_onboarding_status, row_index, "S")

    return {"status": "success"}

@app.get("/health")
async def health():
    return {"status": "ok"}
