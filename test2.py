import websockets
import asyncio

FASTAPI_SERVER = "ws://localhost:8000/ws"

async def test_websocket():
    async with websockets.connect(FASTAPI_SERVER) as ws:
        messages = [
            "I am using macos",
            "I do not like windows",
            "What is the system i am using"
        ]
        
        for message in messages:
            await ws.send(message)
            response = await ws.recv()
            print(f"Sent: {message}")
            print(f"Received: {response}")


for i in range(1):
    asyncio.run(test_websocket())