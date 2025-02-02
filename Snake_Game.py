import pygame
import random
import time
import json

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the game window
width = 800
height = 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Enhanced Snake Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Snake and food
snake_block = 20
snake_speed = 10

# Initialize clock
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont(None, 50)
score_font = pygame.font.SysFont(None, 35)

# Sound effects (ensure these files exist in the same directory)
BACKGROUND_MUSIC = 'Retro-game-arcade-short.mp3'
FOOD_SOUND = 'food_sound.wav'
BONUS_FOOD_SOUND = 'bonus_food_sound.wav'
GAME_OVER_SOUND = 'game_over_sound.wav'
POWER_UP_SOUND = 'power_up_sound.wav'

# Load sound effects
try:
    pygame.mixer.music.load(BACKGROUND_MUSIC)
    food_sound = pygame.mixer.Sound(FOOD_SOUND)
    bonus_food_sound = pygame.mixer.Sound(BONUS_FOOD_SOUND)
    game_over_sound = pygame.mixer.Sound(GAME_OVER_SOUND)
    power_up_sound = pygame.mixer.Sound(POWER_UP_SOUND)
except FileNotFoundError as e:
    print(f"Sound file not found: {e}")
    pygame.quit()
    quit()

# Power-up types
SPEED_BOOST = 0
INVINCIBILITY = 1

def our_snake(snake_block, snake_list, color=GREEN):
    for x in snake_list:
        pygame.draw.rect(window, color, [x[0], x[1], snake_block, snake_block])

def message(msg, color, y_displace=0):
    mesg = font.render(msg, True, color)
    text_rect = mesg.get_rect(center=(width / 2, height / 2 + y_displace))
    window.blit(mesg, text_rect)

def show_score(score, level):
    score_text = score_font.render(f"Score: {score} | Level: {level}", True, WHITE)
    window.blit(score_text, [10, 10])

