from app.services.key_pool import key_pool

key, client = key_pool.get_next_key_and_client()
print('Testing gemini-3.5-flash with key:', key[:12])

resp = client.models.generate_content(
    model='gemini-3.5-flash',
    contents='Respond with valid JSON: {"status": "ok", "model": "gemini-3.5-flash"}'
)
print('Response:', resp.text.strip())
