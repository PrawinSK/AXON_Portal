import requests
from app.core.config import settings

response = requests.get(
    f"{settings.grok_api_base}/models",
    headers={
        "Authorization": f"Bearer {settings.grok_api_key}"
    }
)

print("Status Code:", response.status_code)
print(response.text)