import pygame
import random
import sys

# --------------------
# CONFIG
# --------------------
WIDTH, HEIGHT = 600, 820
FPS = 60

ROWS, COLS = 6, 5
TILE_SIZE = 80
TILE_MARGIN = 10
TOP_OFFSET = 80

BG = (18, 18, 19)
EMPTY = (58, 58, 60)
GREEN = (83, 141, 78)
YELLOW = (181, 159, 59)
DARK_GRAY = (120, 124, 126)
TEXT = (255, 255, 255)
RED = (200, 60, 60)

KEY_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]

# --------------------
# LOAD WORDS
# --------------------
def load_words():
    with open("valid-wordle-words.txt") as f:
        return [w.strip().upper() for w in f if len(w.strip()) == 5]

WORDS_LIST = load_words()
WORDS = set(WORDS_LIST)

# --------------------
# INIT
# --------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 48)
small_font = pygame.font.SysFont("arial", 26)
button_font = pygame.font.SysFont("arial", 30)

# --------------------
# RESET
# --------------------
def reset():
    global TARGET, grid, colors, key_colors
    global row, col, game_over, win
    global message, shake_timer

    TARGET = random.choice(WORDS_LIST)

    grid = [[""]*COLS for _ in range(ROWS)]
    colors = [[EMPTY]*COLS for _ in range(ROWS)]

    key_colors = {}

    row, col = 0, 0
    game_over = False
    win = False

    message = ""
    shake_timer = 0

reset()

# --------------------
# BUTTON
# --------------------
button_rect = pygame.Rect(WIDTH//2 - 110, HEIGHT - 90, 220, 60)

# --------------------
# DRAW TILE
# --------------------
def draw_tile(letter, color, r, c, offset_x=0):
    x = (WIDTH - (COLS*TILE_SIZE + (COLS-1)*TILE_MARGIN))//2
    x += c*(TILE_SIZE+TILE_MARGIN) + offset_x
    y = TOP_OFFSET + r*(TILE_SIZE+TILE_MARGIN)

    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, color, rect, border_radius=6)

    if letter:
        text = font.render(letter, True, TEXT)
        screen.blit(text, text.get_rect(center=rect.center))

# --------------------
# DRAW KEYBOARD
# --------------------
def draw_keyboard():
    start_y = 600
    for i, row_keys in enumerate(KEY_ROWS):
        x_offset = (WIDTH - len(row_keys)*45)//2

        for j, key in enumerate(row_keys):
            x = x_offset + j*45
            y = start_y + i*60

            color = key_colors.get(key, EMPTY)
            rect = pygame.Rect(x, y, 40, 50)

            pygame.draw.rect(screen, color, rect, border_radius=5)

            text = small_font.render(key, True, TEXT)
            screen.blit(text, text.get_rect(center=rect.center))

# --------------------
# DRAW
# --------------------
def draw():
    screen.fill(BG)

    offset = random.randint(-6, 6) if shake_timer > 0 else 0

    for r in range(ROWS):
        for c in range(COLS):
            draw_tile(grid[r][c], colors[r][c], r, c, offset if r == row else 0)

    draw_keyboard()

    if message:
        msg = small_font.render(message, True, RED)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 40))

    if game_over:
        result = "YOU WIN!" if win else f"WORD: {TARGET}"
        txt = button_font.render(result, True, TEXT)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 520))

        pygame.draw.rect(screen, (100, 100, 255), button_rect, border_radius=10)
        btn = button_font.render("Play Again", True, (255,255,255))
        screen.blit(btn, btn.get_rect(center=button_rect.center))

    pygame.display.flip()

# --------------------
# CHECK WORD
# --------------------
def check(word):
    res = [DARK_GRAY]*COLS
    temp = list(TARGET)

    for i in range(COLS):
        if word[i] == TARGET[i]:
            res[i] = GREEN
            temp[i] = None

    for i in range(COLS):
        if res[i] == GREEN:
            continue
        if word[i] in temp:
            res[i] = YELLOW
            temp[temp.index(word[i])] = None

    return res

# --------------------
# UPDATE KEYS
# --------------------
def update_keys(word, result):
    for l, c in zip(word, result):
        if l not in key_colors:
            key_colors[l] = c
        else:
            if c == GREEN or (c == YELLOW and key_colors[l] != GREEN):
                key_colors[l] = c

# --------------------
# MAIN LOOP
# --------------------
animating = False
flip_index = 0
flip_timer = 0

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    reset()

        elif not animating:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    if col == COLS:
                        word = "".join(grid[row])

                        if word not in WORDS:
                            message = random.choice([
                                "We don't know that one",
                                "That word isn't real"
                            ])
                            shake_timer = 10
                        else:
                            message = ""
                            animating = True
                            flip_index = 0
                            flip_timer = 0

                elif event.key == pygame.K_BACKSPACE:
                    if col > 0:
                        col -= 1
                        grid[row][col] = ""

                else:
                    if col < COLS and event.unicode.isalpha():
                        grid[row][col] = event.unicode.upper()
                        col += 1

    # --------------------
    # ANIMATION
    # --------------------
    if animating:
        flip_timer += 1

        if flip_timer % 6 == 0:
            color = check("".join(grid[row]))[flip_index]
            colors[row][flip_index] = color
            flip_index += 1

        if flip_index >= COLS:
            word = "".join(grid[row])
            result = check(word)
            update_keys(word, result)

            if word == TARGET:
                game_over = True
                win = True
            elif row == ROWS - 1:
                game_over = True

            row += 1
            col = 0
            animating = False

    if shake_timer > 0:
        shake_timer -= 1

    draw()

pygame.quit()
sys.exit()