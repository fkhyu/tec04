import requests
import json

# Define the server URL
server_url = 'http://localhost:8000/server.php'

# Example snake data
snake_data = {
    'player1': {
        'position': {'x': 100, 'y': 150},
        'direction': {'x': 1, 'y': 0}
    }
}

# Send data to the server via POST request
response = requests.post(server_url, json=snake_data)

# Print the server's response
print(response.json())  # This will print the response from the PHP server
