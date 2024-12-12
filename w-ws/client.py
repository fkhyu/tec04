import asyncio
import json
from termcolor import colored
from ws import Connection

ip = '172.20.10.2'
# ip = 'localhost'
port = 8080

# Define the WebSocket server URL
server_url = f'ws://{ip}:{port}/w-ws/server.py'

# Establish WebSocket connection
conn = Connection(server_url)

# Example message to send to the server
snake = [{'x': 11, 'y': 20}, {'x': 30, 'y': 40}]

waiting = bool

# Function to connect to the WebSocket server
async def connect():
    try:
        await conn.connect()
        print("WebSocket connection established.")
        response = await conn.get()
        data = json.loads(response)
        print(f"User ID: {data}")
    except Exception as e:
        print(f"Failed to connect to server: {e}")


async def send_recv():
    global waiting

    try:
        while True:
            await conn.send(json.dumps(snake))
            message = await conn.get()
            if message:
                data = json.loads(message)
                print(f"Received data: {data}")
                if len(data) > 1:
                    waiting = False
                    print(colored("Game started!", "green"))
                    break
                else:
                    print("Waiting for more players to connect.")
                    waiting = True
    except Exception as e:
        print(f"Error in send_recv: {e}")

# Main function to manage connection, sending, and receiving
async def main():
    # Establish the connection
    await connect()

    if waiting:
        print("Waiting for more clients to connect.")
    else:
        task = asyncio.create_task(send_recv())
        # Wait for the receive task (optional; adjust logic for periodic sends)
        await task

# Run the main event loop
asyncio.run(main())
