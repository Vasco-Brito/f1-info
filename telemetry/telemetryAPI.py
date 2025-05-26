import threading
import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/telemetria")
async def receber_telemetria(req: Request):
    data = await req.json()
    print("📡 Dados recebidos:", data)
    return {"status": "ok"}

def start_api():
    def _run():
        print("🚀 A arrancar servidor FastAPI...")
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
