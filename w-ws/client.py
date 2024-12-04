# Client example
import asyncio
import uuid
import json
from ws import Connection


client_id = str(uuid.uuid4())
conn = Connection('ws://localhost:8000/w-ws/server.py')
message = [{'x': 11, 'y': 20}, {'x': 30, 'y': 40}]

async def main():
    await conn.connect()
    data_to_send = message
    response = await conn.send(json.dumps(data_to_send))
    if response:
        print(response)
    await conn.close()

asyncio.run(main())