import pygame
import random
import sqlite3
import time
from queue import Queue

pygame.init()

WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI - Snake Game")

try:
    snake_head_img = pygame.image.load("snake_head.png")
    snake_body_img = pygame.image.load("snake.png")
    food_img = pygame.image.load("food.png")
    multiplier_img = pygame.image.load("2x.png")
    slow_img = pygame.image.load("clock.png")
    penalty_img = pygame.image.load("cut.png")
    snake_head_img = pygame.transform.scale(snake_head_img, (CELL_SIZE, CELL_SIZE))
    snake_body_img = pygame.transform.scale(snake_body_img, (CELL_SIZE, CELL_SIZE))
    food_img = pygame.transform.scale(food_img, (CELL_SIZE, CELL_SIZE))
    slow_img = pygame.transform.scale(slow_img, (CELL_SIZE, CELL_SIZE))
    multiplier_img = pygame.transform.scale(multiplier_img, (CELL_SIZE, CELL_SIZE))
    penalty_img = pygame.transform.scale(penalty_img, (CELL_SIZE, CELL_SIZE))
except pygame.error:
    snake_head_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    snake_head_img.fill((0, 150, 0))  # Dark Green
    snake_body_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    snake_body_img.fill((0, 200, 0))  # Light Green
    food_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    food_img.fill((255, 0, 0))  # Red
    slow_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    slow_img.fill((0, 0, 255))  # Blue
    multiplier_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    multiplier_img.fill((255, 215, 0))  # Yellow
    penalty_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    penalty_img.fill((0, 0, 0))  # Black

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
PURPLE = (61, 12, 56)

font = pygame.font.Font(None, 36)
SCORE_HEIGHT = 40

directions = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}

# Database setup
def init_db():
    conn = sqlite3.connect("highscore.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS scores (name TEXT, highscore INTEGER)")
    conn.commit()
    conn.close()

def get_top_scores(limit=5):
    conn = sqlite3.connect("highscore.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, highscore FROM scores ORDER BY highscore DESC LIMIT ?", (limit,))
    top_scores = cursor.fetchall()
    conn.close()
    return top_scores

def add_high_score(name, score):
    conn = sqlite3.connect("highscore.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (name, highscore) VALUES (?, ?)", (name, score))
    conn.commit()
    conn.close()

def is_high_score(score, limit=5):
    if score < 5:
        return False
    top_scores = get_top_scores(limit)
    if len(top_scores) < limit:
        return True
    return score > top_scores[-1][1]

# Logical part
def generate_consumable(snake, other_consumables):
    while True:
        item = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                random.randint(SCORE_HEIGHT // CELL_SIZE, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
        consumable_positions = [c for c in other_consumables if c is not None]
        if item not in snake and item not in consumable_positions:
            return item

def find_best_move(snake, food):
    head_x, head_y = snake[0]
    food_x, food_y = food
    queue = Queue()
    queue.put(((head_x, head_y), []))
    visited = set()
    visited.add((head_x, head_y))
    while not queue.empty():
        (x, y), path = queue.get()
        for direction, (dx, dy) in directions.items():
            new_x, new_y = x + dx * CELL_SIZE, y + dy * CELL_SIZE
            if (new_x, new_y) == (food_x, food_y):
                return direction if not path else path[0]
            if (new_x, new_y) not in snake and 0 <= new_x < WIDTH and SCORE_HEIGHT <= new_y < HEIGHT and (new_x, new_y) not in visited:
                new_path = path + [direction]
                queue.put(((new_x, new_y), new_path))
                visited.add((new_x, new_y))
    for direction, (dx, dy) in directions.items():
        safe_move = (snake[0][0] + dx * CELL_SIZE, snake[0][1] + dy * CELL_SIZE)
        if safe_move not in snake and 0 <= safe_move[0] < WIDTH and SCORE_HEIGHT <= safe_move[1] < HEIGHT:
            return direction
    return "UP"

def get_player_name(score):
    input_box = pygame.Rect(WIDTH // 2 - 140, HEIGHT // 2, 280, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
        screen.fill(WHITE)
        title_text = font.render("New High Score!", True, BLACK)
        score_text = font.render(f"Your Score: {score}", True, BLACK)
        prompt_text = font.render("Enter your name:", True, BLACK)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 100))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, HEIGHT//2 - 30))
        txt_surface = font.render(text, True, BLACK)
        input_box.w = max(280, txt_surface.get_width()+10)
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()
    return text if text else "Anonymous"

