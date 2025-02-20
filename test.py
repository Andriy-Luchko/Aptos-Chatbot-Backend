import websockets
import asyncio

FASTAPI_SERVER = "ws://localhost:8000/ws"

async def test_websocket():
    async with websockets.connect(FASTAPI_SERVER) as ws:
        message = "how to install aptos cli"
        await ws.send(message)
        response = await ws.recv()
        print(f"received: {response}")

for i in range(1):
    asyncio.run(test_websocket())