# server.py
import random
import asyncio
import websockets
import json
from enum import Enum

class GameState(Enum):
    WAITING = "waiting"
    RUNNING = "running"
    FINISHED = "finished"

class GameServer:
    def __init__(self, min_players=2):
        self.clients = {}
        self.game_state = {
            "snakes": {},  
            "food": [],
            "scores": {},
            "alive": {},  # Track alive status
        }
        self.current_state = GameState.WAITING
        self.min_players = min_players
        self.broadcast_interval = 0.03  # 10ms broadcast interval

    def spawn_boosts(self, count, world_size):
        return [
            {
                "x": random.randint(-world_size, world_size),
                "y": random.randint(-world_size, world_size),
                "id": str(random.randint(1000, 9999))
            }
            for _ in range(count)
        ]

    async def broadcast_state(self):
        state_update = {
            "status": self.current_state.value,
            "game_state": self.game_state,
            "player_count": len(self.clients)
        }

        disconnected_clients = []
        for client_id, client in self.clients.items():
            try:
                await client.send(json.dumps(state_update))
            except websockets.ConnectionClosed:
                disconnected_clients.append(client_id)

        for client_id in disconnected_clients:
            await self.remove_client(client_id)

    async def remove_client(self, client_id):
        self.clients.pop(client_id)
        self.game_state["snakes"].pop(client_id)
        self.game_state["scores"].pop(client_id)
        self.game_state["alive"].pop(client_id)

        if len(self.clients) < self.min_players and self.current_state == GameState.RUNNING:
            self.current_state = GameState.WAITING
            print("Not enough players, game state reset to WAITING.")

    def check_boost_collision(self, client_id):
        head = self.game_state['snakes'][client_id][0]
        for food in self.game_state['food']:
            distance = ((head['x'] - food['x'])**2 + (head['y'] - food['y'])**2)**0.5
            if distance < 20:  # Increased collision threshold
                self.game_state['food'].remove(food)
                # Add two segments to make snake growth more noticeable
                self.game_state['snakes'][client_id].extend([
                    {"x": self.game_state['snakes'][client_id][-1]["x"],
                    "y": self.game_state['snakes'][client_id][-1]["y"]} for _ in range(2)
                ])
                break


    def check_snake_collisions(self, client_id):
        head = self.game_state['snakes'][client_id][0]
        for other_id, other_snake in self.game_state['snakes'].items():
            if other_id != client_id and self.game_state['alive'][other_id]:
                for segment in other_snake[1:]:  # Ignore other snake's head
                    distance = ((head['x'] - segment['x'])**2 + (head['y'] - segment['y'])**2)**0.5
                    if distance < 20:  # Collision threshold
                        self.game_state['alive'][client_id] = False
                        return

    async def check_game_state(self):
        while True:
            try:
                if self.current_state == GameState.WAITING and len(self.clients) >= self.min_players:
                    self.current_state = GameState.RUNNING
                    print("Game state changed to RUNNING")
                    self.game_state['food'] = self.spawn_boosts(5, 100)
                    # Reset alive status for all current clients
                    for client_id in self.clients:
                        self.game_state['alive'][client_id] = True
                        # Respawn snake at random location
                        random.seed(client_id)
                        randomhead = random.randint(-100,100)
                        self.game_state["snakes"][client_id] = [
                            {'x': randomhead, 'y': randomhead}, 
                            {'x': randomhead-10, 'y': randomhead}, 
                            {'x': randomhead-20, 'y': randomhead}
                        ]
                        self.game_state["scores"][client_id] = 0

                elif self.current_state == GameState.RUNNING:
                    if len(self.game_state['food']) < 5:
                        self.game_state['food'].extend(
                            self.spawn_boosts(5 - len(self.game_state['food']), 100)
                        )

                    # Check for collisions
                    for client_id in list(self.clients.keys()):
                        if self.game_state['alive'].get(client_id, False):
                            self.check_boost_collision(client_id)
                            self.check_snake_collisions(client_id)

                    # Check if only one player is left
                    alive_players = [id for id, alive in self.game_state['alive'].items() if alive]
                    if len(alive_players) <= 1:
                        self.current_state = GameState.FINISHED
                        if alive_players:
                            print(f"Player {alive_players[0]} wins!")
                        else:
                            print("All players died!")

                elif self.current_state == GameState.FINISHED:
                    # Automatically reset to WAITING state after a short delay
                    await asyncio.sleep(3)
                    self.current_state = GameState.WAITING
                    print("Game reset to WAITING state")

                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error in check_game_state: {e}")
                await asyncio.sleep(1)

    async def continuous_broadcast(self):
        while True:
            try:
                await self.broadcast_state()
                await asyncio.sleep(self.broadcast_interval)
            except Exception as e:
                print(f"Error in continuous_broadcast: {e}")
                await asyncio.sleep(self.broadcast_interval)

    async def handle_client(self, websocket):
        client_id = str(id(websocket))
        self.clients[client_id] = websocket
        random.seed(client_id)
        randomhead = random.randint(-100,100)
        self.game_state["snakes"][client_id] = [{'x': randomhead, 'y': randomhead}, {'x': randomhead-10, 'y': randomhead}, {'x': randomhead-20, 'y': randomhead}]
        self.game_state["scores"][client_id] = 0
        self.game_state["alive"][client_id] = True
        
        print(f"New client connected: {client_id}")

        try:
            await websocket.send(json.dumps({
                "client_id": client_id,
                "status": self.current_state.value,
                "game_state": self.game_state,
                "player_count": len(self.clients)
            }))

            async for message in websocket:
                try:
                    if self.current_state == GameState.RUNNING:
                        data = json.loads(message)
                        if isinstance(data, list):
                            self.game_state['snakes'][client_id] = data
                except json.JSONDecodeError:
                    print(f"Invalid message from {client_id}: {message}")
                except Exception as e:
                    print(f"Error processing message from {client_id}: {e}")

        except websockets.ConnectionClosed:
            print(f"Client disconnected: {client_id}")
        finally:
            await self.remove_client(client_id)

async def main():
    game_server = GameServer(min_players=2)

    async with websockets.serve(game_server.handle_client, "localhost", 8081):
        print("Server started at ws://localhost:8081")
        await asyncio.gather(
            game_server.check_game_state(),
            game_server.continuous_broadcast(),
            asyncio.Future()
        )

if __name__ == "__main__":
    asyncio.run(main())