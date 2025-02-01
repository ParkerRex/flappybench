import pygame
import sys
import random

pygame.init()

# ------------------
# Window and clock
# ------------------
WIDTH, HEIGHT = 400, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("o1")
clock = pygame.time.Clock()

# ------------------
# Helper functions
# ------------------

def get_random_light_color():
    """
    Returns a random "light" color. 
    You can tweak the ranges to ensure the colors are sufficiently light.
    """
    r = random.randint(150, 255)
    g = random.randint(150, 255)
    b = random.randint(150, 255)
    return (r, g, b)

def get_random_dark_color():
    """
    Returns a random "dark" color.
    You can tweak the ranges to ensure the colors are sufficiently dark.
    """
    r = random.randint(0, 100)
    g = random.randint(0, 100)
    b = random.randint(0, 100)
    return (r, g, b)

def get_random_land_color():
    """
    Returns dark brown or yellow chosen randomly.
    """
    # Dark brown (approx) or yellow
    colors = [(101, 67, 33), (255, 255, 0)]
    return random.choice(colors)

def get_random_pipe_color():
    """
    Returns one of dark green, light brown, or dark gray.
    """
    colors = [
        (0, 100, 0),       # dark green
        (181, 101, 29),    # light brown
        (50, 50, 50)       # dark gray
    ]
    return random.choice(colors)

def create_bird_shape():
    """
    Randomly chooses one of three shapes: square, circle, or triangle.
    Also chooses a random dark color.
    Returns a tuple (shape_type, color).
    shape_type in {'square', 'circle', 'triangle'}.
    """
    shape_type = random.choice(['square', 'circle', 'triangle'])
    color = get_random_dark_color()
    return shape_type, color

