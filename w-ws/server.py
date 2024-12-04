import asyncio
import websockets
import json

clients = set()

# Game configuration to be sent to each client
game_config = {
    "speed": 100,
    "radius": 20,
    "a": 1.00001,
    "max_fps": 60,
    "boost_count": 70,
    "world_size": 800
}

async def handler(websocket, path):
    # Register client
    clients.add(websocket)
    print(f"New client connected: {websocket}")
    try:
        # Send game config to the new client
        await websocket.send(json.dumps(game_config))

        # Notify other clients about new connection
        for client in clients:
            if client != websocket:
                await client.send("A new player has joined the game!")

        # Handle incoming messages and broadcast to other clients
        async for message in websocket:
            try:
                # Try to parse message as json
                data = json.loads(message)  
                print(f"Received structured message from client: {data}")

                # Broadcast the message to other clients
                for client in clients:
                    if client != websocket:
                        await client.send(json.dumps({"from": data["client_id"], "message": data["message"]}))
                    else:
                        await client.send(json.dumps({"from": "You", "message": data["message"]}))
            except json.JSONDecodeError:
                # Handle plain text
                print(f"Received plain text message from client: {message}")

                # Broadcast the plain text to other clients
                for client in clients:
                    if client != websocket:
                        await client.send(f"Message from another player: {message}")


    finally:
        # Unregister client
        clients.remove(websocket)
        for client in clients:
            await client.send("A player has left the game!")

start_server = websockets.serve(handler, "localhost", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()