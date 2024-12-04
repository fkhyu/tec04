import pygame
import math
import random
import sys
import requests
import uuid

# Server URL
server_url = 'http://10.97.98.142:8000/server/server.php'

# Define a unique client ID (this could be any string or identifier)
client_id = str(uuid.uuid4())

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
            # print(f"Data received from other clients: {data}")
            return data
        else:
            print("No shared data found.")
    else:
        print(f"Failed to get data. Status code: {response.status_code}")

def from_data(my_key, data):
    for key, value in data.items():
        try :
            if key == my_key:
                return value
        except:
            pass


# ======================== Pygame Snake Game ========================

pygame.init()

# Screen setup
w, h = 800, 600
screen = pygame.display.set_mode([w, h])
# pygame.display.set_caption("WTS - What The Snake")
pygame.display.set_caption(client_id)

running = True
clock = pygame.time.Clock()

# Snake initialization
r = 20  # Circle radius
segment_distance = int(0.6 * r)  # Distance between segments
snake = [{"x": 0, "y": 0}]  # Start the snake at the world origin
for i in range(4):  # Add initial body segments
    snake.append({"x": snake[-1]["x"], "y": snake[-1]["y"] + segment_distance})

v = 100  # Speed in pixels/second
a = 1.00001  # Speed multiplier
max_fps = 60  # Maximum frames per second
direction = {"x": 0, "y": 1}  # Initial direction

# Boost initialization
boost_radius = 10  # Small boost size
boost_count = 70  # Number of boosts
boosts = []  # List of boosts
boost_timer = 0  # Tracks time for adding new boosts

# Finite world size (square)
world_size = 800  # Total size of the world (centered at origin)
font = pygame.font.SysFont("Arial", 50)

# Center of the screen (snake's head stays here)
center_x, center_y = w // 2, h // 2

# Load background image
background_image = pygame.image.load("./src/v6.png")
bg_width, bg_height = background_image.get_size()

# Scale the background image to fit the world (not the entire screen)
bg_image_scaled = pygame.transform.scale(background_image, (2 * world_size, 2 * world_size))

# Function to spawn boosts randomly within the finite world
def spawn_boosts(count, world_size):
    return [
        {"x": random.randint(-world_size, world_size), "y": random.randint(-world_size, world_size)}
        for _ in range(count)
    ]

# Generate initial boosts
boosts = spawn_boosts(boost_count, world_size)


while running:
    send_data(snake)
    # get_data()
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

    # Add 5 new boosts every 60 seconds
    boost_timer += delta_time
    if boost_timer >= 60:
        boosts += spawn_boosts(5, world_size)
        boost_timer = 0

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
    
    pygame.display.set_caption(f"X: {snake[0]['x']:.2f}, Y: {snake[0]['y']:.2f} | {client_id}")

    # Check for out-of-bounds
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

    # Draw all boosts
    for boost in boosts:
        boost_screen_x = center_x + (boost["x"] - snake[0]["x"])
        boost_screen_y = center_y + (boost["y"] - snake[0]["y"])
        pygame.draw.circle(screen, (0, 180, 89), (int(boost_screen_x), int(boost_screen_y)), boost_radius+2)
        pygame.draw.circle(screen, (0, 255, 183), (int(boost_screen_x), int(boost_screen_y)), boost_radius)

    pygame.display.flip()

pygame.quit()
