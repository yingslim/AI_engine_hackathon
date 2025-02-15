# example requires websocket-client library:
# pip install websocket-client

import os
import json
import websocket

OPENAI_API_KEY = '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' #os.environ.get("OPENAI_API_KEY")

url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
headers = [
    "Authorization: Bearer " + OPENAI_API_KEY,
    "OpenAI-Beta: realtime=v1"
]

def on_open(ws):
    print("Connected to server.")

def on_message(ws, message):
    data = json.loads(message)
    print("Received event:", json.dumps(data, indent=2))

ws = websocket.WebSocketApp(
    url,
    header=headers,
    on_open=on_open,
    on_message=on_message,
)

ws.run_forever()