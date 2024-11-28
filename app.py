#=======================================================================
# TODO:
# 1. Create basic game
# 2. Create menu page
# 3. Implement multiplayer
#=======================================================================


import pygame

pygame.init()
screen = pygame.display.set_mode([500, 700])
running = True

# Päästään käsiksi aikaan koodin sisällä
clock = pygame.time.Clock()

w, h = pygame.display.get_surface().get_size()

x = w/2
y = 150


v = 100

while running:        
    # Aika edellisestä näytön päivityksestä (deltaTime)
    dt = clock.tick(60)/1000
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                print("Left pressed")
                x -= 100
            if event.key == pygame.K_d:
                print("Right pressed")
                x += 100
            if event.key == pygame.K_SPACE:
                print("Space pressed")
                y-=v*dt
    
    screen.fill((255, 255, 255))

    # Liikuta palloa 100px oikealle sekunnissa riippumatta pelin nopeudesta
    #x +=100*dt

    # Sijoita pallo takaisin alkupisteeseensä
    if(y > h-85):
        k=0.95
        v=-100
    else:
        k=1.05

    

    y+= v*dt
    v*=k

    

    pygame.draw.circle(screen, (0, 0, 255), (x, y), 75)
    pygame.display.flip()


pygame.quit()