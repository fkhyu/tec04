import pygame
import math
import random
import time
from collections import deque

pygame.init()

w, h = 800, 600
screen = pygame.display.set_mode([w, h])

running = True
clock = pygame.time.Clock()

# Snake initialization
r = 25  # Circle radius
segment_distance = int(0.5 * r)  # Distance between segments (120% of radius)
snake = [{"x": w / 2, "y": 150}]  # Head of the snake
for i in range(5):  # Add 5 more segments
    snake.append({"x": snake[-1]["x"], "y": snake[-1]["y"] + segment_distance})

v = 200  # Speed in pixels/second
a = 1.00001  # Speed multiplier

direction = {"x": 0, "y": 1}  # Initial direction
target_mode = False  # Snake is not currently passing through cursor

# Boost initialization
boost_radius = 20
boost = None  # No boost initially
boost_time = time.time()  # Track time when the last boost appeared
boost_claimed_time = None  # New variable to track when the boost was claimed

# Path queue to store head's movement history
path_queue = deque()  # Stores the history of head's positions
print(path_queue)

max_queue_length = 10000  # Avoid unlimited memory growth

# Function to create the radial gradient background
def create_radial_gradient():
    bg_surface = pygame.Surface((w, h))
    center_x, center_y = w // 2, h // 2
    
    for x in range(w):
        for y in range(h):
            dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
            norm_dist = dist / max_dist
            color_value = int(255 * (1 - norm_dist) + 128 * norm_dist)
            bg_surface.set_at((x, y), (color_value, color_value, color_value))
    
    return bg_surface

bg_image = create_radial_gradient()

# Function to spawn a new boost randomly
def spawn_boost():
    return {"x": random.randint(boost_radius, w - boost_radius),
            "y": random.randint(boost_radius, h - boost_radius)}

# Initial boost spawn
boost = spawn_boost()

while running:
    v = v * a
    delta_time = clock.tick(60) / 1000  # Time since last frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the position of the mouse
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate direction vector from head to target
    if not target_mode:
        dx = mouse_x - snake[0]["x"]
        dy = mouse_y - snake[0]["y"]
        distance_to_cursor = math.sqrt(dx**2 + dy**2)

        if distance_to_cursor != 0:
            direction = {"x": dx / distance_to_cursor, "y": dy / distance_to_cursor}
    else:
        dx = direction["x"]
        dy = direction["y"]

    # Move the head
    new_head_x = snake[0]["x"] + direction["x"] * v * delta_time
    new_head_y = snake[0]["y"] + direction["y"] * v * delta_time
    snake[0]["x"], snake[0]["y"] = new_head_x, new_head_y

    # Record the head's position in the path queue
    path_queue.append({"x": new_head_x, "y": new_head_y})

    # Limit the queue length to prevent excessive memory usage
    if len(path_queue) > max_queue_length:
        path_queue.popleft()

    # Smooth screen wrapping for the head
    if snake[0]["x"] > w + r:
        snake[0]["x"] -= w + 2 * r
    elif snake[0]["x"] < -r:
        snake[0]["x"] += w + 2 * r
    if snake[0]["y"] > h + r:
        snake[0]["y"] -= h + 2 * r
    elif snake[0]["y"] < -r:
        snake[0]["y"] += h + 2 * r

    # Check if head is near the cursor
    if distance_to_cursor < r and not target_mode:
        target_mode = True
    elif target_mode:
        if math.sqrt((snake[0]["x"] - mouse_x) ** 2 + (snake[0]["y"] - mouse_y) ** 2) > 2 * r:
            target_mode = False

    # Update body segments to follow the path of the head
    for i in range(len(snake)-1, 0, -1):  # Start from the last segment and move to the second one
        # Calculate target position for each segment based on its distance
        target_index = (len(snake) - i) * segment_distance
        if target_index < len(path_queue):
            snake[i]["x"] = path_queue[target_index]["x"]
            snake[i]["y"] = path_queue[target_index]["y"]

    # Remove old positions from the queue
    while len(path_queue) > len(snake) * segment_distance:
        path_queue.popleft()

    # Check for collision with boost
    snake_head = snake[0]
    dist_to_boost = math.sqrt((snake_head["x"] - boost["x"]) ** 2 + (snake_head["y"] - boost["y"]) ** 2)
    
    if dist_to_boost < r + boost_radius:
        # Add a new segment to the snake
        last_segment = snake[-1]  # This should be the last segment, not the second
        snake.append({"x": last_segment["x"], "y": last_segment["y"]})
        
        # Set boost claimed time to current time
        boost_claimed_time = time.time()
        
        # Move the boost to a new random location
        boost = spawn_boost()

    # Periodically spawn a new boost (after 8-20 seconds from the last claim)
    if boost_claimed_time is not None and time.time() - boost_claimed_time > random.uniform(8, 20):
        boost = spawn_boost()
        boost_claimed_time = None  # Reset the claimed time after spawning the new boost

    # Drawing
    screen.blit(bg_image, (0, 0))  # Draw background
    for i in range(len(snake)-1, -1, -1):  # Draw from the tail to the head
        segment = snake[i]
        if i == 0:
            color = (0, 0, 255)  # Blue for the head
        elif i == len(snake) - 1:
            color = (255, 0, 0)  # red for the tail
        else:
            color = (0, 0, 0)  # Black for the body
        pygame.draw.circle(screen, color, (int(segment["x"]), int(segment["y"])), r)

    # Draw the boost
    pygame.draw.circle(screen, (0, 255, 0), (int(boost["x"]), int(boost["y"])), boost_radius)

    pygame.display.flip()

pygame.quit()