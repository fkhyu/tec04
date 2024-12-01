import requests
import time
import json

# Server URL
server_url = 'http://localhost:8000/server.php'

# Define a unique client ID (this could be any string or identifier)
client_id = 'client2'

# Function to send data to the server
def send_data(message):
    data_to_send = {'client_id': client_id, 'message': message}
    response = requests.post(server_url, json=data_to_send)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            print("Data successfully sent to the server.")
        else:
            print("Failed to send data.")
    else:
        print(f"Failed to send data. Status code: {response.status_code}")

# Function to retrieve data from the server (other clients' data)
def get_data():
    params = {'client_id': client_id}
    response = requests.get(server_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict):
            print(f"Data received from other clients: {data}")
        else:
            print("No shared data found.")
    else:
        print(f"Failed to get data. Status code: {response.status_code}")

# Loop that sends and receives data every 1 second
while True:
    send_data("Hello from client2!")
    get_data()
    time.sleep(1)
