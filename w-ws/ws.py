import websockets

server_url = 'ws://localhost:8000/w-ws/server.py'  # Only for testing

class Connection:
    def __init__(self, server_url):
        self.server_url = server_url
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self.server_url)

    async def send(self, message):
        if self.ws is None or self.ws.closed:
            raise ConnectionError("WebSocket is not connected.")
        await self.ws.send(message)
        response = await self.ws.recv()
        return response

    async def close(self):
        if self.ws and not self.ws.closed:
            await self.ws.close()
        
    async def get(self):
        data = await self.ws.recv()
        return data