def load_high_scores():
    try:
        with open('high_scores.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_high_scores(high_scores):
    with open('high_scores.json', 'w') as f:
        json.dump(high_scores, f)

def show_high_scores():
    high_scores = load_high_scores()
    window.fill(BLACK)
    message("High Scores", GREEN, -100)
    for i, score in enumerate(sorted(high_scores, reverse=True)[:5]):
        message(f"{i + 1}. {score}", WHITE, -50 + i * 50)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def gameLoop():
    global snake_speed
    game_over = False
    game_close = False

    x1 = width / 2
    y1 = height / 2

    x1_change = 0
    y1_change = 0

    snake_list = []
    length_of_snake = 1

    foodx = round(random.randrange(0, width - snake_block) / 20.0) * 20.0
    foody = round(random.randrange(0, height - snake_block) / 20.0) * 20.0

    bonus_foodx = round(random.randrange(0, width - snake_block) / 20.0) * 20.0
    bonus_foody = round(random.randrange(0, height - snake_block) / 20.0) * 20.0
    bonus_food_active = False
    bonus_food_timer = 0

    power_up_x = -100
    power_up_y = -100
    power_up_active = False
    power_up_timer = 0
    current_power_up = None
    power_up_duration = 0

    score = 0
    level = 1

    while not game_over:
        while game_close:
            window.fill(BLACK)
            message(f"Game Over! Score: {score}", RED)
            pygame.display.update()
            time.sleep(1)
            window.fill(BLACK)
            message("Press C to Play Again or Q to Quit", WHITE)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        high_scores = load_high_scores()
                        high_scores.append(score)
                        save_high_scores(high_scores)
                        show_high_scores()
                        return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                # Prevent reversing direction
                if event.key == pygame.K_LEFT and x1_change == 0:  # Cannot reverse from right to left
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:  # Cannot reverse from left to right
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:  # Cannot reverse from down to up
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:  # Cannot reverse from up to down
                    y1_change = snake_block
                    x1_change = 0

        # Wrap-around walls
        if x1 >= width:
            x1 = 0
        elif x1 < 0:
            x1 = width - snake_block
        if y1 >= height:
            y1 = 0
        elif y1 < 0:
            y1 = height - snake_block

        x1 += x1_change
        y1 += y1_change
        window.fill(BLACK)

        pygame.draw.rect(window, RED, [foodx, foody, snake_block, snake_block])

        if bonus_food_active:
            pygame.draw.rect(window, BLUE, [bonus_foodx, bonus_foody, snake_block, snake_block])
            bonus_food_timer -= 1
            if bonus_food_timer <= 0:
                bonus_food_active = False

        if power_up_active:
            pygame.draw.rect(window, YELLOW, [power_up_x, power_up_y, snake_block, snake_block])
            power_up_timer -= 1
            if power_up_timer <= 0:
                power_up_active = False

        snake_head = [x1, y1]
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for x in snake_list[:-1]:
            if x == snake_head and current_power_up != INVINCIBILITY:
                pygame.mixer.music.stop()
                game_over_sound.play()
                game_close = True

        snake_color = YELLOW if current_power_up == INVINCIBILITY else GREEN
        our_snake(snake_block, snake_list, snake_color)
        show_score(score, level)

        # Display power-up timer
        if current_power_up is not None:
            timer_text = score_font.render(f"Power-up: {power_up_duration // 10}s", True, ORANGE)
            window.blit(timer_text, [width - 200, 10])

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, width - snake_block) / 20.0) * 20.0
            foody = round(random.randrange(0, height - snake_block) / 20.0) * 20.0
            length_of_snake += 1
            score += 10
            food_sound.play()

            if score % 50 == 0:
                level += 1
                snake_speed += 1

            if not bonus_food_active and random.random() < 0.2:
                bonus_foodx = round(random.randrange(0, width - snake_block) / 20.0) * 20.0
                bonus_foody = round(random.randrange(0, height - snake_block) / 20.0) * 20.0
                bonus_food_active = True
                bonus_food_timer = 100

            if not power_up_active and random.random() < 0.1:
                power_up_x = round(random.randrange(0, width - snake_block) / 20.0) * 20.0
                power_up_y = round(random.randrange(0, height - snake_block) / 20.0) * 20.0
                power_up_active = True
                power_up_timer = 150

        if bonus_food_active and x1 == bonus_foodx and y1 == bonus_foody:
            bonus_food_active = False
            length_of_snake += 2
            score += 50
            bonus_food_sound.play()

        if power_up_active and x1 == power_up_x and y1 == power_up_y:
            power_up_active = False
            current_power_up = random.choice([SPEED_BOOST, INVINCIBILITY])
            power_up_duration = 200
            power_up_sound.play()
            if current_power_up == SPEED_BOOST:
                snake_speed += 5

        if current_power_up is not None:
            power_up_duration -= 1
            if power_up_duration <= 0:
                if current_power_up == SPEED_BOOST:
                    snake_speed -= 5
                current_power_up = None

        clock.tick(snake_speed)

    pygame.quit()
    quit()

def show_menu():
    menu = True
    selected = 0
    options = ['Start Game', 'High Scores', 'Quit']

    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        return True  # Start the game
                    elif selected == 1:
                        show_high_scores()
                    else:
                        return False  # Quit the game

        window.fill(BLACK)
        title = font.render('Enhanced Snake Game', True, GREEN)
        title_rect = title.get_rect(center=(width / 2, height / 4))
        window.blit(title, title_rect)

        for i, option in enumerate(options):
            color = WHITE if i == selected else GREEN
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(width / 2, height / 2 + i * 50))
            window.blit(text, text_rect)

        pygame.display.update()
        clock.tick(15)

def main():
    while True:
        start_game = show_menu()
        if start_game:
            pygame.mixer.music.play(-1)  # Start the background music
            gameLoop()
            pygame.mixer.music.stop()  # Stop the music after the game ends
        else:
            break
    pygame.quit()
    quit()

if __name__ == "__main__":
    main()