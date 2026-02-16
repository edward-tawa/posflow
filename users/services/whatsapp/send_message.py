import requests
from django.conf import settings

ACCESS_TOKEN = settings.WHATSAPP_ACCESS_TOKEN
PHONE_NUMBER_ID = settings.WHATSAPP_PHONE_NUMBER_ID
API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

def send_whatsapp_template(to_number, template_name, parameters):
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en_US"},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in parameters]
                }
            ]
        }
    }


    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, json=payload, headers=headers)
    return response.json()
