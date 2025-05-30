import threading
import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/telemetria")
async def receber_telemetria(req: Request):
    data = await req.json()
    if data.get("evento") == "fim_corrida":
        # Salva o ficheiro localmente
        now = data.get("timestamp")
        filename = f"corrida_{now}.json"
        path = Path("corridas") / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data["resultado"], f, indent=2)

        # Envia o ficheiro para o canal
        canal = bot.get_channel(1364658111687692360)
        if canal:
            await canal.send(
                f"🏁 Corrida terminada! Resultados salvos em `{filename}`",
                file=discord.File(str(path))
            )

def start_api():
    def _run():
        print("🚀 A arrancar servidor FastAPI...")
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
