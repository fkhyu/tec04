import pygame
import math
import random
import asyncio
import json
import sys

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
                            print(("Game started!", "green"))
                        elif self.game_state == "waiting":
                            print(("Waiting for players...", "yellow"))
                    
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

def get_snake(n):
    # Players: 2, State: {'snakes': {'140560609385568': [{'x': 11, 'y': 20}, {'x': 30, 'y': 40}], '140560609388208': [{'x': 11, 'y': 20}, {'x': 30, 'y': 40}]}, 'food': [{'x': 92, 'y': -65, 'id': '9518'}, {'x': 47, 'y': -15, 'id': '5579'}, {'x': 14, 'y': 77, 'id': '4333'}, {'x': -73, 'y': -49, 'id': '8528'}, {'x': -38, 'y': -76, 'id': '4764'}], 'scores': {'140560609385568': 0, '140560609388208': 0}}
    snake = GameClient.game_state['snakes'][n]
    for key in snake:
        return snake[key]
    
print(get_snake(1))

# ======================== Pygame Snake Game ========================

pygame.init()

# Screen setup
w, h = 800, 600
screen = pygame.display.set_mode([w, h])
# pygame.display.set_caption("WTS - What The Snake")
pygame.display.set_caption(GameClient.client_id)

running = True
clock = pygame.time.Clock()

state = GameClient.game_state
snakes = state['snakes']
boosts = state['food']

r = 10
segment_distance = int(0.6 * r)
snake = [{"x": 0, "y": 0}]
for i in range(4):
    snake.append({"x": snake[-1]["x"], "y": snake[-1]["y"] + segment_distance})

v = 100
a = 1.0001
max_fps = 60
direction = {"x": 0, "y": 1}

boost_radius = 10
boosts = []

world_size = 800
font = pygame.font.SysFont("Arial", 50)

center_x, center_y = w // 2, h // 2

background_image = pygame.image.load("./src/v6.png")
bg_width, bg_height = background_image.get_size()

bg_image_scaled = pygame.transform.scale(background_image, (2 * world_size, 2 * world_size))

while running:
    v *= a  # Gradually increase speed
    delta_time = clock.tick(max_fps) / 1000  # Limit to 60 FPS for smooth performance

    # Get and print FPS
    # fps = clock.get_fps()  # Get the current FPS
    # print(f"FPS: {fps:.2f}")  # Print FPS in the console with two decimal places

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                v *= 2
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                v /= 2

    # Get the mouse position and calculate direction
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - center_x  # Relative to the screen center
    dy = mouse_y - center_y
    distance_to_cursor = math.sqrt(dx**2 + dy**2)

    if distance_to_cursor != 0:
        direction = {"x": dx / distance_to_cursor, "y": dy / distance_to_cursor}

    # Update the head position in the world
    new_head_x = snake[0]["x"] + direction["x"] * v * delta_time
    new_head_y = snake[0]["y"] + direction["y"] * v * delta_time

    # Prevent the snake from leaving the world boundaries
    if -world_size <= new_head_x <= world_size:
        snake[0]["x"] = new_head_x
    if -world_size <= new_head_y <= world_size:
        snake[0]["y"] = new_head_y
    
    pygame.display.set_caption(f"X: {snake[0]["x"]:.2f}, Y: {snake[0]["y"]:.2f} | {GameClient.client_id}")

    # # Check for out-of-bounds
    # if not (-world_size <= new_head_x <= world_size) or not (-world_size <= new_head_y <= world_size):
    #     running = False
    #     # Render the "Game Over" text
    #     popup = pygame.Surface((w/2, h/2), pygame.SRCALPHA)
    #     pygame.draw.rect(popup, (0, 0, 0, 230), pygame.Rect(0, 0, w / 2, h / 2), border_radius=20)  # White with rounded corners
    #     game_over_text = pygame.font.SysFont("Arial", 50, "Bold").render("Game Over", True, (255, 255, 0))
    #     score = pygame.font.SysFont("Arial", 25).render(f"Your score: {len(snake)-5}", True, (255, 255, 255))
    #     # Position the text at the center of the screen
    #     screen.blit(popup, (w / 4, h / 4))
    #     screen.blit(game_over_text, (w / 3, h / 2.4))
    #     screen.blit(score, (w / 2.5, h / 1.9))
    #     pygame.display.update()  # Update the display
    #     pygame.time.wait(3000)  # Wait for 3 seconds before quitting
    #     pygame.quit()  # Quit Pygame
    #     sys.exit()  # Exit the program

    # Update the body segments
    for i in range(len(snake) - 1, 0, -1):
        snake[i]["x"] = snake[i - 1]["x"]
        snake[i]["y"] = snake[i - 1]["y"]

    # Check collisions with all boosts
    collected_boosts = []
    for boost in boosts:
        dist_to_boost = math.sqrt((snake[0]["x"] - boost["x"]) ** 2 + (snake[0]["y"] - boost["y"]) ** 2)
        if dist_to_boost < r + boost_radius:
            # Collect boost and add a new segment
            collected_boosts.append(boost)
            last_segment = snake[-1]
            snake.append({"x": last_segment["x"], "y": last_segment["y"]})

    # Remove collected boosts from the list
    for boost in collected_boosts:
        boosts.remove(boost)

    # Drawing
    # Draw the dark blue background outside the world
    screen.fill((20, 30, 50))

    # Calculate the position of the background image based on the snake's position
    bg_offset_x = int((snake[0]["x"] + world_size) % bg_width)
    bg_offset_y = int((snake[0]["y"] + world_size) % bg_height)

    # Draw the background image multiple times to cover the whole world
    screen.blit(bg_image_scaled, (center_x - bg_offset_x, center_y - bg_offset_y))

    # Draw the red world border with a subtle glow
    border_top_left = (center_x + (-world_size - snake[0]["x"]), center_y + (-world_size - snake[0]["y"]))
    border_bottom_right = (center_x + (world_size - snake[0]["x"]), center_y + (world_size - snake[0]["y"]))
    pygame.draw.rect(screen, (255, 0, 0), (*border_top_left, 2 * world_size, 2 * world_size), 5)

    # Draw the snake
    for i, segment in enumerate(snake):
        screen_x = center_x + (segment["x"] - snake[0]["x"])  # Offset by head
        screen_y = center_y + (segment["y"] - snake[0]["y"])
        color = (30, 30, 30)
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), r)


    snake2 = get_snake()
    if not snake2:
        print("No second snake to draw.")
    else:
        print(f"Drawing second snake: {snake2}")
        for segment in snake2:
            try:
                screen_x = center_x + (segment['x'] - snake[0]['x'])
                screen_y = center_y + (segment['y'] - snake[0]['y'])
                pygame.draw.circle(screen, (30, 30, 200), (int(screen_x), int(screen_y)), r)
                print(f"Drawn segment at ({segment['x']:.2f}, {segment['y']:.2f})")
            except KeyError as e:
                print(f"Invalid segment data: {segment}, error: {e}")
        

    # Draw all boosts
    for boost in boosts:
        boost_screen_x = center_x + (boost["x"] - snake[0]["x"])
        boost_screen_y = center_y + (boost["y"] - snake[0]["y"])
        pygame.draw.circle(screen, (0, 180, 89), (int(boost_screen_x), int(boost_screen_y)), boost_radius+2)
        pygame.draw.circle(screen, (0, 255, 183), (int(boost_screen_x), int(boost_screen_y)), boost_radius)

    pygame.display.flip()

pygame.quit()
