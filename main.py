import pygame
import random
import math

pygame.init()

WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Meteor Dodge")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont('Arial', 30, bold=True)
font_medium = pygame.font.SysFont('Arial', 20, bold=True)
font_small = pygame.font.SysFont('Arial', 14)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
GRAY = (130, 130, 130)
GOLD = (255, 215, 0)
GREEN = (50, 255, 50)
RED = (255, 60, 60)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

player_x = 200
player_y = 550
player_width = 30
player_height = 30
player_speed = 7

lives = 3
score = 0
high_score = 0
streak = 0
meteor_list = []
star_list = []
life_list = []
background_stars = []
shield = False
paused = False

game_started = False
game_over = False

spawn_timer = 0
meteor_speed = 1.5
spawn_rate = 75
invincible_timer = 0


def reset_game():
    global player_x, lives, score, streak, shield, paused
    global meteor_list, star_list, life_list, background_stars, meteor_speed, spawn_rate, spawn_timer
    global game_started, game_over, invincible_timer

    player_x = 200
    lives = 3
    score = 0
    streak = 0
    shield = False
    paused = False
    meteor_list = []
    star_list = []
    life_list = []
    background_stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)] for _ in range(40)]
    meteor_speed = 1.5
    spawn_rate = 75
    spawn_timer = 0
    invincible_timer = 0
    game_started = True
    game_over = False


def spawn_meteor():
    x = random.randint(25, WIDTH - 25)
    size = random.randint(16, 32)
    variant = random.choice([0, 1, 2])
    color = random.choice([GRAY, ORANGE, RED])
    speed = meteor_speed * random.uniform(0.95, 1.2)
    meteor_list.append([x, -size, size, False, color, speed, variant])


def spawn_star():
    x = random.randint(20, WIDTH - 20)
    star_list.append([x, -10])


def spawn_life():
    x = random.randint(30, WIDTH - 30)
    life_list.append([x, -10])


def check_collision(x1, y1, size1, x2, y2, size2):
    distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    if distance < size1 + size2:
        return True
    return False


def draw_text_center(text, font, color, x, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)


def draw_meteor(m):
    x, y, size, _, color, _, variant = m
    if variant == 0:
        pygame.draw.circle(screen, color, (int(x), int(y)), size)
        pygame.draw.circle(screen, BLACK, (int(x), int(y)), size, 2)
    else:
        points = []
        for i in range(6):
            angle = math.radians(i * 60 + (variant * 10))
            radius = size * (0.7 + 0.18 * ((i % 2) * 0.8 + 0.2))
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            points.append((px, py))
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, BLACK, points, 2)


