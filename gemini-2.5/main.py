import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
LAND_HEIGHT = 100

# Bird properties
BIRD_SIZE = 20  # Radius for circle, half-side for square/triangle base
GRAVITY = 0.25
FLAP_STRENGTH = 0.6  # Amount to decrease velocity by (increase upward speed)
MAX_UP_VELOCITY = -6  # Limit how fast the bird can accelerate upwards

# Pipe properties
PIPE_WIDTH = 70
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_FREQUENCY = 1500  # Milliseconds between new pipe spawns

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Color Palettes
DARK_COLORS = [
    (40, 40, 40),
    (50, 20, 20),
    (20, 50, 20),
    (20, 20, 50),
    (80, 0, 0),
    (0, 80, 0),
    (0, 0, 80),
    (60, 60, 10),
]
LAND_COLORS = [(139, 69, 19), (218, 165, 32)]  # Dark Brown, Yellow (ish)
PIPE_COLORS = [
    (34, 139, 34),
    (205, 133, 63),
    (105, 105, 105),
]  # Dark Green, Light Brown, Dark Gray


# --- Helper Functions ---
def get_random_light_color():
    """Generates a random light color."""
    r = random.randint(180, 255)
    g = random.randint(180, 255)
    b = random.randint(180, 255)
    return (r, g, b)


def get_random_dark_color():
    """Selects a random dark color from the predefined list."""
    return random.choice(DARK_COLORS)


def get_random_land_color():
    """Selects a random land color."""
    return random.choice(LAND_COLORS)


def get_random_pipe_color():
    """Selects a random pipe color."""
    return random.choice(PIPE_COLORS)


# --- Bird Class ---
class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 4
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.size = BIRD_SIZE
        self.shape = "square"  # Default, will be randomized in reset
        self.color = BLACK  # Default, will be randomized in reset
        self.rect = pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )
        self.reset()  # Initialize with random properties

    def flap(self):
        self.velocity -= FLAP_STRENGTH
        # Limit maximum upward velocity
        if self.velocity < MAX_UP_VELOCITY:
            self.velocity = MAX_UP_VELOCITY

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

        # Prevent going above the screen
        if self.y < self.size // 2:
            self.y = self.size // 2
            self.velocity = 0  # Stop upward movement if hitting the top

        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        if self.shape == "square":
            # Adjust rect position for drawing centered square
            draw_rect = pygame.Rect(
                self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
            )
            pygame.draw.rect(screen, self.color, draw_rect)
        elif self.shape == "circle":
            pygame.draw.circle(
                screen, self.color, (self.x, int(self.y)), self.size // 2
            )
        elif self.shape == "triangle":
            # Simple isosceles triangle pointing up
            points = [
                (self.x, int(self.y - self.size // 2)),  # Top point
                (
                    int(self.x - self.size / 2),
                    int(self.y + self.size // 2),
                ),  # Bottom left
                (
                    int(self.x + self.size / 2),
                    int(self.y + self.size // 2),
                ),  # Bottom right
            ]
            pygame.draw.polygon(screen, self.color, points)

        # Update the collision rect regardless of shape (bounding box)
        # Make the collision rect slightly smaller for circles/triangles for fairness
        if self.shape != "square":
            hitbox_size = int(self.size * 0.9)  # Adjust hitbox size
            self.rect = pygame.Rect(
                self.x - hitbox_size // 2,
                self.y - hitbox_size // 2,
                hitbox_size,
                hitbox_size,
            )
        else:
            self.rect = pygame.Rect(
                self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
            )

    def reset(self):
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.shape = random.choice(["square", "circle", "triangle"])
        self.color = get_random_dark_color()
        # Adjust size slightly based on shape if desired (optional)
        if self.shape == "triangle":
            self.size = int(
                BIRD_SIZE * 1.2
            )  # Make triangle base similar size to square
        else:
            self.size = BIRD_SIZE
        self.rect = pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )


# --- Pipe Functions ---
def create_pipe():
    """Creates a new pair of pipe rects with random height and color."""
    pipe_color = get_random_pipe_color()
    pipe_height = random.randint(
        150, SCREEN_HEIGHT - LAND_HEIGHT - PIPE_GAP - 150
    )  # Random height for bottom pipe's top edge
    bottom_pipe = pygame.Rect(
        SCREEN_WIDTH, pipe_height, PIPE_WIDTH, SCREEN_HEIGHT - pipe_height - LAND_HEIGHT
    )
    top_pipe = pygame.Rect(SCREEN_WIDTH, 0, PIPE_WIDTH, pipe_height - PIPE_GAP)
    return bottom_pipe, top_pipe, pipe_color


def move_pipes(pipes):
    """Moves pipes to the left and returns pipes still on screen."""
    new_pipes = []
    for pipe_data in pipes:
        bottom_pipe, top_pipe, color, passed = pipe_data
        bottom_pipe.centerx -= PIPE_SPEED
        top_pipe.centerx -= PIPE_SPEED
        if bottom_pipe.right > 0:  # Only keep pipes that are still visible
            new_pipes.append((bottom_pipe, top_pipe, color, passed))
    return new_pipes


def draw_pipes(screen, pipes):
    """Draws all pipes."""
    for bottom_pipe, top_pipe, color, passed in pipes:
        pygame.draw.rect(screen, color, bottom_pipe)
        pygame.draw.rect(screen, color, top_pipe)


# --- Collision Function ---
def check_collision(bird, pipes, land_rect):
    """Checks for collisions between the bird, pipes, and land."""
    # Collision with land
    if bird.rect.colliderect(land_rect):
        return True

    # Collision with pipes
    for bottom_pipe, top_pipe, color, passed in pipes:
        if bird.rect.colliderect(bottom_pipe) or bird.rect.colliderect(top_pipe):
            return True

    # Collision with sky (already handled in bird.update, but good to double check)
    if (
        bird.rect.top <= 0
    ):  # Bird hit the top boundary - allow this? Let's make it not a lose condition for now.
        pass  # Bird just stops going up in update()

    return False


# --- Text Display Functions ---
def draw_score(screen, score, font):
    """Draws the current score."""
    score_text = f"Score: {score}"
    score_surface = font.render(score_text, True, BLACK)
    score_rect = score_surface.get_rect(topright=(SCREEN_WIDTH - 15, 10))
    screen.blit(score_surface, score_rect)


def draw_game_over(screen, score, best_score, font_large, font_small):
    """Draws the game over message and scores."""
    # Game Over Text
    over_text = "GAME OVER!"
    over_surface = font_large.render(over_text, True, BLACK)
    over_rect = over_surface.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)
    )
    screen.blit(over_surface, over_rect)

    # Final Score Text
    score_text = f"Score: {score}"
    score_surface = font_small.render(score_text, True, BLACK)
    score_rect = score_surface.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
    )
    screen.blit(score_surface, score_rect)

    # Best Score Text
    best_score_text = f"Best: {best_score}"
    best_score_surface = font_small.render(best_score_text, True, BLACK)
    best_score_rect = best_score_surface.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
    )
    screen.blit(best_score_surface, best_score_rect)

    # Restart Text
    restart_text = "Press SPACE to Play Again"
    restart_surface = font_small.render(restart_text, True, BLACK)
    restart_rect = restart_surface.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)
    )
    screen.blit(restart_surface, restart_rect)

    # Quit Text
    quit_text = "Press Q or ESC to Quit"
    quit_surface = font_small.render(quit_text, True, BLACK)
    quit_rect = quit_surface.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110)
    )
    screen.blit(quit_surface, quit_rect)


