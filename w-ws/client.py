# Client example
import asyncio
import websockets

async def hello():
    uri = "ws://localhost:8000/w-ws/server.py"
    async with websockets.connect(uri) as ws:
        await ws.send("Hello, Server!")
        response = await ws.recv()
        print(response)

asyncio.get_event_loop().run_until_complete(hello())