def draw_start_screen():
    screen.fill(BLACK)
    draw_text_center("METEOR DODGE", font_big, WHITE, WIDTH // 2, 250)
    draw_text_center("Arrow keys to move", font_small, WHITE, WIDTH // 2, 300)
    draw_text_center("Press SPACE to start", font_small, YELLOW, WIDTH // 2, 330)
    draw_text_center("Press P to pause", font_small, CYAN, WIDTH // 2, 360)


def draw_hud():
    score_surface = font_small.render("Score: " + str(score), True, WHITE)
    screen.blit(score_surface, (10, 10))

    level = int((meteor_speed - 1.5) / 0.5) + 1
    level_surface = font_small.render("Level: " + str(level), True, (180, 180, 255))
    level_rect = level_surface.get_rect(topright=(WIDTH - 10, 10))
    screen.blit(level_surface, level_rect)

    streak_surface = font_small.render("Streak: " + str(streak), True, ORANGE)
    streak_rect = streak_surface.get_rect(centerx=WIDTH // 2, y=10)
    screen.blit(streak_surface, streak_rect)

    high_surface = font_small.render("Best: " + str(high_score), True, YELLOW)
    high_rect = high_surface.get_rect(centerx=WIDTH // 2, y=30)
    screen.blit(high_surface, high_rect)

    # Draw heart icons for lives
    for i in range(lives):
        heart_x = 20 + i * 24
        pygame.draw.polygon(screen, RED, [
            (heart_x + 7, 42),
            (heart_x + 2, 36),
            (heart_x, 30),
            (heart_x + 7, 22),
            (heart_x + 14, 30),
            (heart_x + 12, 36)
        ])

    shield_text = "SHIELD ON" if shield else "SHIELD OFF"
    shield_color = GREEN if shield else GRAY
    shield_surface = font_small.render(shield_text, True, shield_color)
    screen.blit(shield_surface, (10, HEIGHT - 30))

    pause_surface = font_small.render("P: Pause/Resume", True, CYAN)
    screen.blit(pause_surface, (WIDTH - 150, HEIGHT - 30))


def draw_game_over_screen():
    pygame.draw.rect(screen, BLACK, (50, 230, 300, 160))
    pygame.draw.rect(screen, RED, (50, 230, 300, 160), 3)
    draw_text_center("GAME OVER", font_big, RED, WIDTH // 2, 270)
    draw_text_center("Score: " + str(score), font_medium, WHITE, WIDTH // 2, 310)
    draw_text_center("Best: " + str(high_score), font_medium, YELLOW, WIDTH // 2, 340)
    draw_text_center("Press R to restart", font_small, CYAN, WIDTH // 2, 370)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_started:
                reset_game()
            elif event.key == pygame.K_r and game_over:
                reset_game()
            elif event.key == pygame.K_p and game_started and not game_over:
                paused = not paused

    if not game_started or game_over:
        if game_over:
            draw_game_over_screen()
        else:
            draw_start_screen()
        pygame.display.flip()
        clock.tick(60)
        continue

    if paused:
        screen.fill(BLACK)
        for star in background_stars:
            pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), star[2])
        draw_text_center("PAUSED", font_big, CYAN, WIDTH // 2, HEIGHT // 2)
        draw_hud()
        pygame.display.flip()
        clock.tick(15)
        continue

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x = player_x - player_speed
    if keys[pygame.K_RIGHT]:
        player_x = player_x + player_speed

    if player_x < player_width // 2:
        player_x = player_width // 2
    if player_x > WIDTH - player_width // 2:
        player_x = WIDTH - player_width // 2

    for star in background_stars:
        star[1] = star[1] + star[2]
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = -5
            star[2] = random.randint(1, 3)

    score = score + 1
    spawn_timer = spawn_timer + 1

    if invincible_timer > 0:
        invincible_timer = invincible_timer - 1

    if spawn_timer >= spawn_rate:
        spawn_timer = 0
        spawn_meteor()
        if random.randint(1, 6) == 1:
            spawn_star()
        if random.randint(1, 28) == 1:
            spawn_life()
        if meteor_speed < 8:
            meteor_speed = meteor_speed + 0.05
        if spawn_rate > 20:
            spawn_rate = spawn_rate - 0.15

    for m in meteor_list:
        m[1] = m[1] + m[5]

        if invincible_timer == 0 and check_collision(player_x, player_y, 12, m[0], m[1], m[2]):
            if shield:
                shield = False
                meteor_list.remove(m)
                invincible_timer = 30
                continue
            else:
                meteor_list.remove(m)
                streak = streak + 1
                score = score + 5
                invincible_timer = 60
                continue

        if m[1] > HEIGHT + m[2]:
            if not m[3]:
                lives = lives - 1
                streak = 0
                if lives <= 0:
                    game_over = True
                    if score > high_score:
                        high_score = score
            else:
                streak = streak + 1
                score = score + 10
            meteor_list.remove(m)
            continue

        if not m[3] and abs(m[0] - player_x) < 40 and m[1] > player_y - 60 and m[1] < player_y:
            m[3] = True
            score = score + 5

    for s in star_list:
        s[1] = s[1] + meteor_speed

        if check_collision(player_x, player_y, 12, s[0], s[1], 10):
            shield = True
            star_list.remove(s)
            continue

        if s[1] > HEIGHT + 10:
            star_list.remove(s)

    for l in life_list:
        l[1] = l[1] + meteor_speed

        if check_collision(player_x, player_y, 12, l[0], l[1], 10):
            if lives < 5:
                lives = lives + 1
            score = score + 15
            life_list.remove(l)
            continue

        if l[1] > HEIGHT + 10:
            life_list.remove(l)

    if score > high_score:
        high_score = score

    screen.fill(BLACK)

    for star in background_stars:
        pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), star[2])

    for m in meteor_list:
        draw_meteor(m)

    for s in star_list:
        pygame.draw.circle(screen, GOLD, (int(s[0]), int(s[1])), 10)

    for l in life_list:
        pygame.draw.circle(screen, CYAN, (int(l[0]), int(l[1])), 8)
        pygame.draw.polygon(screen, WHITE, [
            (l[0] - 4, l[1] - 2),
            (l[0] + 2, l[1] - 2),
            (l[0] + 2, l[1] + 4),
            (l[0] + 6, l[1] + 4),
            (l[0] - 2, l[1] + 10),
            (l[0] - 8, l[1] + 4),
            (l[0] - 2, l[1] + 4)
        ])

    if shield:
        pygame.draw.circle(screen, GREEN, (int(player_x), int(player_y)), 22)

    draw_ship = True
    if invincible_timer > 0 and invincible_timer % 6 < 3:
        draw_ship = False

    if draw_ship:
        nose = (player_x, player_y - 18)
        left_back = (player_x - 15, player_y + 12)
        right_back = (player_x + 15, player_y + 12)
        left_wing = (player_x - 22, player_y + 16)
        right_wing = (player_x + 22, player_y + 16)

        pygame.draw.polygon(screen, CYAN, [nose, left_back, right_back])
        pygame.draw.polygon(screen, (0, 160, 200), [left_back, left_wing, (player_x - 6, player_y + 12)])
        pygame.draw.polygon(screen, (0, 160, 200), [right_back, right_wing, (player_x + 6, player_y + 12)])
        pygame.draw.circle(screen, WHITE, (int(player_x), int(player_y - 2)), 4)

        flame_height = random.randint(8, 16)
        pygame.draw.polygon(screen, ORANGE, [
            (player_x - 6, player_y + 12),
            (player_x + 6, player_y + 12),
            (player_x, player_y + 12 + flame_height)
        ])

    draw_hud()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()