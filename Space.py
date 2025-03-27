import pygame
import sys
import random
import math
from pygame import gfxdraw

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space")

COLORS = {
    "bg": (0, 0, 20),
    "player": (0, 255, 255),
    "asteroid": (255, 50, 50),
    "bonus": (50, 255, 50),
    "text": (255, 255, 255)
}


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 60
        self.speed = 5
        self.size = 20
        self.color = COLORS["player"]

    def draw(self):
        points = [
            (self.x, self.y - self.size),
            (self.x - self.size, self.y + self.size),
            (self.x + self.size, self.y + self.size)
        ]
        pygame.draw.polygon(screen, self.color, points)

    def move(self, direction):
        if direction == "left" and self.x > self.size:
            self.x -= self.speed
        if direction == "right" and self.x < WIDTH - self.size:
            self.x += self.speed


class Asteroid:
    def __init__(self):
        self.size = random.randint(15, 40)
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = -self.size
        self.speed = random.randint(2, 6)
        self.color = (
            random.randint(150, 255),
            random.randint(50, 150),
            random.randint(50, 150)
        )
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3)

    def draw(self):
        self.rotation += self.rotation_speed
        points = []
        for i in range(6):
            angle = math.radians(self.rotation + i * 60)
            radius = self.size + random.uniform(-5, 5)
            x = self.x + radius * math.cos(angle)
            y = self.y + radius * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(screen, self.color, points)

    def update(self):
        self.y += self.speed
        return self.y > HEIGHT + self.size


class Bonus:
    def __init__(self):
        self.size = 15
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = -self.size
        self.speed = 3
        self.color = COLORS["bonus"]
        self.type = random.choice(["shield", "score", "slow"])

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

    def update(self):
        self.y += self.speed
        return self.y > HEIGHT + self.size


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.lifetime = random.randint(20, 40)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        self.size *= 0.95
        return self.lifetime <= 0

    def draw(self):
        alpha = min(255, self.lifetime * 6)
        color = (*self.color[:3], alpha)
        pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), int(self.size), color)


def main_game():
    player = Player()
    asteroids = []
    bonuses = []
    particles = []
    score = 0
    level = 1
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    asteroid_spawn_timer = 0
    bonus_spawn_timer = 0
    game_over = False
    color_shift = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    return main_game()
        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move("left")
            if keys[pygame.K_RIGHT]:
                player.move("right")

            asteroid_spawn_timer += 1
            if asteroid_spawn_timer > 60 - level * 5:
                asteroids.append(Asteroid())
                asteroid_spawn_timer = 0

            bonus_spawn_timer += 1
            if bonus_spawn_timer > 180:
                bonuses.append(Bonus())
                bonus_spawn_timer = 0

            for asteroid in asteroids[:]:
                if asteroid.update():
                    asteroids.remove(asteroid)
                else:
                    distance = math.hypot(player.x - asteroid.x, player.y - asteroid.y)
                    if distance < player.size + asteroid.size:
                        game_over = True
                        for _ in range(30):
                            particles.append(Particle(asteroid.x, asteroid.y, (255, 100, 100)))

            for bonus in bonuses[:]:
                if bonus.update():
                    bonuses.remove(bonus)
                else:
                    distance = math.hypot(player.x - bonus.x, player.y - bonus.y)
                    if distance < player.size + bonus.size:
                        bonuses.remove(bonus)
                        score += 100
                        for _ in range(20):
                            particles.append(Particle(bonus.x, bonus.y, (100, 255, 100)))

            if score > level * 1000:
                level += 1

        for particle in particles[:]:
            if particle.update():
                particles.remove(particle)

        color_shift = (color_shift + 0.5) % 360
        COLORS["player"] = (
            int(127 + 127 * math.sin(math.radians(color_shift))),
            int(127 + 127 * math.sin(math.radians(color_shift + 120))),
            int(127 + 127 * math.sin(math.radians(color_shift + 240)))
        )

        screen.fill(COLORS["bg"])

        for _ in range(5):
            pygame.draw.circle(
                screen,
                (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)),
                (random.randint(0, WIDTH), random.randint(0, HEIGHT)),
                random.randint(1, 2)
            )

        for particle in particles:
            particle.draw()
        for asteroid in asteroids:
            asteroid.draw()
        for bonus in bonuses:
            bonus.draw()
        player.draw()

        score_text = font.render(f"Score: {score}", True, COLORS["text"])
        level_text = font.render(f"Level: {level}", True, COLORS["text"])
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 40))

        if game_over:
            game_over_text = font.render("GAME OVER! Press R to restart", True, (255, 50, 50))
            screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_game()