# --- Game Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Clone")
clock = pygame.time.Clock()

# Fonts
score_font = pygame.font.Font(None, 40)  # Font for score
game_over_font_large = pygame.font.Font(None, 70)  # Font for "GAME OVER"
game_over_font_small = pygame.font.Font(
    None, 40
)  # Font for scores/instructions on game over

# Game Variables
bird = Bird()
pipes = []  # List to store tuples: (bottom_rect, top_rect, color, passed_flag)
score = 0
best_score = 0
game_active = False
running = True
first_game = True  # To prevent showing "Game Over" on the very first screen

# Timers
pipe_timer = pygame.USEREVENT + 1
pygame.time.set_timer(pipe_timer, PIPE_FREQUENCY)

# Initial random elements
background_color = (173, 216, 230)  # Start with light blue
land_color = get_random_land_color()
land_rect = pygame.Rect(0, SCREEN_HEIGHT - LAND_HEIGHT, SCREEN_WIDTH, LAND_HEIGHT)


# --- Main Game Loop ---
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                if game_active:
                    bird.flap()
                else:
                    # Restart Game
                    game_active = True
                    first_game = False
                    pipes.clear()
                    bird.reset()
                    score = 0
                    # Choose new random colors for the new game
                    background_color = get_random_light_color()
                    land_color = get_random_land_color()

        # Pipe generation timer (only if game is active)
        if event.type == pipe_timer and game_active:
            bottom_pipe, top_pipe, pipe_color = create_pipe()
            pipes.append(
                (bottom_pipe, top_pipe, pipe_color, False)
            )  # Add new pipe data with passed_flag=False

    # --- Game Logic ---
    if game_active:
        # Bird movement
        bird.update()

        # Pipe movement and removal
        pipes = move_pipes(pipes)

        # Collision detection
        if check_collision(bird, pipes, land_rect):
            game_active = False
            if score > best_score:
                best_score = score

        # Score update
        for i in range(len(pipes)):
            bottom_pipe, top_pipe, color, passed = pipes[i]
            # Check if bird has passed the pipe's center AND hasn't been scored yet
            if not passed and bottom_pipe.centerx < bird.x:
                score += 1
                # Mark this pipe pair as passed
                pipes[i] = (bottom_pipe, top_pipe, color, True)
                # print(f"Score: {score}") # Debugging score

    # --- Drawing ---
    # Background
    screen.fill(background_color)

    if game_active:
        # Draw pipes
        draw_pipes(screen, pipes)

        # Draw Bird
        bird.draw(screen)

        # Draw Score
        draw_score(screen, score, score_font)

    else:  # Game Over Screen or Initial Screen
        # Draw Bird (idle) only if it's not the very first launch screen
        if not first_game:
            bird.draw(screen)  # Show the bird where it died (or reset position)
            draw_game_over(
                screen, score, best_score, game_over_font_large, game_over_font_small
            )
        else:
            # Initial instructions
            start_text = "Press SPACE to Start"
            start_surface = game_over_font_small.render(start_text, True, BLACK)
            start_rect = start_surface.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            screen.blit(start_surface, start_rect)

            quit_text = "Press Q or ESC to Quit"
            quit_surface = game_over_font_small.render(quit_text, True, BLACK)
            quit_rect = quit_surface.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            )
            screen.blit(quit_surface, quit_rect)

    # Draw Land (always visible)
    pygame.draw.rect(screen, land_color, land_rect)
    # Draw a thin black line above the land for definition
    pygame.draw.line(
        screen,
        BLACK,
        (0, SCREEN_HEIGHT - LAND_HEIGHT),
        (SCREEN_WIDTH, SCREEN_HEIGHT - LAND_HEIGHT),
        2,
    )

    # Update display
    pygame.display.flip()

    # Cap framerate
    clock.tick(60)

# --- Cleanup ---
pygame.quit()
sys.exit()
