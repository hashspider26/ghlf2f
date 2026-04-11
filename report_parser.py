import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from config import VALID_PLATFORMS, PROGRAMS
from utils import logger

class SalesReport(BaseModel):
    name: str
    email: EmailStr
    payment_plan: str
    amount: float
    platform: str
    notes: Optional[str] = "N/A"
    date: str

    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v):
        if v not in VALID_PLATFORMS:
            raise ValueError(f"Unknown platform: {v}")
        return v

def clean_value(val: str) -> str:
    """Removes brackets, extra whitespace, and common garbage symbols."""
    if not val: return ""
    cleaned = re.sub(r'[\[\]\(\)]', '', val)
    return cleaned.strip()

def parse_sales_report(text: str) -> Optional[dict]:
    """The 'Advanced Mapping' Parser: Detects 3, 6, 12 months and PIF vs Plan."""
    try:
        full_text = text.replace('\xa0', ' ') 
        
        # 1. Extract Name
        name_match = re.search(r"Name:\s*(.*)", full_text, re.IGNORECASE)
        name = clean_value(name_match.group(1).split('\n')[0]) if name_match else None
        
        # 2. Extract Email
        email_match = re.search(r"([\w\.-]+@[\w\.-]+\.\w+)", full_text)
        email = email_match.group(1).lower() if email_match else None
        
        # 3. Extract Amount (First Number)
        amount_line = re.search(r"Amount:\s*(.*)", full_text, re.IGNORECASE)
        amount = 0.0
        if amount_line:
            first_num_match = re.search(r"[\d,\.]+", amount_line.group(1))
            if first_num_match:
                amount = float(first_num_match.group(0).replace(',', ''))
        
        # 4. STRICT Plan Detection
        plan_line = re.search(r"Payment plan:\s*(.*)", full_text, re.IGNORECASE)
        plan_raw = plan_line.group(1).lower().strip() if plan_line else ""
        
        # Check for duration
        months = None
        if "12" in plan_raw: months = "12"
        elif "6" in plan_raw: months = "6"
        elif "3" in plan_raw: months = "3"
        elif any(x in plan_raw for x in ["paid", "full", "pif", "custom"]):
             months = "6" # Assume 6 only if they specified PIF or Custom
        
        # Determine specific mapping
        payment_plan = None
        if months:
            if "1month" in plan_raw.replace(" ", ""):
                payment_plan = "1month"
            elif "custom" in plan_raw:
                payment_plan = f"{months} custom plan"
            elif any(x in plan_raw for x in ["paid", "full", "pif"]):
                payment_plan = f"{months} PIF"
            elif any(x in plan_raw for x in ["pp", "plan", "install"]):
                # Apply exact match for 6Payment Plan (no space) or others
                if months == "6":
                    payment_plan = "6Payment Plan"
                else:
                    payment_plan = f"{months} Payment Plan"

        # If we couldn't determine a SPECIFIC plan, trigger human intervention
        if not payment_plan:
            logger.warning(f"Ambiguous payment plan detected: '{plan_raw}'. Triggering vault alert.")
            return None

        # 5. Extract Platform
        platform_found = "Stripe" 
        for p in VALID_PLATFORMS:
            if p.lower() in full_text.lower():
                platform_found = p
                break
        
        # 6. Notes
        notes = "N/A"
        if "Platform:" in full_text:
            notes = full_text.split("Platform:")[1].split('\n', 1)[-1].strip()
        elif amount_line:
            notes = full_text.split(amount_line.group(0))[1].strip()

        if not all([name, email, amount > 0]):
            return None

        now = datetime.now()
        date_str = f"{now.month}/{now.day}/{now.year}"
        
        data = {
            "name": name,
            "email": email,
            "payment_plan": payment_plan,
            "amount": amount,
            "platform": platform_found,
            "notes": notes[:500] if notes else "N/A",
            "date": date_str
        }

        # Final match check against known sheet strings
        # Note: 6Payment Plan is exactly what's in the screenshot (no space)
        SalesReport(**data)
        return data

    except Exception as e:
        logger.error(f"Parser error: {e}")
        return None
