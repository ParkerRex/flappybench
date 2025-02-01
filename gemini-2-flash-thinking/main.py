import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 600
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("gemini-2-flash-thinking")

# Colors
LIGHT_BLUE = (173, 216, 230)
DARK_BROWN = (101, 67, 33)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 100, 0)
LIGHT_BROWN = (139, 69, 19)
DARK_GRAY = (105, 105, 105)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_RED = (139, 0, 0)
DARK_BLUE = (0, 0, 139)
DARK_PURPLE = (75, 0, 130)

DARK_COLORS = [DARK_RED, DARK_BLUE, DARK_GREEN, DARK_PURPLE, DARK_GRAY, BLACK]
PIPE_COLORS = [DARK_GREEN, LIGHT_BROWN, DARK_GRAY]
LAND_COLORS = [DARK_BROWN, YELLOW]

def get_light_color():
    base_color = random.choice([LIGHT_BLUE, WHITE, (240, 240, 240), (224, 255, 255)]) # More light shades
    offset = 50
    r = min(255, base_color[0] + random.randint(-offset, offset))
    g = min(255, base_color[1] + random.randint(-offset, offset))
    b = min(255, base_color[2] + random.randint(-offset, offset))
    return (r, g, b)

def get_dark_color():
    return random.choice(DARK_COLORS)

def get_pipe_color():
    return random.choice(PIPE_COLORS)

def get_land_color():
    return random.choice(LAND_COLORS)

class Bird:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT // 2
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.shape_type = random.choice(['square', 'circle', 'triangle'])
        self.color = get_dark_color()
        self.size = 20

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        if self.y > HEIGHT - LAND_HEIGHT - self.size // 2:
            self.y = HEIGHT - LAND_HEIGHT - self.size // 2
            self.velocity = 0

    def jump(self):
        self.velocity = self.jump_strength

    def draw(self, screen):
        if self.shape_type == 'square':
            pygame.draw.rect(screen, self.color, (self.x - self.size // 2, self.y - self.size // 2, self.size, self.size))
        elif self.shape_type == 'circle':
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size // 2)
        elif self.shape_type == 'triangle':
            points = [(self.x, self.y - self.size // 2),
                      (self.x - self.size // 2, self.y + self.size // 2),
                      (self.x + self.size // 2, self.y + self.size // 2)]
            pygame.draw.polygon(screen, self.color, points)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_size = 150
        self.gap_y = random.randint(100, HEIGHT - LAND_HEIGHT - 100 - self.gap_size)
        self.width = 60
        self.color = get_pipe_color()
        self.speed = 3
        self.passed = False

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, 0, self.width, self.gap_y)) # Top pipe
        pygame.draw.rect(screen, self.color, (self.x, self.gap_y + self.gap_size, self.width, HEIGHT - (self.gap_y + self.gap_size) - LAND_HEIGHT)) # Bottom pipe

    def is_off_screen(self):
        return self.x + self.width < 0

    def check_collision(self, bird):
        bird_rect = pygame.Rect(bird.x - bird.size // 2, bird.y - bird.size // 2, bird.size, bird.size)
        top_pipe_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_pipe_rect = pygame.Rect(self.x, self.gap_y + self.gap_size, self.width, HEIGHT - (self.gap_y + self.gap_size) - LAND_HEIGHT)

        return bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)

# Land
LAND_HEIGHT = 50
land_color = get_land_color()

# Score
score = 0
best_score = 0
font = pygame.font.Font(None, 36)

# Game variables
bird = Bird()
pipes = []
pipe_spawn_interval = 150 # frames
pipe_spawn_timer = 0
game_over = False
background_color = get_light_color()

def reset_game():
    global bird, pipes, score, game_over, background_color, land_color
    bird = Bird()
    pipes = []
    score = 0
    game_over = False
    background_color = get_light_color()
    land_color = get_land_color()

def display_game_over_screen():
    screen.fill(background_color)
    pygame.draw.rect(screen, land_color, (0, HEIGHT - LAND_HEIGHT, WIDTH, LAND_HEIGHT))

    game_over_text = font.render("Game Over", True, BLACK)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(game_over_text, game_over_rect)

    score_text = font.render(f"Score: {score}", True, BLACK)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(score_text, score_rect)

    best_score_text = font.render(f"Best Score: {best_score}", True, BLACK)
    best_score_rect = best_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(best_score_text, best_score_rect)

    restart_text = font.render("Press SPACE to Restart", True, BLACK)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    screen.blit(restart_text, restart_rect)

    quit_text = font.render("Press Q or ESC to Quit", True, BLACK)
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
    screen.blit(quit_text, quit_rect)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_over:
                    reset_game()
                else:
                    bird.jump()
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                running = False

    if not game_over:
        # Background
        screen.fill(background_color)

        # Land
        pygame.draw.rect(screen, land_color, (0, HEIGHT - LAND_HEIGHT, WIDTH, LAND_HEIGHT))
        # Added text overlay on the floor
        ground_text = font.render("gemini-2-flash-thinking", True, BLACK)
        ground_rect = ground_text.get_rect(center=(WIDTH // 2, HEIGHT - LAND_HEIGHT // 2))
        screen.blit(ground_text, ground_rect)
        
        # Pipes
        pipe_spawn_timer += 1
        if pipe_spawn_timer >= pipe_spawn_interval:
            pipes.append(Pipe(WIDTH))
            pipe_spawn_timer = 0

        for pipe in list(pipes): # Iterate over a copy to allow removal
            pipe.update()
            pipe.draw(screen)

            if not pipe.passed and pipe.x + pipe.width < bird.x:
                score += 1
                pipe.passed = True

            if pipe.check_collision(bird):
                game_over = True
                best_score = max(score, best_score)

            if pipe.is_off_screen():
                pipes.remove(pipe)

        # Bird
        bird.update()
        bird.draw(screen)

        # Score display
        score_text = font.render(f"Score: {score}", True, BLACK)
        score_rect = score_text.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(score_text, score_rect)
    else:
        display_game_over_screen()

    pygame.display.flip()
    pygame.time.delay(16) # Limit frame rate to ~60 FPS

pygame.quit()