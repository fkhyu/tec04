import asyncio
import json
import sys
from termcolor import colored
from ws import Connection

class GameClient:
    def __init__(self, server_url):
        self.conn = Connection(server_url)
        self.client_id = None
        self.game_state = None
        self.status = None
        self.snake = [{'x': 11, 'y': 20}, {'x': 30, 'y': 40}]

    async def connect(self):
        try:
            await self.conn.connect()
            print("WebSocket connection established.")
            response = await self.conn.get()
            data = json.loads(response)
            self.client_id = data["client_id"]
            self.game_state = data["game_state"]
            self.status = data["status"]
            print(f"Connected with ID: {self.client_id}")
            print(f"Current game state: {self.game_state}")
            print(f"Players connected: {data['player_count']}")
            print(f"Game status: {self.status}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            sys.exit(1)

    async def game_loop(self):
        try:
            while True:
                await self.conn.send(json.dumps(self.snake))
                print(f"Sent snake position: {self.snake}")
                
                message = await self.conn.get()
                if message:
                    data = json.loads(message)
                    prev_state = self.game_state
                    self.game_state = data["game_state"]
                    
                    if prev_state != self.game_state:
                        if self.game_state == "running":
                            print(colored("Game started!", "green"))
                        elif self.game_state == "waiting":
                            print(colored("Waiting for players...", "yellow"))
                    
                    print(f"Players: {data['player_count']}, State: {self.game_state}")

                await asyncio.sleep(0.05)
                    
        except Exception as e:
            print(f"Error in game loop: {e}")
            await self.conn.close()
            sys.exit(1)

async def main():
    server_url = 'ws://65.109.231.169/tec04/'
    client = GameClient(server_url)
    await client.connect()
    await client.game_loop()

if __name__ == "__main__":
    asyncio.run(main())