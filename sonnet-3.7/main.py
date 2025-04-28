import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()
pygame.font.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
BIRD_SIZE = 30
PIPE_WIDTH = 70
PIPE_GAP = 200
PIPE_SPEED = 3
GROUND_HEIGHT = 80
FONT = pygame.font.SysFont("Arial", 30)
FONT_LARGE = pygame.font.SysFont("Arial", 50)


# Colors
def random_light_color():
    return (
        random.randint(180, 240),
        random.randint(180, 240),
        random.randint(180, 240),
    )


def random_dark_color():
    return (random.randint(20, 100), random.randint(20, 100), random.randint(20, 100))


LIGHT_BLUE = (173, 216, 230)
BACKGROUND_COLOR = LIGHT_BLUE  # Initial background
DARK_BROWN = (101, 67, 33)
YELLOW = (218, 165, 32)
DARK_GREEN = (0, 100, 0)
LIGHT_BROWN = (139, 69, 19)
DARK_GRAY = (64, 64, 64)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")
clock = pygame.time.Clock()


# Game variables
class Bird:
    def __init__(self):
        self.reset()
        self.color = random_dark_color()
        self.shape = random.choice(["square", "circle", "triangle"])

    def reset(self):
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.velocity = 0
        self.alive = True

    def flap(self):
        if self.alive:
            self.velocity = -8

    def update(self):
        if not self.alive:
            return

        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity

        # Check if bird hit the ground
        if self.y + BIRD_SIZE / 2 >= HEIGHT - GROUND_HEIGHT:
            self.y = HEIGHT - GROUND_HEIGHT - BIRD_SIZE / 2
            self.alive = False

        # Don't allow bird to go above the screen
        if self.y - BIRD_SIZE / 2 <= 0:
            self.y = BIRD_SIZE / 2
            self.velocity = 0

    def draw(self):
        if self.shape == "square":
            pygame.draw.rect(
                screen,
                self.color,
                (self.x - BIRD_SIZE / 2, self.y - BIRD_SIZE / 2, BIRD_SIZE, BIRD_SIZE),
            )
        elif self.shape == "circle":
            pygame.draw.circle(
                screen, self.color, (int(self.x), int(self.y)), BIRD_SIZE // 2
            )
        elif self.shape == "triangle":
            pygame.draw.polygon(
                screen,
                self.color,
                [
                    (self.x, self.y - BIRD_SIZE / 2),
                    (self.x - BIRD_SIZE / 2, self.y + BIRD_SIZE / 2),
                    (self.x + BIRD_SIZE / 2, self.y + BIRD_SIZE / 2),
                ],
            )

    def check_collision(self, pipes):
        if not self.alive:
            return False

        bird_rect = None
        if self.shape == "square":
            bird_rect = pygame.Rect(
                self.x - BIRD_SIZE / 2, self.y - BIRD_SIZE / 2, BIRD_SIZE, BIRD_SIZE
            )
        elif self.shape == "circle":
            # For circle, we'll use a square bounding box that's slightly smaller than the circle
            bird_rect = pygame.Rect(
                self.x - BIRD_SIZE / 2.5,
                self.y - BIRD_SIZE / 2.5,
                BIRD_SIZE / 1.25,
                BIRD_SIZE / 1.25,
            )
        elif self.shape == "triangle":
            # For triangle, also use a square bounding box that's slightly smaller
            bird_rect = pygame.Rect(
                self.x - BIRD_SIZE / 2.5,
                self.y - BIRD_SIZE / 3,
                BIRD_SIZE / 1.25,
                BIRD_SIZE / 1.5,
            )

        for pipe in pipes:
            top_pipe_rect = pygame.Rect(pipe["x"], 0, PIPE_WIDTH, pipe["height"])
            bottom_pipe_rect = pygame.Rect(
                pipe["x"],
                pipe["height"] + PIPE_GAP,
                PIPE_WIDTH,
                HEIGHT - pipe["height"] - PIPE_GAP - GROUND_HEIGHT,
            )

            if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(
                bottom_pipe_rect
            ):
                self.alive = False
                return True

        return False


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.best_score = self.best_score if hasattr(self, "best_score") else 0
        self.add_pipe()
        self.game_active = True
        self.background_color = (
            random_light_color() if random.random() > 0.5 else LIGHT_BLUE
        )
        self.ground_color = random.choice([DARK_BROWN, YELLOW])

    def add_pipe(self):
        pipe_height = random.randint(100, HEIGHT - GROUND_HEIGHT - PIPE_GAP - 100)
        pipe_color = random.choice([DARK_GREEN, LIGHT_BROWN, DARK_GRAY])
        self.pipes.append(
            {
                "x": WIDTH + PIPE_WIDTH,
                "height": pipe_height,
                "color": pipe_color,
                "passed": False,
            }
        )

    def update(self):
        if not self.game_active:
            return

        self.bird.update()

        # Update pipes and check for score
        for pipe in self.pipes:
            pipe["x"] -= PIPE_SPEED

            # Check if bird passed the pipe
            if not pipe["passed"] and pipe["x"] + PIPE_WIDTH < self.bird.x:
                pipe["passed"] = True
                self.score += 1

        # Remove pipes that are off screen
        self.pipes = [pipe for pipe in self.pipes if pipe["x"] + PIPE_WIDTH > 0]

        # Add new pipes
        if len(self.pipes) == 0 or self.pipes[-1]["x"] < WIDTH - 300:
            self.add_pipe()

        # Check for collisions
        if self.bird.check_collision(self.pipes):
            self.game_active = False
            if self.score > self.best_score:
                self.best_score = self.score

    def draw(self):
        # Draw background
        screen.fill(self.background_color)

        # Draw pipes
        for pipe in self.pipes:
            # Top pipe
            pygame.draw.rect(
                screen, pipe["color"], (pipe["x"], 0, PIPE_WIDTH, pipe["height"])
            )
            # Bottom pipe
            pygame.draw.rect(
                screen,
                pipe["color"],
                (
                    pipe["x"],
                    pipe["height"] + PIPE_GAP,
                    PIPE_WIDTH,
                    HEIGHT - pipe["height"] - PIPE_GAP - GROUND_HEIGHT,
                ),
            )

        # Draw ground
        pygame.draw.rect(
            screen, self.ground_color, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)
        )

        # Draw bird
        self.bird.draw()

        # Draw score
        score_text = FONT.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (WIDTH - score_text.get_width() - 20, 20))

        # If game is over, show best score and restart instructions
        if not self.game_active:
            game_over_text = FONT_LARGE.render("Game Over", True, BLACK)
            best_score_text = FONT.render(f"Best Score: {self.best_score}", True, BLACK)
            restart_text = FONT.render(
                "Press SPACE to restart or Q/ESC to quit", True, BLACK
            )

            screen.blit(
                game_over_text,
                (
                    WIDTH // 2 - game_over_text.get_width() // 2,
                    HEIGHT // 3 - game_over_text.get_height() // 2,
                ),
            )
            screen.blit(
                best_score_text,
                (
                    WIDTH // 2 - best_score_text.get_width() // 2,
                    HEIGHT // 2 - best_score_text.get_height() // 2,
                ),
            )
            screen.blit(
                restart_text,
                (
                    WIDTH // 2 - restart_text.get_width() // 2,
                    HEIGHT // 2 + restart_text.get_height(),
                ),
            )


# Main game loop
def main():
    game = Game()

    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.game_active:
                        game.bird.flap()
                    else:
                        game.reset()
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False

        # Update game state
        game.update()

        # Draw everything
        game.draw()

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
