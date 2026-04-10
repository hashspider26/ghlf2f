import requests
import asyncio
from config import GHL_API_KEY, GHL_LOCATION_ID, GHL_BASE_URL
from utils import logger, send_va_alert

class GHLService:
    def __init__(self):
        # PIT tokens (pit-*) are v2 API tokens ONLY.
        # v1 endpoint (rest.gohighlevel.com) rejects them with 401.
        self.headers = {
            "Authorization": f"Bearer {GHL_API_KEY}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"   # Required by GHL v2 API
        }
        # v2 API base — compatible with Private Integration Tokens (pit-*)
        self.v2_base = GHL_BASE_URL
        self.location_id = GHL_LOCATION_ID

    def get_contact_by_email(self, email: str):
        """Fetches a contact from GHL by email using v2 API."""
        email_clean = email.strip().lower()

        # v2 contacts search using 'query'
        url = f"{self.v2_base}/contacts/"
        params = {"locationId": self.location_id, "query": email_clean}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            logger.info(f"GHL lookup status: {response.status_code}")
            response.raise_for_status()
            
            contacts = response.json().get("contacts", [])
            # Double check that the email matches exactly (security)
            for contact in contacts:
                if contact.get("email", "").strip().lower() == email_clean:
                    return contact
                    
            return None
        except Exception as e:
            logger.error(f"GHL Error (get_contact): {e}")
            return None

    def apply_tag(self, contact_id: str, tag: str):
        """Applies a tag to a contact in GHL using v2 API."""
        url = f"{self.v2_base}/contacts/{contact_id}/tags"
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
