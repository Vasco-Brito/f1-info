import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))
TELEMETRY_PORT = int(os.getenv("TELEMETRY_PORT", "20777"))
