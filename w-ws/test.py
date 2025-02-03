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
        self.game_state = {
            'snakes': {},
            'food': [],
            'scores': {}
        }
        self.status = None

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
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False

    async def update_server(self, snake_position):
        try:
            await self.conn.send(json.dumps(snake_position))
            message = await self.conn.get()
            if message:
                data = json.loads(message)
                self.game_state = data["game_state"]
                return True
        except Exception as e:
            print(f"Error updating server: {e}")
            return False

async def main():
    pygame.init()
    w, h = 800, 600
    screen = pygame.display.set_mode([w, h])
    clock = pygame.time.Clock()
    
    server_url = 'ws://65.109.231.169/tec04/'
    client = GameClient(server_url)
    if not await client.connect():
        pygame.quit()
        return

    world_size = 800
    r = 10 
    v = 300
    a = 1.00005
    center_x, center_y = w // 2, h // 2

    death_font = pygame.font.Font(None, 74)
    death_text = death_font.render("You Died!", True, (255, 0, 0))
    death_text_rect = death_text.get_rect(center=(w//2, h//2))
    
    snake = [{"x": 0, "y": 0}]
    for i in range(4):
        snake.append({"x": snake[-1]["x"], "y": snake[-1]["y"] + int(0.6 * r)})
    
    background_image = pygame.image.load("/Users/user/Desktop/tec04/w-ws/v6.png")
    bg_image_scaled = pygame.transform.scale(background_image, (2 * world_size, 2 * world_size))
    
    running = True
    game_over = False
    while running:
        v *= a
        delta_time = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_over and event.type == pygame.KEYDOWN:
                game_over = False

        if not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        v *= 2
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        v /= 2

            if not client.game_state['alive'].get(client.client_id, True):
                game_over = True


        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - center_x
        dy = mouse_y - center_y
        distance_to_cursor = math.sqrt(dx**2 + dy**2)
        
        if distance_to_cursor != 0:
            direction = {"x": dx / distance_to_cursor, "y": dy / distance_to_cursor}
            
            new_head_x = snake[0]["x"] + direction["x"] * v * delta_time
            new_head_y = snake[0]["y"] + direction["y"] * v * delta_time
            
            if -world_size <= new_head_x <= world_size:
                snake[0]["x"] = new_head_x
            if -world_size <= new_head_y <= world_size:
                snake[0]["y"] = new_head_y

        for i in range(len(snake) - 1, 0, -1):
            snake[i]["x"] = snake[i - 1]["x"]
            snake[i]["y"] = snake[i - 1]["y"]

        await client.update_server(snake)

        screen.fill((20, 30, 50))
        
        if not game_over:
            bg_offset_x = int((snake[0]["x"] + world_size) % background_image.get_width())
            bg_offset_y = int((snake[0]["y"] + world_size) % background_image.get_height())
            screen.blit(bg_image_scaled, (center_x - bg_offset_x, center_y - bg_offset_y))
            
            border_top_left = (center_x + (-world_size - snake[0]["x"]), center_y + (-world_size - snake[0]["y"]))
            pygame.draw.rect(screen, (255, 0, 0), (*border_top_left, 2 * world_size, 2 * world_size), 5)

            for segment in snake:
                screen_x = center_x + (segment["x"] - snake[0]["x"])
                screen_y = center_y + (segment["y"] - snake[0]["y"])
                pygame.draw.circle(screen, (30, 30, 30), (int(screen_x), int(screen_y)), r)

            for player_id, other_snake in client.game_state['snakes'].items():
                if player_id != client.client_id:
                    for segment in other_snake:
                        screen_x = center_x + (segment['x'] - snake[0]['x'])
                        screen_y = center_y + (segment['y'] - snake[0]['y'])
                        pygame.draw.circle(screen, (30, 30, 200), (int(screen_x), int(screen_y)), r)

            # Draw food
            # for food in client.game_state['food']:
            #     food_screen_x = center_x + (food["x"] - snake[0]["x"])
            #     food_screen_y = center_y + (food["y"] - snake[0]["y"])
            #     pygame.draw.circle(screen, (0, 180, 89), (int(food_screen_x), int(food_screen_y)), r+2)
            #     pygame.draw.circle(screen, (0, 255, 183), (int(food_screen_x), int(food_screen_y)), r)
        else:
            screen.fill((0, 0, 0))
            screen.blit(death_text, death_text_rect)

        pygame.display.set_caption(f"X: {snake[0]['x']:.2f}, Y: {snake[0]['y']:.2f} | {client.client_id}")
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())