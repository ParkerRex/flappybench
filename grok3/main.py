import pygame
import random
import platform
import asyncio

pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

land_height = 50
land_rect = pygame.Rect(0, SCREEN_HEIGHT - land_height, SCREEN_WIDTH, land_height)
font = pygame.font.SysFont(None, 36)


def generate_light_color():
    return (
        random.randint(150, 255),
        random.randint(150, 255),
        random.randint(150, 255),
    )


class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.gravity = 0.5
        self.lift = -10
        self.shape = random.choice(["square", "circle", "triangle"])
        self.color = (
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100),
        )
        self.size = 20
        self.rect = pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )

    def flap(self):
        self.velocity += self.lift

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        if self.shape == "square":
            pygame.draw.rect(screen, self.color, self.rect)
        elif self.shape == "circle":
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size // 2)
        elif self.shape == "triangle":
            points = [
                (self.x - self.size // 2, self.y + self.size // 2),
                (self.x + self.size // 2, self.y + self.size // 2),
                (self.x, self.y - self.size // 2),
            ]
            pygame.draw.polygon(screen, self.color, points)


class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap = 150
        self.gap_y = random.randint(100, 450)
        self.color = random.choice([(0, 100, 0), (205, 133, 63), (169, 169, 169)])
        self.width = 50
        self.passed = False
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y - self.gap // 2)
        self.bottom_rect = pygame.Rect(
            self.x,
            self.gap_y + self.gap // 2,
            self.width,
            SCREEN_HEIGHT - land_height - (self.gap_y + self.gap // 2),
        )

    def update(self):
        self.x -= 3
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.top_rect)
        pygame.draw.rect(screen, self.color, self.bottom_rect)

    def off_screen(self):
        return self.x < -self.width

    def check_passed(self, bird_x):
        if not self.passed and self.x < bird_x:
            self.passed = True
            return True
        return False


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird-like Game")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.background_color = (173, 216, 230)  # Light blue initially
        self.land_color = random.choice([(139, 69, 19), (255, 255, 0)])
        self.bird = Bird()
        self.pipes = [Pipe(SCREEN_WIDTH)]
        self.score = 0
        self.spawn_counter = random.randint(50, 100)
        self.game_over = False
        self.best_score = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.bird.flap()
                else:
                    if event.key == pygame.K_SPACE:
                        if self.score > self.best_score:
                            self.best_score = self.score
                        self.background_color = generate_light_color()
                        self.reset()
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        return False
        return True

    def update(self):
        if not self.game_over:
            self.bird.update()
            for pipe in self.pipes[:]:
                pipe.update()
                if pipe.check_passed(self.bird.x):
                    self.score += 1
            if (
                self.bird.rect.top <= 0
                or self.bird.rect.colliderect(land_rect)
                or any(
                    self.bird.rect.colliderect(pipe.top_rect)
                    or self.bird.rect.colliderect(pipe.bottom_rect)
                    for pipe in self.pipes
                )
            ):
                self.game_over = True
            self.pipes = [pipe for pipe in self.pipes if not pipe.off_screen()]
            self.spawn_counter -= 1
            if self.spawn_counter <= 0:
                self.pipes.append(Pipe(SCREEN_WIDTH))
                self.spawn_counter = random.randint(50, 100)

    def draw(self):
        self.screen.fill(self.background_color)
        pygame.draw.rect(self.screen, self.land_color, land_rect)
        for pipe in self.pipes:
            pipe.draw(self.screen)
        self.bird.draw(self.screen)
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))
        if self.game_over:
            game_over_text = font.render(
                f"Game Over! Best Score: {self.best_score}. Press SPACE to restart or Q to quit.",
                True,
                (0, 0, 0),
            )
            self.screen.blit(
                game_over_text,
                (
                    SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2,
                ),
            )
        pygame.display.flip()


async def main():
    game = Game()
    running = True
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        await asyncio.sleep(1.0 / FPS)
    pygame.quit()


if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
