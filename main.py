from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List, Tuple
from query_data import query
from typing import Dict
from query_data import query
import uuid


app = FastAPI()

# Dictionary to store active WebSocket connections
conversations: Dict[str, Tuple[WebSocket, List[str]]] = {}

async def handle_websocket(conversation_id: str, websocket: WebSocket):
    conversations[conversation_id] = (websocket, [])  # Ensure history is stored 

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message: {data}")
            bot_response = query(data)
            await websocket.send_text(f"{bot_response}")  # Echo message
    except WebSocketDisconnect:
        del conversations[conversation_id]
        print(f"Conversation {conversation_id} closed.")
    finally:
        websocket.close()


@app.get("/conversation_history/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """Retrieve the stored conversation history for a given conversation ID."""
    if conversation_id in conversations:
        _, history = conversations[conversation_id]
        return {"conversation_id": conversation_id, "history": history}
    return {"error": "Conversation not found"}

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
