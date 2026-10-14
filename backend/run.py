import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"[*] Starting SENTINEL-X ShadowGuard Gateway on {host}:{port}...")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
