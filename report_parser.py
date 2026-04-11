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
            raw_amount = amount_line.group(1).lower()
            # If it contains both 'paid' and 'pending' (or 'panding'), trigger human intervention
            if "paid" in raw_amount and ("pend" in raw_amount or "pand" in raw_amount):
                logger.warning(f"Complex split payment detected in Amount: '{raw_amount}'. Triggering human review.")
                return None

            first_num_match = re.search(r"[\d,\.]+", amount_line.group(1))
            if first_num_match:
                amount = float(first_num_match.group(0).replace(',', ''))
        
        # 4. STRICT Plan Detection
        # Capture everything between "Payment plan:" and the next field (Amount/Platform)
        plan_match = re.search(r"Payment plan:\s*([\s\S]*?)(?=Amount:|Payment Platform:|Platform:|$)", full_text, re.IGNORECASE)
        plan_raw = plan_match.group(1).lower().strip() if plan_match else ""
        
        # Numeric Mapping (Magic Numbers)
        PRICE_TO_PLAN = {
            "1960": "6 Payment Plan",
            "1125": "12 Payment Plan",
            "7225": "6 PIF",
            "9800": "12 PIF"
        }

        # Check for magic numbers first
        payment_plan = None
        for price, plan in PRICE_TO_PLAN.items():
            if price in plan_raw:
                payment_plan = plan
                break

        if not payment_plan:
            # Traditional Detection Logic
            months = None
            if "12" in plan_raw: months = "12"
            elif "6" in plan_raw: months = "6"
            elif "3" in plan_raw: months = "3"
            elif any(x in plan_raw for x in ["paid", "full", "pif", "custom", "plan", "pp"]):
                 months = "6" # Assume 6 only if they specified PIF, Custom or generic Plan
            
            if months:
                if "1month" in plan_raw.replace(" ", ""):
                    payment_plan = "1month"
                elif "custom" in plan_raw:
                    payment_plan = f"{months} custom plan"
                elif any(x in plan_raw for x in ["paid", "full", "pif"]):
                    payment_plan = f"{months} PIF"
                elif any(x in plan_raw for x in ["pp", "plan", "install"]):
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
        SalesReport(**data)
        return data

    except Exception as e:
        logger.error(f"Parser error: {e}")
        return None
