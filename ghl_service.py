import requests
import asyncio
from config import GHL_API_KEY, GHL_LOCATION_ID, GHL_BASE_URL
from utils import logger, send_va_alert

class GHLService:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {GHL_API_KEY}",
            "Version": "2021-07-28",
            "Content-Type": "application/json"
        }

    def get_contact_by_email(self, email: str):
        """Fetches a contact from GHL by email."""
        url = f"{GHL_BASE_URL}/contacts/"
        params = {"locationId": GHL_LOCATION_ID, "query": email}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            contacts = response.json().get("contacts", [])
            return contacts[0] if contacts else None
        except Exception as e:
            logger.error(f"GHL Error (get_contact): {e}")
            return None

    def apply_tag(self, contact_id: str, tag: str):
        """Applies a tag to a contact in GHL."""
        url = f"{GHL_BASE_URL}/contacts/{contact_id}/tags"
        payload = {"tags": [tag]}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"Successfully applied tag {tag} to GHL contact {contact_id}")
            return True
        except Exception as e:
            logger.error(f"GHL Error (apply_tag): {e}")
            # Send VA Alert for GHL failure
            asyncio.create_task(send_va_alert(
                f"Failed to apply GHL tag `{tag}` for contact `{contact_id}`. Error: {e}"
            ))
            return False

ghl_service = GHLService()
