import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from config import VALID_PLATFORMS

class SalesReport(BaseModel):
    name: str
    email: EmailStr
    payment_plan: str  # 6PIF or 6PP
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

def parse_sales_report(text: str) -> Optional[dict]:
    """Parses raw telegram text into a structured dictionary."""
    try:
        # Extract fields using regex
        name_match = re.search(r"Name:\s*\[?([^\]\n]+)\]?", text, re.IGNORECASE)
        email_match = re.search(r"Email:\s*\[?([\w\.-]+@[\w\.-]+)\]?", text, re.IGNORECASE)
        plan_match = re.search(r"Payment plan:\s*(.*)", text, re.IGNORECASE)
        amount_match = re.search(r"Amount:\s*\$?([\d,\.]+)", text, re.IGNORECASE)
        platform_match = re.search(r"(?:Payment )?Platform:\s*(.*)", text, re.IGNORECASE)
        notes_match = re.search(r"Notes:\s*(.*)", text, re.IGNORECASE | re.DOTALL)

        if not all([name_match, email_match, plan_match, amount_match, platform_match]):
            return None

        # Determine Payment Plan Code (Matching your dropdowns)
        plan_raw = plan_match.group(1).lower()
        if "paid in full" in plan_raw:
            payment_plan = "6 PIF"
        elif any(x in plan_raw for x in ["payment plan", "installments"]):
            payment_plan = "6 Payment Plan"
        else:
            payment_plan = "UNKNOWN"

        # Sanitize Amount (Handle $7,225.00 format)
        amount_str = amount_match.group(1).replace(",", "")
        amount = float(amount_str)

        # Sanitize Platform (Handle lowercase input like 'stripe')
        platform_raw = platform_match.group(1).strip().capitalize()
        # Edge case for Wire Transfer (needs two words capitalized)
        if platform_raw.lower() == "wire transfer":
            platform_raw = "Wire Transfer"

        # Structure data
        now = datetime.now()
        date_str = f"{now.month}/{now.day}/{now.year}"
        
        data = {
            "name": name_match.group(1).strip().strip("[]"),
            "email": email_match.group(1).strip().strip("[]"),
            "payment_plan": payment_plan,
            "amount": amount,
            "platform": platform_raw,
            "notes": notes_match.group(1).strip() if notes_match else "N/A",
            "date": date_str
        }

        # Basic Pydantic Validation
        report = SalesReport(**data)
        return data

    except Exception:
        return None
