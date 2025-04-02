import pygame
import random

# Initialize Pygame
pygame.init()

# Load bullet sound
bullet_sound = pygame.mixer.Sound("Bullet_sound.wav")
bullet_sound.set_volume(0.2)

# Load background music
pygame.mixer.music.load('Cipher2.mp3')
pygame.mixer.music.set_volume(0.8)
# Note: Music is not played until the user starts the game.

# Game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 680
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sky Bird Shooter")

# Colors
SKY_BLUE = (135, 206, 250)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LASER_BLUE = (0, 191, 255)

# Game variables
score = 0
best_score = 0
game_over = False
paused = False
game_started = False  # NEW: game has not started until user clicks "Start Game"
speed_multiplier = 1.0
speed_increase_rate = 0.001
bullet_timer = 0
bullet_interval = 60

# Load images
bird_img = pygame.image.load("bird image.png").convert_alpha()
bird_img = pygame.transform.scale(bird_img, (50, 50))

gun_img = pygame.image.load("gun image.png").convert_alpha()
gun_img = pygame.transform.scale(gun_img, (60, 60))

sky_bg = pygame.image.load("sky image.jpeg").convert()
sky_bg = pygame.transform.scale(sky_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# -------------------------------
# Player class
# -------------------------------
class Player:
    def __init__(self):
        self.image = gun_img
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5
    
    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * speed_multiplier
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed * speed_multiplier
        
        # Keep player within screen bounds
        self.rect.clamp_ip(screen.get_rect())

# -------------------------------
# Bullet class
# -------------------------------
class Bullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((5, 15))
        self.image.fill(LASER_BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.base_speed = 10
    
    def update(self):
        self.rect.y -= self.base_speed * speed_multiplier

# -------------------------------
# Bird class
# -------------------------------
class Bird:
    def __init__(self):
        self.image = bird_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - 40)
        self.rect.y = 0
        self.speed = random.uniform(1, 3) * speed_multiplier
    
    def update(self):
        self.rect.y += self.speed

    # Ensure birds do not overlap
    def is_overlapping(self, other_birds):
        for other in other_birds:
            if self.rect.colliderect(other.rect):
                return True
        return False

# -------------------------------
# NEW: Button class for Start/Restart buttons
# -------------------------------
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = pygame.font.Font(None, 45)
    
    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.hover_color, self.rect, border_radius=10)
        else:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.action()

# -------------------------------
# NEW: Game start and restart functions
# -------------------------------
def start_game():
    global game_started, game_over, paused
    game_started = True
    game_over = False
    paused = False
    pygame.mixer.music.play(-1)  # Start the background music

def restart_game():
    global game_over, score, speed_multiplier, game_started
    game_over = False
    score = 0
    speed_multiplier = 1.0
    birds.clear()
    bullets.clear()
    player.rect.centerx = SCREEN_WIDTH // 2
    pygame.mixer.music.play(-1)  # Restart the music

# -------------------------------
# Create game objects and buttons
# -------------------------------
player = Player()
bullets = []
birds = []

# Bird spawn timer
SPAWNBIRD = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWNBIRD, 600)

# NEW: Create Start and Restart buttons (feel free to adjust positions/colors)
start_button = Button(
    SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 25, 200, 60,
    "Start Game", (76, 175, 80), (69, 160, 73), start_game
)
restart_button = Button(
    SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 20, 220, 60,
    "Restart Game", (244, 67, 54), (211, 47, 47), restart_game
)

# -------------------------------
# Main Game Loop
# -------------------------------
running = True
clock = pygame.time.Clock()

while running:
    screen.blit(sky_bg, (0, 0))
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # NEW: When game has not started, let the Start button handle events.
        if not game_started:
            start_button.handle_event(event)
        # NEW: When game is over, let the Restart button handle events.
        if game_over:
            restart_button.handle_event(event)
        
        # Existing events:
        if event.type == SPAWNBIRD and game_started and not game_over and not paused:
            new_bird = Bird()
            while new_bird.is_overlapping(birds):
                new_bird = Bird()
            birds.append(new_bird)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and game_started and not game_over:
                paused = not paused
            # Also allow restart via keyboard (as before)
            if event.key == pygame.K_r and game_over:
                restart_game()
    
    keys = pygame.key.get_pressed()
    
    # Only update game objects if game has started
    if game_started:
        if not game_over and not paused:
            # Update objects
            player.update(keys)
        
            bullet_timer += clock.get_time()
            if keys[pygame.K_SPACE] and bullet_timer >= bullet_interval:
                bullets.append(Bullet(player.rect.centerx, player.rect.top))
                bullet_sound.play()
                bullet_timer = 0
            
            for bullet in bullets[:]:
                bullet.update()
                if bullet.rect.bottom < 0:
                    bullets.remove(bullet)
            
            for bird in birds[:]:
                bird.update()
                if bird.rect.y > SCREEN_HEIGHT:
                    game_over = True
                    pygame.mixer.music.stop()  # Stop music when game is over
            speed_multiplier += speed_increase_rate

        # Collision detection
        for bullet in bullets[:]:
            for bird in birds[:]:
                if bullet.rect.colliderect(bird.rect):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if bird in birds:
                        birds.remove(bird)
                    score += 10
                    if score > best_score:
                        best_score = score

        # Draw game objects
        for bullet in bullets:
            screen.blit(bullet.image, bullet.rect)
        
        for bird in birds:
            screen.blit(bird.image, bird.rect)
        
        screen.blit(player.image, player.rect)

        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        best_score_text = font.render(f"Best Score: {best_score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(best_score_text, (SCREEN_WIDTH - 200, 10))

        # Pause text
        if paused:
            pause_text = font.render("PAUSED (Press P to resume)", True, BLACK)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        
        # Game over screen with restart button
        if game_over:
            font = pygame.font.Font(None, 45)
            over_text = font.render("Game Over!", True, BLACK)
            over_rect = over_text.get_rect(center=(SCREEN_WIDTH / 4 + 200, SCREEN_HEIGHT / 2 - 40))
            screen.blit(over_text, over_rect)
            restart_button.draw(screen)
    else:
        # NEW: When game hasn't started, show the Start button.
        start_button.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()





