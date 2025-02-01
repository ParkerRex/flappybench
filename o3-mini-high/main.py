import pygame
import random
import sys

# -------- Constants -------- #
WIDTH, HEIGHT = 400, 600
FPS = 60

GRAVITY = 0.5
FLAP_STRENGTH = -10

PIPE_SPEED = 3
PIPE_WIDTH = 70
PIPE_GAP = 150  # vertical gap between top and bottom pipe

LAND_HEIGHT = 50  # height of the land at the bottom

# Land colors: dark brown or a yellowish tone.
LAND_COLORS = [
    (101, 67, 33),   # dark brown
    (218, 165, 32)   # goldenrod (yellowish)
]

# Pipe colors: dark green, light brown, or dark gray.
PIPE_COLORS = [
    (0, 100, 0),     # dark green
    (210, 180, 140), # light brown (tan)
    (105, 105, 105)  # dark gray
]

# -------- Helper Functions -------- #
def random_light_color():
    """Return a random light color (each RGB channel high)."""
    return (random.randint(180, 255), random.randint(180, 255), random.randint(180, 255))

# -------- Classes -------- #
class Bird:
    def __init__(self):
        # Start near the left and vertically centered.
        self.x = 50
        self.y = HEIGHT // 2
        self.vel = 0
        self.size = 30
        
        # Randomly choose a shape among "square", "circle" or "triangle"
        self.shape = random.choice(["square", "circle", "triangle"])
        # Randomly choose a dark color (RGB values on the low side).
        self.color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        self.rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2,
                                self.size, self.size)
    
    def flap(self):
        """Apply an upward impulse."""
        # Every space press gives an upward boost.
        self.vel = FLAP_STRENGTH
    
    def update(self):
        self.vel += GRAVITY
        self.y += self.vel
        self.rect.center = (self.x, self.y)
    
    def draw(self, screen):
        if self.shape == "square":
            pygame.draw.rect(screen, self.color, self.rect)
        elif self.shape == "circle":
            pygame.draw.circle(screen, self.color, (self.x, int(self.y)), self.size // 2)
        elif self.shape == "triangle":
            half = self.size // 2
            points = [
                (self.x, self.y - half),           # top point
                (self.x - half, self.y + half),      # bottom left
                (self.x + half, self.y + half)       # bottom right
            ]
            pygame.draw.polygon(screen, self.color, points)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        self.gap = PIPE_GAP
        # Choose a random gap vertical position.
        # Leave a margin at the top and above the land.
        self.gap_y = random.randint(100, HEIGHT - LAND_HEIGHT - 100 - self.gap)
        # Choose a random color for this pipe pair.
        self.color = random.choice(PIPE_COLORS)
        self.passed = False  # to mark when the bird has successfully passed it
    
    def update(self):
        self.x -= PIPE_SPEED
    
    def draw(self, screen):
        # Top pipe: from the top of the screen to gap_y.
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        # Bottom pipe: from gap_y + gap to just above the land.
        bottom_rect = pygame.Rect(self.x, self.gap_y + self.gap, self.width,
                                  HEIGHT - LAND_HEIGHT - (self.gap_y + self.gap))
        pygame.draw.rect(screen, self.color, top_rect)
        pygame.draw.rect(screen, self.color, bottom_rect)
    
    def get_rects(self):
        """Return the two pygame.Rect objects for collision checking."""
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_rect = pygame.Rect(self.x, self.gap_y + self.gap, self.width,
                                  HEIGHT - LAND_HEIGHT - (self.gap_y + self.gap))
        return [top_rect, bottom_rect]

def draw_land(screen, land_color):
    """Draw the ground (land) at the bottom."""
    land_rect = pygame.Rect(0, HEIGHT - LAND_HEIGHT, WIDTH, LAND_HEIGHT)
    pygame.draw.rect(screen, land_color, land_rect)

def reset_game(first=False):
    """
    Reset the game state: new bird, pipes, score, and random colors.
    If 'first' is True, start with a light blue background.
    """
    bird = Bird()
    pipes = [Pipe(WIDTH)]
    score = 0
    background_color = (173, 216, 230) if first else random_light_color()
    land_color = random.choice(LAND_COLORS)
    # Random horizontal spacing (distance) to wait before generating a new pipe.
    pipe_gap_offset = random.randint(200, 300)
    return bird, pipes, score, background_color, land_color, pipe_gap_offset

# -------- Main Game Loop -------- #
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("o3-mini-high")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    
    best_score = 0
    # Initialize game state (first game uses light blue background)
    bird, pipes, score, background_color, land_color, pipe_gap_offset = reset_game(first=True)
    game_over = False

    while True:
        # --- Event Handling --- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # SPACE: if playing, flap; if game over, restart.
                if event.key == pygame.K_SPACE:
                    if game_over:
                        bird, pipes, score, background_color, land_color, pipe_gap_offset = reset_game()
                        game_over = False
                    else:
                        bird.flap()
                # Quit on q or Esc.
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # --- Game Updates --- #
        if not game_over:
            bird.update()
            
            # Generate a new pipe when the last one has moved far enough left.
            if pipes[-1].x < WIDTH - pipe_gap_offset:
                pipes.append(Pipe(WIDTH))
                pipe_gap_offset = random.randint(200, 300)
            
            # Update all pipes.
            for pipe in pipes:
                pipe.update()
            # Remove pipes that have moved completely off screen.
            pipes = [pipe for pipe in pipes if pipe.x + pipe.width > 0]
            
            # Check for collisions with each pipe.
            bird_rect = bird.rect
            for pipe in pipes:
                for prect in pipe.get_rects():
                    if bird_rect.colliderect(prect):
                        game_over = True
            
            # Check if the bird hits the top of the screen or the land.
            if bird.y - bird.size // 2 < 0 or bird.y + bird.size // 2 > HEIGHT - LAND_HEIGHT:
                game_over = True
            
            # Increase score when passing a pipe.
            for pipe in pipes:
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1
            
            if score > best_score:
                best_score = score
        
        # --- Drawing --- #
        screen.fill(background_color)
        for pipe in pipes:
            pipe.draw(screen)
        bird.draw(screen)
        draw_land(screen, land_color)
        
        # Overlay text on the floor: "o3-mini-high"
        floor_text = font.render("o3-mini-high", True, (255, 255, 255))  # white text
        floor_text_rect = floor_text.get_rect(center=(WIDTH // 2, HEIGHT - LAND_HEIGHT // 2))
        screen.blit(floor_text, floor_text_rect)
        
        # Draw current score (top right).
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        score_rect = score_text.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(score_text, score_rect)
        
        # If game over, display game over and best score messages.
        if game_over:
            go_text = font.render("Game Over!", True, (255, 0, 0))
            bs_text = font.render(f"Best Score: {best_score}", True, (255, 0, 0))
            restart_text = font.render("Press SPACE to Restart", True, (255, 0, 0))
            screen.blit(go_text, go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
            screen.blit(bs_text, bs_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()