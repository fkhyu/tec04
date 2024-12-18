import asyncio
import websockets
import json

clients = {}
game_state = {}

ip = "172.20.10.2"
# ip = "localhost"

port = 8080


async def broadcast():
    while True:
        # print(clients)
        for client in list(clients.values()):
            try:
                await client.send(json.dumps(game_state))
            except websockets.ConnectionClosed:
                # TODO: Handle client disconnection later
                print("Client disconnected.")
                pass
        await asyncio.sleep(0.05)

async def handler(websocket, path):
    # Assign a unique ID for the client
    client_id = str(id(websocket))
    clients[client_id] = websocket
    print(f"New client connected: {client_id}")

    try:
        # Send game configuration to the new client
        await websocket.send(json.dumps(client_id))

        async for message in websocket:
            try:
                # Parse and update the game state
                data = json.loads(message)
                game_state[client_id] = data
            except json.JSONDecodeError:
                print(f"Invalid message from {client_id}: {message}")

    except websockets.ConnectionClosed:
        print(f"Client disconnected: {client_id}")
    finally:
        # Clean up on disconnection
        clients.pop(client_id, None)
        game_state.pop(client_id, None)

# Run the WebSocket server and broadcast in the same event loop
async def main():
    server = await websockets.serve(handler, ip, port)
    print("Server started at ws://localhost:8080")
    await asyncio.gather(server.wait_closed(), broadcast())

# Start the main event loop
asyncio.run(main())
