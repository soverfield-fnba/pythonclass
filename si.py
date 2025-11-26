import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Load images or create placeholders
def create_ship_image():
    ship = pygame.Surface((50, 30), pygame.SRCALPHA)
    pygame.draw.polygon(ship, GREEN, [(25, 0), (0, 30), (50, 30)])
    return ship

def create_alien_image():
    alien = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.rect(alien, RED, (5, 5, 30, 30))
    pygame.draw.rect(alien, RED, (0, 15, 40, 10))
    pygame.draw.rect(alien, RED, (10, 0, 5, 10))
    pygame.draw.rect(alien, RED, (25, 0, 5, 10))
    return alien

# Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_ship_image()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 8
        self.lives = 3
        self.shoot_cooldown = 0
        self.cooldown_time = 500  # milliseconds
        self.last_shot = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        
    def update(self):
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        
        # Handle invulnerability after being hit
        if self.invulnerable:
            self.invulnerable_timer -= 1
            # Make the player blink
            if self.invulnerable_timer % 10 < 5:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)
                
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.image.set_alpha(255)
            
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.cooldown_time:
            self.last_shot = current_time
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            return True
        return False
    
    def hit(self):
        if not self.invulnerable:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_timer = 120  # 2 seconds at 60 FPS
            return True
        return False

# Enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, row):
        super().__init__()
        self.image = create_alien_image()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2
        self.direction = 1  # 1 for right, -1 for left
        self.row = row  # Store row for difficulty scaling
        
    def update(self):
        self.rect.x += self.speed * self.direction

# Bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# Enemy Bullet
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 5
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create enemies
def create_enemies(level=1):
    speed_multiplier = 1 + (level * 0.1)  # Increase speed with level
    for row in range(5):
        for column in range(10):
            enemy = Enemy(column * 70 + 50, row * 50 + 50, row)
            enemy.speed *= speed_multiplier
            all_sprites.add(enemy)
            enemies.add(enemy)

create_enemies()

# Game variables
score = 0
level = 1
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)
game_over = False
game_won = False
last_enemy_shot = pygame.time.get_ticks()
enemy_shoot_delay = 1000  # Start with 1 second between possible enemy shots
difficulty_timer = pygame.time.get_ticks()
difficulty_increase_rate = 30000  # Increase difficulty every 30 seconds

# Main game loop
clock = pygame.time.Clock()
running = True

def check_alien_direction():
    """Check if any alien has hit the edge and needs to change direction"""
    change_direction = False
    for enemy in enemies:
        if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
            change_direction = True
            break
    
    if change_direction:
        for enemy in enemies:
            enemy.direction *= -1
            enemy.rect.y += 20

def alien_shoot():
    """Have a random alien shoot"""
    current_time = pygame.time.get_ticks()
    global last_enemy_shot, enemy_shoot_delay
    
    # Adjust difficulty based on remaining enemies
    if len(enemies) < 20:
        actual_delay = enemy_shoot_delay * 0.8
    elif len(enemies) < 10:
        actual_delay = enemy_shoot_delay * 0.6
    else:
        actual_delay = enemy_shoot_delay
    
    if current_time - last_enemy_shot > actual_delay:
        if enemies:
            shooting_alien = random.choice(list(enemies))
            enemy_bullet = EnemyBullet(shooting_alien.rect.centerx, shooting_alien.rect.bottom)
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)
            last_enemy_shot = current_time

def check_collisions():
    """Check all game collisions and handle them"""
    global score, game_over, game_won
    
    # Check for bullet-enemy collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10 * (hit.row + 1)  # More points for higher row aliens
    
    # Check for enemy-player collisions
    if pygame.sprite.spritecollide(player, enemies, False) and not player.invulnerable:
        if player.hit():
            if player.lives <= 0:
                game_over = True
    
    # Check for enemy bullet-player collisions
    if pygame.sprite.spritecollide(player, enemy_bullets, True) and not player.invulnerable:
        if player.hit():
            if player.lives <= 0:
                game_over = True
    
    # Check if all enemies are defeated
    if len(enemies) == 0:
        game_won = True
    
    # Check if enemies reached the bottom
    for enemy in enemies:
        if enemy.rect.bottom >= player.rect.top:
            game_over = True
            break

def draw_lives():
    """Draw the player's remaining lives"""
    lives_text = small_font.render(f"Lives: {player.lives}", True, WHITE)
    screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))
    
    # Draw life icons
    for i in range(player.lives):
        life_icon = create_ship_image()
        life_icon = pygame.transform.scale(life_icon, (25, 15))
        screen.blit(life_icon, (SCREEN_WIDTH - 100 + i * 30, 40))

def draw_ui():
    """Draw all UI elements"""
    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Draw level
    level_text = small_font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (10, 50))
    
    # Draw lives
    draw_lives()
    
    # Draw game over or win message
    if game_over:
        game_over_text = font.render("GAME OVER - Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))
    elif game_won:
        win_text = font.render(f"LEVEL COMPLETE! Press N for next level", True, WHITE)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2))

def reset_game():
    """Reset the game to initial state"""
    global all_sprites, enemies, bullets, enemy_bullets, player
    global score, game_over, game_won, level
    
    game_over = False
    game_won = False
    
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    
    player = Player()
    all_sprites.add(player)
    
    create_enemies(level)

def next_level():
    """Advance to the next level"""
    global level, game_won, enemy_shoot_delay
    
    level += 1
    game_won = False
    
    # Clear existing sprites
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    
    # Keep the player but reset position
    player.rect.centerx = SCREEN_WIDTH // 2
    player.rect.bottom = SCREEN_HEIGHT - 10
    all_sprites.add(player)
    
    # Create new enemies with increased difficulty
    create_enemies(level)
    
    # Decrease enemy shooting delay (makes game harder)
    enemy_shoot_delay = max(200, enemy_shoot_delay - 100)

while running:
    # Keep the game running at the right speed
    clock.tick(60)
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over and not game_won:
                player.shoot()
            if event.key == pygame.K_r and game_over:
                # Reset game
                score = 0
                level = 1
                enemy_shoot_delay = 1000
                reset_game()
            if event.key == pygame.K_n and game_won:
                # Next level
                next_level()
    
    if not game_over and not game_won:
        # Update all sprites
        all_sprites.update()
        
        # Check if enemies need to change direction
        check_alien_direction()
        
        # Enemy shooting
        alien_shoot()
        
        # Check all collisions
        check_collisions()
        
        # Increase difficulty over time
        current_time = pygame.time.get_ticks()
        if current_time - difficulty_timer > difficulty_increase_rate:
            difficulty_timer = current_time
            enemy_shoot_delay = max(200, enemy_shoot_delay - 50)  # Decrease delay, increase shooting frequency
    
    # Draw
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # Draw UI
    draw_ui()
    
    # Flip the display
    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()