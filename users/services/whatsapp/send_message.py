# utils/whatsapp.py
import requests
from django.conf import settings
from loguru import logger

ACCESS_TOKEN = settings.WHATSAPP_ACCESS_TOKEN
PHONE_NUMBER_ID = settings.WHATSAPP_PHONE_NUMBER_ID
API_VERSION = settings.WHATSAPP_API_VERSION
API_URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"


def mask_number(number):
    """Mask phone number for logs (show last 4 digits only)."""
    if not number:
        return "N/A"
    return f"{'*' * (len(number) - 4)}{number[-4:]}"


def send_whatsapp_message_to_user(user, template_name, parameters):
    """
    Send a WhatsApp template message to a system user.
    """

    if not user.whatsapp_opt_in or not user.whatsapp_number:
        logger.warning(
            f"WhatsApp skipped | user={user.username} | reason=not_opted_in_or_missing_number"
        )
        return {"error": "User not opted in or missing WhatsApp number"}

    masked_number = mask_number(user.whatsapp_number)

    payload = {
        "messaging_product": "whatsapp",
        "to": user.whatsapp_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en_US"},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in parameters]
                }
            ],
        },
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        logger.info(
            f"WhatsApp attempt | user={user.username} | "
            f"phone={masked_number} | template={template_name} | "
            f"param_count={len(parameters)}"
        )

        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        response_data = response.json()

        if not response.ok:
            logger.error(
                f"WhatsApp failed | user={user.username} | "
                f"phone={masked_number} | template={template_name} | "
                f"status={response.status_code} | error={response_data}"
            )
        else:
            logger.success(
                f"WhatsApp sent | user={user.username} | "
                f"phone={masked_number} | template={template_name}"
            )

        return response_data

    except requests.RequestException as e:
        logger.exception(
            f"WhatsApp exception | user={user.username} | "
            f"phone={masked_number} | template={template_name} | error={str(e)}"
        )
        return {"error": str(e)}
