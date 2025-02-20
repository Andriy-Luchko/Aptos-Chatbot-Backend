from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
from query_data import query  # Ensure query is now async
import uuid

app = FastAPI()

# Dictionary to store active WebSocket connections
conversations: Dict[str, WebSocket] = {}

async def handle_websocket(conversation_id: str, websocket: WebSocket):
    conversations[conversation_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message: {data}")
            bot_response = await query(data)  # Await the async query
            await websocket.send_text(f"{bot_response}")  # Send bot response
    except WebSocketDisconnect:
        del conversations[conversation_id]
        print(f"Conversation {conversation_id} closed.")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("New WebSocket connection.")
    await websocket.accept()

    # Generate a unique conversation ID for the connection
    conversation_id = str(uuid.uuid4())
    print(f"Conversation ID generated: {conversation_id}")
    
    await handle_websocket(conversation_id, websocket)

@app.get("/active_conversations")
async def get_active_conversations():
    return {"active_conversations": list(conversations.keys())}

@app.get("/")  # ✅ Keep this here, but don't reassign `app`
async def root():
    return {"message": "FastAPI WebSocket Server Running"}
