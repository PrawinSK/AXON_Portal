import asyncio
import httpx
from app.main import app

async def test_api_routes():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        print("Testing GET /")
        r_root = await client.get("/")
        assert r_root.status_code == 200
        print("Root response:", r_root.json())

        print("\nTesting GET /config")
        r_cfg = await client.get("/config")
        assert r_cfg.status_code == 200
        data_cfg = r_cfg.json()
        print("Config response:", data_cfg)
        assert data_cfg["total_api_keys"] == 50
        assert data_cfg["gemini_model"] == "gemini-3.6-flash"

        print("\nTesting GET /interview/pool/status")
        r_pool = await client.get("/interview/pool/status")
        assert r_pool.status_code == 200
        pool_data = r_pool.json()
        print("Pool status:", pool_data)
        assert pool_data["total_keys"] == 50

        print("\nALL FASTAPI API ROUTES VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_api_routes())
