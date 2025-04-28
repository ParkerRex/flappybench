import pygame, sys, random

# ─── Constants ─────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -10
PIPE_SPEED = 3
PIPE_INTERVAL = 1500  # ms

# Dark colors for bird, pipes, land
DARK_COLORS = [
    (random.randint(0, 60), random.randint(0, 60), random.randint(0, 60))
    for _ in range(10)
]
PIPE_COLORS = [(0, 100, 0), (181, 101, 29), (64, 64, 64)]
LAND_COLORS = [(101, 67, 33), (218, 165, 32)]
LIGHT_SHADE_RANGE = (180, 255)


# ─── Helpers ─────────────────────────────────────────────────────────────────
def random_light_color():
    return tuple(random.randint(*LIGHT_SHADE_RANGE) for _ in range(3))


# ─── Classes ─────────────────────────────────────────────────────────────────
class Bird:
    def __init__(self):
        self.size = 30
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.vel = 0
        self.shape = random.choice(["circle", "square", "triangle"])
        self.color = random.choice(DARK_COLORS)

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel

    def draw(self, surf):
        if self.shape == "circle":
            pygame.draw.circle(
                surf, self.color, (int(self.x), int(self.y)), self.size // 2
            )
        elif self.shape == "square":
            rect = pygame.Rect(
                self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
            )
            pygame.draw.rect(surf, self.color, rect)
        else:  # triangle
            points = [
                (self.x, self.y - self.size // 2),
                (self.x - self.size // 2, self.y + self.size // 2),
                (self.x + self.size // 2, self.y + self.size // 2),
            ]
            pygame.draw.polygon(surf, self.color, points)

    def jump(self):
        self.vel = JUMP_STRENGTH * 1.2  # accelerate more if pressed repeatedly

    @property
    def rect(self):
        return pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )


class Pipe:
    def __init__(self):
        gap = 150
        top_height = random.randint(50, HEIGHT - gap - 150)
        self.x = WIDTH
        self.top = pygame.Rect(self.x, 0, 50, top_height)
        self.bot = pygame.Rect(
            self.x, top_height + gap, 50, HEIGHT - (top_height + gap)
        )
        self.color = random.choice(PIPE_COLORS)

    def update(self):
        self.x -= PIPE_SPEED
        self.top.x = self.bot.x = self.x

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.top)
        pygame.draw.rect(surf, self.color, self.bot)


# ─── Main Game ────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    best_score = 0
    first_run = True

    def reset():
        nonlocal pipes, score, last_pipe_time, first_run
        bird = Bird()
        pipes = []
        score = 0
        last_pipe_time = pygame.time.get_ticks()
        if first_run:
            bg_color = (173, 216, 230)  # light blue
            first_run = False
        else:
            bg_color = random_light_color()
        land_color = random.choice(LAND_COLORS)
        return bird, bg_color, land_color

    bird, bg_color, land_color = reset()

    running = True
    playing = True

    while running:
        dt = clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                if e.key == pygame.K_SPACE:
                    if not playing:
                        bird, bg_color, land_color = reset()
                        playing = True
                    else:
                        bird.jump()

        if playing:
            # Spawn pipes
            now = pygame.time.get_ticks()
            if now - last_pipe_time > PIPE_INTERVAL:
                pipes.append(Pipe())
                last_pipe_time = now

            # Update
            bird.update()
            for p in pipes:
                p.update()
            # Remove off-screen
            pipes = [p for p in pipes if p.x + 50 > 0]

            # Check for pass and collide
            for p in pipes:
                if p.x + 50 < bird.x and not getattr(p, "scored", False):
                    score += 1
                    p.scored = True
                if bird.rect.colliderect(p.top) or bird.rect.colliderect(p.bot):
                    playing = False

            # Check ground or ceiling
            if bird.y - bird.size // 2 <= 0 or bird.y + bird.size // 2 >= HEIGHT - 40:
                playing = False
                best_score = max(best_score, score)

        # ─── Draw ────────────────────────────────────────────────────────────────
        screen.fill(bg_color)
        for p in pipes:
            p.draw(screen)
        pygame.draw.rect(screen, land_color, (0, HEIGHT - 40, WIDTH, 40))
        bird.draw(screen)

        # Score
        score_surf = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_surf, (WIDTH - score_surf.get_width() - 10, 10))

        if not playing:
            msg = font.render(f"Game Over! Best: {best_score}", True, (0, 0, 0))
            sub = font.render("SPACE to restart, Q/ESC to quit", True, (0, 0, 0))
            screen.blit(msg, ((WIDTH - msg.get_width()) // 2, HEIGHT // 2 - 20))
            screen.blit(sub, ((WIDTH - sub.get_width()) // 2, HEIGHT // 2 + 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
