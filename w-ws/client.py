import asyncio
import json
from termcolor import colored
from ws import Connection

# Define the WebSocket server URL
server_url = 'ws://localhost:8080/w-ws/server.py'

# Establish WebSocket connection
conn = Connection(server_url)

# Example message to send to the server
snake = [{'x': 11, 'y': 20}, {'x': 30, 'y': 40}]

# Function to connect to the WebSocket server
async def connect():
    try:
        await conn.connect()
        print("WebSocket connection established.")
        client_id = await conn.get()
        print(f"User ID: {client_id}")
    except Exception as e:
        print(f"Failed to connect to server: {e}")

async def send_recv():
    try:
        while True:
            await conn.send(json.dumps(snake))
            # print("Sent data.")
            message = await conn.get()
            if message:
                data = json.loads(message)
                print(f"Received data: {data}")
    except Exception as e:
        print(f"Error in send_recv: {e}")

# Main function to manage connection, sending, and receiving
async def main():
    # Establish the connection
    await connect()

    # Start receiving and sending
    task = asyncio.create_task(send_recv())

    # Wait for the receive task (optional; adjust logic for periodic sends)
    await task

# Run the main event loop
asyncio.run(main())