def draw_bird(screen, shape_type, color, x, y, size=20):
    """
    Draws the bird on the screen given shape_type, color, position, and size.
    """
    if shape_type == 'square':
        pygame.draw.rect(screen, color, (x - size//2, y - size//2, size, size))
    elif shape_type == 'circle':
        pygame.draw.circle(screen, color, (x, y), size//2)
    elif shape_type == 'triangle':
        # Draw an upward-pointing triangle
        # Coordinates of triangle's vertices
        points = [
            (x, y - size//2),           # top
            (x - size//2, y + size//2), # bottom-left
            (x + size//2, y + size//2)  # bottom-right
        ]
        pygame.draw.polygon(screen, color, points)

def generate_pipe_pair(pipe_x):
    """
    Generates a single pipe pair starting at x = pipe_x.
    Returns a tuple (top_rect, bottom_rect, pipe_color).
    """
    gap_size = 150
    # random top pipe length
    top_height = random.randint(50, HEIGHT - 200)
    bottom_y = top_height + gap_size
    bottom_height = HEIGHT - bottom_y - LAND_HEIGHT
    
    pipe_color = get_random_pipe_color()
    
    top_rect = pygame.Rect(pipe_x, 0, PIPE_WIDTH, top_height)
    bottom_rect = pygame.Rect(pipe_x, bottom_y, PIPE_WIDTH, bottom_height)
    return top_rect, bottom_rect, pipe_color

def check_collision(bird_rect, pipes):
    """
    Checks if the bird_rect collides with any pipe rects or the land.
    """
    # Check land collision
    if bird_rect.bottom >= HEIGHT - LAND_HEIGHT:
        return True
    
    # Check pipe collision
    for (top_rect, bottom_rect, _) in pipes:
        if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
            return True
    return False

def draw_pipes(screen, pipes):
    """
    Draws the pipe pairs on the screen.
    """
    for (top_rect, bottom_rect, pipe_color) in pipes:
        pygame.draw.rect(screen, pipe_color, top_rect)
        pygame.draw.rect(screen, pipe_color, bottom_rect)

def draw_text(screen, text, size, color, x, y, align_right=False):
    """
    Utility to draw text on the screen.
    If align_right is True, anchor the text's right side to (x,y).
    """
    font = pygame.font.SysFont(None, size)
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if align_right:
        rect.topright = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)

# ------------------
# Global constants
# ------------------
PIPE_WIDTH = 60
PIPE_SPEED = 3
LAND_HEIGHT = 40

def main():
    # ------------------
    # Game variables
    # ------------------
    global_best_score = 0
    running = True
    
    # Initial background color (light blue), or you could randomize it
    background_color = (173, 216, 230)  # Light blue
    
    while running:
        # -------------
        # Setup / Restart
        # -------------
        # Once the player hits space to restart, randomize if you want:
        # background_color = get_random_light_color()
        
        bird_x = 50
        bird_y = HEIGHT // 2
        bird_velocity = 0
        gravity = 0.4
        jump_strength = -6

        # Random bird shape and color
        bird_shape, bird_color = create_bird_shape()
        bird_size = 30  # Larger size so shapes are more visible

        # Random land color
        land_color = get_random_land_color()

        # Create initial pipes
        pipes = []
        pipe_dist = 200
        # We generate a few pipes in front
        for i in range(3):
            pipe_x = WIDTH + i*pipe_dist
            pipes.append(generate_pipe_pair(pipe_x))

        score = 0
        game_active = False
        passed_pipe_indices = set()

        # -------------
        # Main loop for each "run" of the game
        # -------------
        while True:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_SPACE:
                        if not game_active:
                            # Start or restart the game
                            game_active = True
                            bird_velocity = jump_strength
                        else:
                            # Bird jumps
                            bird_velocity = jump_strength
            
            # -------------
            # Update game logic if active
            # -------------
            if game_active:
                # Bird movement
                bird_velocity += gravity
                bird_y += bird_velocity
                
                # Move pipes
                for i in range(len(pipes)):
                    top_rect, bottom_rect, color = pipes[i]
                    top_rect.x -= PIPE_SPEED
                    bottom_rect.x -= PIPE_SPEED
                    pipes[i] = (top_rect, bottom_rect, color)
                
                # If the leftmost pipe is off screen, pop it and add a new one
                if pipes[0][0].right < 0:
                    pipes.pop(0)
                    new_x = pipes[-1][0].x + pipe_dist
                    pipes.append(generate_pipe_pair(new_x))
                
                # Check for pipe passes for score
                for i, (top_rect, bottom_rect, _) in enumerate(pipes):
                    # If bird passes the center of a pipe pair's X and hasn't counted yet
                    pipe_center_x = top_rect.centerx
                    if pipe_center_x < bird_x and i not in passed_pipe_indices:
                        passed_pipe_indices.add(i)
                        score += 1

                # Collision check
                bird_rect = pygame.Rect(bird_x - bird_size//2, bird_y - bird_size//2, bird_size, bird_size)
                if check_collision(bird_rect, pipes):
                    game_active = False
                    # Update global best score if needed
                    if score > global_best_score:
                        global_best_score = score

                # If bird goes off the top of screen, also consider that a collision
                if bird_y + bird_size//2 < 0:
                    game_active = False
                    if score > global_best_score:
                        global_best_score = score

            # -------------
            # Drawing
            # -------------
            screen.fill(background_color)
            
            # Draw pipes
            draw_pipes(screen, pipes)
            
            # Draw bird
            draw_bird(screen, bird_shape, bird_color, bird_x, int(bird_y), bird_size)
            
            # Draw land at the bottom
            pygame.draw.rect(screen, land_color, (0, HEIGHT - LAND_HEIGHT, WIDTH, LAND_HEIGHT))
            
            # Draw "o1" text overlaying the floor
            draw_text(screen, "o1", 30, (0, 0, 0), 10, HEIGHT - LAND_HEIGHT + 5)
            
            # Draw score in top-right
            draw_text(screen, f"Score: {score}", 30, (0, 0, 0), WIDTH - 10, 10, align_right=True)
            
            # If game is over, show best score
            if not game_active:
                draw_text(screen, f"Best Score: {global_best_score}", 40, (255, 0, 0), WIDTH//2, HEIGHT//2)
                draw_text(screen, "Press SPACE to Restart, Q/Esc to Quit", 20, (0, 0, 0), WIDTH//2, HEIGHT//2 + 50)
            
            pygame.display.flip()
            
            # If not active, wait for SPACE, Q, or ESC
            if not game_active:
                # Break out of this loop to restart or quit
                # The event loop above handles Q/Esc quitting
                # So we just keep an easy break condition
                pressed_keys = pygame.key.get_pressed()
                if pressed_keys[pygame.K_SPACE]:
                    break  # restarts game
                # If user tries to close or press Q/Esc, it's handled above.

    pygame.quit()

if __name__ == "__main__":
    main()