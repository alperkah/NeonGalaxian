import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Galaxian: Cyberpunk Edition")

# Colors
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Load fonts
try:
    font = pygame.font.Font("path/to/Orbitron-Regular.ttf", 18)
    title_font = pygame.font.Font("path/to/Orbitron-Bold.ttf", 36)
except:
    font = pygame.font.Font(None, 18)
    title_font = pygame.font.Font(None, 36)

# Game variables
score = 0
lives = 3
level = 1
game_active = False

# Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, MAGENTA, [(20, 0), (0, 40), (40, 40)])
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT-20))
        self.speed = 5
        self.powerup = None
        self.powerup_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.clamp_ip(screen.get_rect())

        if self.powerup:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.powerup = None

    def shoot(self):
        if self.powerup == 'rapidFire':
            return [Bullet(self.rect.centerx, self.rect.top)]
        elif self.powerup == 'wideShot':
            return [
                Bullet(self.rect.left, self.rect.top),
                Bullet(self.rect.centerx, self.rect.top),
                Bullet(self.rect.right, self.rect.top)
            ]
        elif self.powerup == 'bombAttack':
            return [Bomb(self.rect.centerx, self.rect.top)]
        else:
            return [Bullet(self.rect.centerx, self.rect.top)]

# Bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 12))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 8

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# Bomb
class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 6

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# Enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        color = pygame.Color(0)
        color.hsla = (random.randint(0, 360), 100, 50, 100)
        pygame.draw.polygon(self.image, color, [(20, 0), (0, 40), (40, 40)])
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1
        self.speed = 2

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1
            self.rect.y += 20

# Boss
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((160, 160), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, RED, [(80, 0), (0, 80), (40, 160), (120, 160), (160, 80)])
        self.rect = self.image.get_rect(center=(WIDTH//2, 100))
        self.speed = 3
        self.direction = 1
        self.health = 100 + level * 20
        self.max_health = self.health

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1

# PowerUp
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(['rapidFire', 'wideShot', 'shield', 'bombAttack'])
        self.image = pygame.Surface((20, 20))
        if self.type == 'rapidFire':
            self.image.fill(YELLOW)
        elif self.type == 'wideShot':
            self.image.fill(MAGENTA)
        elif self.type == 'shield':
            self.image.fill(CYAN)
        else:  # bombAttack
            self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Star
class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((random.randint(1, 3), random.randint(1, 3)))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.speed = random.uniform(0.5, 1.5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
            self.rect.x = random.randint(0, WIDTH)

# Sprite groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()
stars = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Create stars
for _ in range(100):
    star = Star()
    stars.add(star)
    all_sprites.add(star)

# Main game loop
clock = pygame.time.Clock()
running = True

def create_enemies():
    for i in range(4):
        for j in range(8):
            enemy = Enemy(50 + j * 80, 50 + i * 60)
            enemies.add(enemy)
            all_sprites.add(enemy)

def create_boss():
    boss = Boss()
    enemies.add(boss)
    all_sprites.add(boss)

def show_game_over():
    screen.fill(BLACK)
    game_over_text = title_font.render("GAME OVER", True, RED)
    score_text = font.render(f"SCORE: {score}", True, WHITE)
    restart_text = font.render("Press SPACE to restart", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 10))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))

def show_start_menu():
    screen.fill(BLACK)
    title_text = title_font.render("NEON GALAXIAN", True, MAGENTA)
    start_text = font.render("Press SPACE to start", True, WHITE)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 + 50))

def reset_game():
    global score, lives, level
    score = 0
    lives = 3
    level = 1
    player.rect.midbottom = (WIDTH//2, HEIGHT-20)
    player.powerup = None
    player.powerup_timer = 0
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    powerups.empty()
    all_sprites.add(player)
    all_sprites.add(stars)
    create_enemies()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_active:
                    game_active = True
                    reset_game()
                elif game_active:
                    new_bullets = player.shoot()
                    bullets.add(new_bullets)
                    all_sprites.add(new_bullets)

    if game_active:
        all_sprites.update()

        # Check for collisions
        for enemy in pygame.sprite.spritecollide(player, enemies, False):
            if player.powerup != 'shield':
                lives -= 1
                if lives <= 0:
                    game_active = False
                enemy.kill()

        for bullet in bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                if isinstance(enemy, Boss):
                    enemy.health -= 10
                    if enemy.health <= 0:
                        enemy.kill()
                        score += 2000 * level
                        level += 1
                else:
                    enemy.kill()
                    score += 10 * level
                bullet.kill()
                if random.random() < 0.2:
                    powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery)
                    powerups.add(powerup)
                    all_sprites.add(powerup)

        for powerup in pygame.sprite.spritecollide(player, powerups, True):
            player.powerup = powerup.type
            player.powerup_timer = 600  # 10 seconds at 60 FPS

        # Create new enemies or boss
        if len(enemies) == 0:
            if level % 5 == 0:
                create_boss()
            else:
                create_enemies()
            level += 1

        # Draw everything
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # Draw HUD
        score_text = font.render(f"SCORE: {score}", True, WHITE)
        lives_text = font.render(f"LIVES: {lives}", True, WHITE)
        level_text = font.render(f"LEVEL: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

        if player.powerup:
            powerup_text = font.render(f"{player.powerup.upper()} {player.powerup_timer//60}s", True, CYAN)
            screen.blit(powerup_text, (WIDTH - powerup_text.get_width() - 10, HEIGHT - 30))

        # Draw boss health bar
        boss = next((sprite for sprite in enemies if isinstance(sprite, Boss)), None)
        if boss:
            pygame.draw.rect(screen, RED, (boss.rect.x, boss.rect.y - 20, boss.rect.width, 10))
            pygame.draw.rect(screen, GREEN, (boss.rect.x, boss.rect.y - 20, boss.rect.width * boss.health // boss.max_health, 10))

    else:
        if lives <= 0:
            show_game_over()
        else:
            show_start_menu()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()