# Game Setup
import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('o3-mini')

clock = pygame.time.Clock()
FONT = pygame.font.SysFont('Arial', 24)

# Colors
LIGHT_BLUE = (173, 216, 230)  # Starting background color
LIGHT_SHADES = [LIGHT_BLUE, (224, 255, 255), (240, 248, 255), (230, 230, 250)]

DARK_COLORS = [(0, 0, 0), (25, 25, 112), (0, 0, 139), (139, 0, 0), (0, 100, 0)]

LAND_COLORS = [(101, 67, 33), (218, 165, 32)]  # dark brown or yellow
PIPE_COLORS = [(0, 100, 0), (181, 101, 29), (105, 105, 105)]  # dark green, light brown, dark gray

# Game variables
GRAVITY = 0.25
FLAP_STRENGTH = -6

PIPE_WIDTH = 60
PIPE_GAP = 150  # Gap height between top and bottom pipe
PIPE_FREQUENCY = 1500  # milliseconds

GROUND_HEIGHT = 50

# Bird class
def create_bird():
    # Randomly choose shape: square, circle, or triangle
    shape = random.choice(['square', 'circle', 'triangle'])
    color = random.choice(DARK_COLORS)
    size = 30
    return {'shape': shape,
            'color': color,
            'x': 100,
            'y': SCREEN_HEIGHT // 2,
            'size': size,
            'vel': 0}


def draw_bird(bird):
    if bird['shape'] == 'square':
        pygame.draw.rect(screen, bird['color'], (bird['x'] - bird['size']//2, bird['y'] - bird['size']//2, bird['size'], bird['size']))
    elif bird['shape'] == 'circle':
        pygame.draw.circle(screen, bird['color'], (bird['x'], bird['y']), bird['size']//2)
    elif bird['shape'] == 'triangle':
        half = bird['size'] // 2
        points = [
            (bird['x'], bird['y'] - half),
            (bird['x'] - half, bird['y'] + half),
            (bird['x'] + half, bird['y'] + half)
        ]
        pygame.draw.polygon(screen, bird['color'], points)

# Pipe functions
def create_pipe_pair():
    # Determine gap position
    gap_y = random.randint(100, SCREEN_HEIGHT - GROUND_HEIGHT - 100 - PIPE_GAP)
    color = random.choice(PIPE_COLORS)
    pipe = {
        'x': SCREEN_WIDTH + 10,
        'gap_y': gap_y,
        'color': color
    }
    return pipe


def draw_pipes(pipe):
    # Top pipe: from top to gap_y
    pygame.draw.rect(screen, pipe['color'], (pipe['x'], 0, PIPE_WIDTH, pipe['gap_y']))
    # Bottom pipe: from gap_y + PIPE_GAP to ground top
    bottom_pipe_height = SCREEN_HEIGHT - GROUND_HEIGHT - (pipe['gap_y'] + PIPE_GAP)
    pygame.draw.rect(screen, pipe['color'], (pipe['x'], pipe['gap_y'] + PIPE_GAP, PIPE_WIDTH, bottom_pipe_height))


def move_pipes(pipes, speed):
    for pipe in pipes:
        pipe['x'] -= speed
    # Remove pipes that are out of screen
    return [pipe for pipe in pipes if pipe['x'] + PIPE_WIDTH > 0]

# Land
LAND_COLOR = random.choice(LAND_COLORS)

def draw_land():
    pygame.draw.rect(screen, LAND_COLOR, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
    # Add overlay text
    overlay_text = FONT.render('o3-mini', True, (255, 255, 255))  # White text
    text_rect = overlay_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - GROUND_HEIGHT//2))
    screen.blit(overlay_text, text_rect)

# Display score

def display_score(score):
    score_text = FONT.render(f'Score: {score}', True, (0, 0, 0))
    screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))


def display_game_over(current_score, best_score):
    game_over_text = FONT.render(f'Game Over! Score: {current_score}  Best: {best_score}', True, (255, 0, 0))
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(game_over_text, text_rect)

# Main game loop

def main_game():
    # Use a random background that is light; start with light blue
    background_color = LIGHT_BLUE
    # initialize bird and pipes
    bird = create_bird()
    pipes = []
    score = 0
    best_score = 0
    game_active = True

    # Timer event for pipe generation
    PIPE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(PIPE_EVENT, PIPE_FREQUENCY)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        # Accelerate the bird: pressing SPACE multiple times accelerates the bird upward
                        bird['vel'] = FLAP_STRENGTH
                    else:
                        # Restarting game
                        bird = create_bird()
                        pipes = []
                        score = 0
                        # Change background color randomly from light shades on restart
                        background_color = random.choice(LIGHT_SHADES)
                        # Also choose new land color
                        global LAND_COLOR
                        LAND_COLOR = random.choice(LAND_COLORS)
                        game_active = True
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == PIPE_EVENT and game_active:
                pipes.append(create_pipe_pair())

        if game_active:
            # Update bird
            bird['vel'] += GRAVITY
            bird['y'] += bird['vel']

            # Collision with ground
            if bird['y'] + bird['size'] // 2 > SCREEN_HEIGHT - GROUND_HEIGHT or bird['y'] - bird['size'] // 2 < 0:
                game_active = False
                best_score = max(best_score, score)

            # Move pipes
            pipes = move_pipes(pipes, 3)

            # Check collision with pipes and increase score if passed
            for pipe in pipes:
                # Check collision with top pipe
                bird_rect = pygame.Rect(bird['x'] - bird['size']//2, bird['y'] - bird['size']//2, bird['size'], bird['size'])
                top_pipe_rect = pygame.Rect(pipe['x'], 0, PIPE_WIDTH, pipe['gap_y'])
                bottom_pipe_rect = pygame.Rect(pipe['x'], pipe['gap_y'] + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - (pipe['gap_y'] + PIPE_GAP))
                if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
                    game_active = False
                    best_score = max(best_score, score)
                # Increase score: when bird passes the center of the pipe
                if pipe['x'] + PIPE_WIDTH//2 < bird['x'] and not pipe.get('scored', False):
                    score += 1
                    pipe['scored'] = True

        # Draw everything
        screen.fill(background_color)
        
        if game_active:
            draw_bird(bird)
            for pipe in pipes:
                draw_pipes(pipe)
            draw_land()
            display_score(score)
        else:
            draw_land()
            display_game_over(score, best_score)

        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main_game()
