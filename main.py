import pygame
import random
import sqlite3

# Initialisierung von Pygame
pygame.init()

# Fenstergröße
width, height = 450, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("City Dash")

# Farben
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)

# Schriftarten
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Spielercharakter
player_width, player_height = 30, 30
player_x = width / 2 - player_width / 2
player_y = height - player_height - 20
player_lane = 1
lane_width = 200
lane_positions = [width / 2 - lane_width, width / 2, width / 2 + lane_width]

# Unsichtbares Element erstellen
invisible_rect = pygame.Rect(100, 100, 50, 50)  # Position und Größe festlegen

# Hindernisse
obstacle_width, obstacle_height = 20, 20
obstacles = []
obstacle_speed = 7
min_obstacle_distance = 150
speed_increase_rate = 0.002

# Power-Ups
power_ups = []
power_up_size = 20
power_up_spawn_rate = 600

# Punktzahl
score = 0

# Spielzustände
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Highscore-Datenbank
conn = sqlite3.connect('highscores.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS highscores (score INTEGER)''')
conn.commit()


def get_highscore():
    c.execute("SELECT MAX(score) FROM highscores")
    result = c.fetchone()
    if result and result[0]:
        return result[0]
    return 0


def save_highscore(score):
    c.execute("INSERT INTO highscores (score) VALUES (?)", (score,))
    conn.commit()


def spawn_power_up():
    lane = random.randint(0, 2)
    x = lane_positions[lane] - power_up_size / 2
    y = -power_up_size
    power_ups.append([x, y, lane])


def draw_menu():
    screen.fill(white)
    title_text = font_large.render("City Dash", True, black)
    start_text = font_medium.render("Start Game", True, black)
    screen.blit(title_text, (width / 2 - title_text.get_width() / 2, height / 3))
    screen.blit(start_text, (width / 2 - start_text.get_width() / 2, height / 2))


def draw_game_over():
    screen.fill(white)
    game_over_text = font_large.render("Game Over", True, black)
    score_text = font_medium.render("Score: " + str(score), True, black)
    highscore_text = font_medium.render("Highscore: " + str(get_highscore()), True, black)
    restart_text = font_medium.render("Restart", True, black)
    exit_text = font_medium.render("Exit", True, black)
    screen.blit(game_over_text, (width / 2 - game_over_text.get_width() / 2, height / 4))
    screen.blit(score_text, (width / 2 - score_text.get_width() / 2, height / 3))
    screen.blit(highscore_text, (width / 2 - highscore_text.get_width() / 2, height / 2.5))
    screen.blit(restart_text, (width / 2 - restart_text.get_width() / 2, height / 2))
    screen.blit(exit_text, (width / 2 - exit_text.get_width() / 2, height * 2 / 3))


def reset_game():
    global score, obstacles, obstacle_speed
    score = 0
    obstacles = []
    obstacle_speed = 7


running = True
clock = pygame.time.Clock()


def spawn_obstacle():
    lane = random.randint(0, 2)
    x = lane_positions[lane] - obstacle_width / 2
    y = -obstacle_height

    if obstacles:
        last_obstacle = obstacles[-1]
        if y + obstacle_height + min_obstacle_distance > last_obstacle[1]:
            return

    obstacles.append([x, y, lane])


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if game_state == MENU:
                if width / 2 - 100 < mouse_pos[0] < width / 2 + 100 and height / 2 - 20 < mouse_pos[
                    1] < height / 2 + 20:
                    game_state = PLAYING
                    reset_game()
            elif game_state == GAME_OVER:
                if width / 2 - 100 < mouse_pos[0] < width / 2 + 100 and height / 2 - 20 < mouse_pos[
                    1] < height / 2 + 20:
                    game_state = PLAYING
                    reset_game()
                elif width / 2 - 100 < mouse_pos[0] < width / 2 + 100 and height * 2 / 3 - 20 < mouse_pos[
                    1] < height * 2 / 3 + 20:
                    running = False
        if event.type == pygame.KEYDOWN and game_state == PLAYING:
            if event.key == pygame.K_LEFT and player_lane > 0:
                player_lane -= 1
                player_x = lane_positions[player_lane] - player_width / 2
            if event.key == pygame.K_RIGHT and player_lane < 2:
                player_lane += 1
                player_x = lane_positions[player_lane] - player_width / 2

    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        if random.randint(0, 100) < 3:
            spawn_obstacle()
        if random.randint(0, power_up_spawn_rate) == 0:
            spawn_power_up()
        for obstacle in obstacles:
            obstacle[1] += obstacle_speed
            if obstacle[1] > height:
                obstacles.remove(obstacle)
                score += 1
                obstacle_speed *= (1 + speed_increase_rate)
        for power_up in power_ups:
            power_up[1] += obstacle_speed
            if power_up[1] > height:
                power_ups.remove(power_up)
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        for obstacle in obstacles:
            obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], obstacle_width, obstacle_height)
            if player_rect.colliderect(obstacle_rect):
                save_highscore(score)  # Speichern des Highscores beim Game Over
                game_state = GAME_OVER
        for power_up in power_ups:
            power_up_rect = pygame.Rect(power_up[0], power_up[1], power_up_size, power_up_size)
            if player_rect.colliderect(power_up_rect):
                power_ups.remove(power_up)
                score += 5
                obstacle_speed *= 1.1
        screen.fill(white)
        pygame.draw.rect(screen, black, (player_x, player_y, player_width, player_height))
        for obstacle in obstacles:
            pygame.draw.rect(screen, red, (obstacle[0], obstacle[1], obstacle_width, obstacle_height))
            for power_up in power_ups:
                pygame.draw.rect(screen, green, (power_up[0], power_up[1], power_up_size, power_up_size))
            score_text = font_medium.render("Score: " + str(score), True, black)
            screen.blit(score_text, (10, 10))
    elif game_state == GAME_OVER:
        draw_game_over()

    # Zeichne die Punktzahl immer
    score_text = font_medium.render("Score: " + str(score), True, black)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

conn.close()
pygame.quit()