def restart_screen(score):
    if is_high_score(score):
        name = get_player_name(score)
        if name: add_high_score(name, score)
    top_scores = get_top_scores()
    screen.fill(WHITE)
    score_text = font.render(f"Your Score: {score}", True, BLACK)
    leaderboard_title = font.render("Leaderboard", True, BLACK)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 100))
    screen.blit(leaderboard_title, (WIDTH // 2 - leaderboard_title.get_width() // 2, 180))
    y_offset = 220
    for i, (name, highscore) in enumerate(top_scores):
        entry_text = f"{i+1}. {name}: {highscore}"
        entry_render = font.render(entry_text, True, BLACK)
        screen.blit(entry_render, (WIDTH // 2 - entry_render.get_width() // 2, y_offset + i * 40))
    restart_text = font.render("Press R to Restart or Q to Quit", True, BLACK)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT - 100))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return True
                if event.key == pygame.K_q: return False

def pause_screen():
    paused_text = font.render("PAUSED", True, BLACK)
    resume_text = font.render("Press P to Resume", True, BLACK)
    screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False

def game_loop():
    snake = [(WIDTH // 2, HEIGHT // 2), (WIDTH // 2 - CELL_SIZE, HEIGHT // 2)]
    direction = "RIGHT"
    food = generate_consumable(snake, [])
    slow_potion, score_multiplier, penalty_item = None, None, None
    slow_timer, multiplier_timer = 0, 0
    slow_spawn, mult_spawn, penalty_spawn = None, None, None
    clock = pygame.time.Clock()
    score = 0
    auto_run = False
    cheat_input = ""  # Cheat code
    while True:
        current_speed = 10 + (score // 5)
        if slow_timer > 0:
            current_speed = max(5, current_speed // 2)  # For reducing speed
            slow_timer -= 1
        if multiplier_timer > 0:
            multiplier_timer -= 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: pause_screen()
                elif event.key == pygame.K_UP and direction != "DOWN": direction = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP": direction = "DOWN"
                elif event.key == pygame.K_LEFT and direction != "RIGHT": direction = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT": direction = "RIGHT"
                else:
                    cheat_input += event.unicode.lower()
                    if cheat_input.endswith("solly"):  # Cheat Code
                        auto_run = not auto_run
                        cheat_input = ""
        if auto_run:
            direction = find_best_move(snake, food)
        head_x, head_y = snake[0]
        move_x, move_y = directions[direction]
        new_head = (head_x + move_x * CELL_SIZE, head_y + move_y * CELL_SIZE)
        if (new_head in snake or not (0 <= new_head[0] < WIDTH) or not (SCORE_HEIGHT <= new_head[1] < HEIGHT)):
            return restart_screen(score)
        snake.insert(0, new_head)
        if new_head == food:
            score += 2 if multiplier_timer > 0 else 1
            food = generate_consumable(snake, [slow_potion, score_multiplier, penalty_item])
            if not slow_potion and random.random() < 0.15:
                slow_potion = generate_consumable(snake, [food, score_multiplier, penalty_item])
                slow_spawn = time.time()
            if not score_multiplier and random.random() < 0.1:
                score_multiplier = generate_consumable(snake, [food, slow_potion, penalty_item])
                mult_spawn = time.time()
            if not penalty_item and random.random() < 0.1:
                penalty_item = generate_consumable(snake, [food, slow_potion, score_multiplier])
                penalty_spawn = time.time()
        else:
            snake.pop()
        if slow_potion and new_head == slow_potion:
            slow_timer, slow_potion, slow_spawn = 200, None, None
        if score_multiplier and new_head == score_multiplier:
            multiplier_timer, score_multiplier, mult_spawn = 200, None, None
        if penalty_item and new_head == penalty_item:
            score = max(0, score - 2)
            penalty_spawn = time.time() + 1
            penalty_item= None
        now = time.time()
        if slow_potion and now - slow_spawn > 20:
            slow_potion, slow_spawn = None, None
        if score_multiplier and now - mult_spawn > 10:
            score_multiplier, mult_spawn = None, None

        screen.fill(WHITE)
        top_score_val = get_top_scores(1)[0][1] if get_top_scores(1) else 0
        score_text = font.render(f"Score: {score}", True, BLACK)
        top_score_text = font.render(f"High Score: {top_score_val}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(top_score_text, (WIDTH - top_score_text.get_width() - 10, 10))
        if slow_timer > 0:
            slow_text = font.render("SLOWED!", True, BLUE)
            screen.blit(slow_text, (WIDTH // 2 - slow_text.get_width() // 2, 10))
        if multiplier_timer > 0:
            mult_text = font.render("2x SCORE!", True, GOLD)
            screen.blit(mult_text, (WIDTH // 2 - mult_text.get_width() // 2, 10))
        if penalty_spawn and time.time() < penalty_spawn:
            penalty_text = font.render("-2 SCORE!", True, PURPLE)
            screen.blit(penalty_text, (WIDTH // 2 - penalty_text.get_width() // 2, 70))
        screen.blit(food_img, food)
        if slow_potion: screen.blit(slow_img, slow_potion)
        if score_multiplier: screen.blit(multiplier_img, score_multiplier)
        if penalty_item: screen.blit(penalty_img, penalty_item)
        screen.blit(snake_head_img, snake[0])
        for segment in snake[1:]:
            screen.blit(snake_body_img, segment)
        pygame.display.flip()
        clock.tick(current_speed)

if __name__ == "__main__":
    init_db()
    keep_playing = True
    while keep_playing:
        keep_playing = game_loop()
    pygame.quit()