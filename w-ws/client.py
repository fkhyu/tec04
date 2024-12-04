import asyncio
import uuid
import json
from ws import Connection

# Generate a unique client ID
client_id = str(uuid.uuid4())

# Define the WebSocket server URL
server_url = 'ws://localhost:8000/w-ws/server.py'

# Establish WebSocket connection
conn = Connection(server_url)

# Example message to send to the server
message = {'message': [{'x': 11, 'y': 20}, {'x': 30, 'y': 40}]}

# Function to connect to the WebSocket server
async def connect():
    try:
        await conn.connect()
        print("WebSocket connection established.")
    except Exception as e:
        print(f"Failed to connect to server: {e}")

# Function to send data to the server
async def send_data():
    try:
        response = await conn.send(json.dumps(message))
        if response:
            print(f"Response from server: {response}")
    except Exception as e:
        print(f"Error sending data: {e}")

# Function to continuously receive data from the server
async def receive_data():
    try:
        while True:
            message = await conn.get()  # Exclusive access to recv() guaranteed
            if message:
                data = json.loads(message)
                print(f"Received data: {data}")
    except Exception as e:
        print(f"Error receiving data: {e}")

# Main function to manage connection, sending, and receiving
async def main():
    # Establish the connection
    await connect()

    # Start receiving data
    receive_task = asyncio.create_task(receive_data())

    # Send data to the server
    await send_data()

    # Wait for the receive task (optional; adjust logic for periodic sends)
    await receive_task

# Run the main event loop
asyncio.run(main())
