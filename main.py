import pygame
import sys
import random
import json
import os

# Размеры окна
WIN_WIDTH = 400
WIN_HEIGHT = 500


# ---------------- Работа с таблицей рекордов ----------------
def load_leaderboard():
    filename = "leaderboard.json"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}


def save_leaderboard(data):
    filename = "leaderboard.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_score_to_leaderboard(grid_size, score):
    leaderboard = load_leaderboard()
    key = f"{grid_size}x{grid_size}"
    if key not in leaderboard:
        leaderboard[key] = []
    leaderboard[key].append(score)
    # Сохраняем только топ-10 результатов
    leaderboard[key] = sorted(leaderboard[key], reverse=True)[:10]
    save_leaderboard(leaderboard)


def display_leaderboard(screen, clock, grid_size):
    leaderboard = load_leaderboard()
    screen.fill((250, 248, 239))

    font = pygame.font.Font(None, 48)
    title = font.render(f'Рекорды {grid_size}x{grid_size}', True, (119, 110, 101))
    screen.blit(title, (50, 50))

    font_small = pygame.font.Font(None, 36)
    y_offset = 120

    for index, (score, date) in enumerate(leaderboard):
        text = font_small.render(f'{index + 1}. {score} - {date}', True, (119, 110, 101))
        screen.blit(text, (50, y_offset))
        y_offset += 40

    button_font = pygame.font.Font(None, 36)
    back_button = button_font.render('Назад в меню', True, (255, 255, 255), (143, 122, 102))
    back_rect = back_button.get_rect(center=(screen.get_width() // 2, y_offset + 60))
    screen.blit(back_button, back_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return 'menu'

        clock.tick(30)

# ---------------- Вспомогательная функция: цвет плитки ----------------
def get_tile_color(value):
    colors = {
        0: (205, 193, 180),
        2: (238, 228, 218),
        4: (237, 224, 200),
        8: (242, 177, 121),
        16: (245, 149, 99),
        32: (246, 124, 95),
        64: (246, 94, 59),
        128: (237, 207, 114),
        256: (237, 204, 97),
        512: (237, 200, 80),
        1024: (237, 197, 63),
        2048: (237, 194, 46)
    }
    return colors.get(value, (60, 58, 50))


# ---------------- Класс игры 2048 ----------------
class Game2048:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.board = [[0] * grid_size for _ in range(grid_size)]
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(self.grid_size)
                       for j in range(self.grid_size) if self.board[i][j] == 0]
        if not empty_cells:
            return
        i, j = random.choice(empty_cells)
        self.board[i][j] = 4 if random.random() < 0.1 else 2

    def move(self, direction):
        moved = False
        if direction in ('left', 'right'):
            for i in range(self.grid_size):
                row = self.board[i][:]
                if direction == 'right':
                    row = row[::-1]
                merged, score_gain = self.merge(row)
                if direction == 'right':
                    merged = merged[::-1]
                if merged != self.board[i]:
                    self.board[i] = merged
                    self.score += score_gain
                    moved = True
        elif direction in ('up', 'down'):
            for j in range(self.grid_size):
                col = [self.board[i][j] for i in range(self.grid_size)]
                if direction == 'down':
                    col = col[::-1]
                merged, score_gain = self.merge(col)
                if direction == 'down':
                    merged = merged[::-1]
                for i in range(self.grid_size):
                    if self.board[i][j] != merged[i]:
                        self.board[i][j] = merged[i]
                        moved = True
                self.score += score_gain
        if moved:
            self.add_new_tile()
        return moved

    def merge(self, tiles):
        non_zero = [x for x in tiles if x != 0]
        merged = []
        skip = False
        score_gain = 0
        for i in range(len(non_zero)):
            if skip:
                skip = False
                continue
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                new_val = non_zero[i] * 2
                merged.append(new_val)
                score_gain += new_val
                skip = True
            else:
                merged.append(non_zero[i])
        merged += [0] * (len(tiles) - len(merged))
        return merged, score_gain

    def can_move(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == 0:
                    return True
                if j < self.grid_size - 1 and self.board[i][j] == self.board[i][j + 1]:
                    return True
                if i < self.grid_size - 1 and self.board[i][j] == self.board[i + 1][j]:
                    return True
        return False

    def is_win(self):
        for row in self.board:
            if 2048 in row:
                return True
        return False


# ---------------- Функция отрисовки игрового поля ----------------
def draw_game(screen, game):
    grid_size = game.grid_size
    margin = 10
    board_size = WIN_WIDTH - 2 * margin
    tile_size = board_size // grid_size
    font = pygame.font.Font(None, 40)

    # Отрисовка плиток
    for i in range(grid_size):
        for j in range(grid_size):
            value = game.board[i][j]
            rect = pygame.Rect(margin + j * tile_size,
                               margin + i * tile_size + 100,
                               tile_size - 5, tile_size - 5)
            color = get_tile_color(value)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            if value:
                text = font.render(str(value), True, (0, 0, 0))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

    # Отрисовка счета
    score_font = pygame.font.Font(None, 36)
    score_text = score_font.render("Score: " + str(game.score), True, (119, 110, 101))
    screen.blit(score_text, (margin, 10))


# ---------------- Меню выбора разметки (с мышкой) ----------------
def menu(screen, clock):
    font = pygame.font.Font(None, 36)
    options = [(4, "4 x 4"), (5, "5 x 5"), (6, "6 x 6")]
    selected = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Клавиатурное управление
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected][0]
            # Обработка мыши
            if event.type == pygame.MOUSEMOTION:
                for i, opt in enumerate(options):
                    button_rect = pygame.Rect(WIN_WIDTH // 2 - 100, 120 + i * 50, 200, 40)
                    if button_rect.collidepoint(event.pos):
                        selected = i
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for i, opt in enumerate(options):
                    button_rect = pygame.Rect(WIN_WIDTH // 2 - 100, 120 + i * 50, 200, 40)
                    if button_rect.collidepoint(pos):
                        return opt[0]
                # Кнопка "Рекорды"
                leaderboard_rect = pygame.Rect(WIN_WIDTH // 2 - 100, 120 + len(options) * 50 + 20, 200, 40)
                if leaderboard_rect.collidepoint(pos):
                    display_leaderboard(screen, clock, options[selected][0])
        # Отрисовка меню
        screen.fill((250, 248, 239))
        title = font.render("Выберите разметку поля", True, (119, 110, 101))
        screen.blit(title, (WIN_WIDTH // 2 - title.get_width() // 2, 20))
        for i, opt in enumerate(options):
            color = (255, 0, 0) if i == selected else (0, 0, 0)
            button_rect = pygame.Rect(WIN_WIDTH // 2 - 100, 120 + i * 50, 200, 40)
            pygame.draw.rect(screen, (205, 193, 180), button_rect)
            text = font.render(opt[1], True, color)
            screen.blit(text, (WIN_WIDTH // 2 - text.get_width() // 2,
                               120 + i * 50 + (40 - text.get_height()) // 2))
        # Кнопка для просмотра рекордов
        leaderboard_text = font.render("Рекорды", True, (0, 0, 0))
        leaderboard_rect = pygame.Rect(WIN_WIDTH // 2 - 100, 120 + len(options) * 50 + 20, 200, 40)
        pygame.draw.rect(screen, (205, 193, 180), leaderboard_rect)
        screen.blit(leaderboard_text, (WIN_WIDTH // 2 - leaderboard_text.get_width() // 2,
                                       120 + len(options) * 50 + 20 + (40 - leaderboard_text.get_height()) // 2))
        pygame.display.flip()
        clock.tick(30)


# ---------------- Экран паузы (во время игры) ----------------
def pause_menu(screen, clock, grid_size):
    font = pygame.font.Font(None, 36)
    options = ["Continue", "New Game", "Main Menu", "Leaderboard"]
    selected = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    result = options[selected].lower().replace(" ", "_")
                    if result == "main_menu":
                        result = "menu"
                    return result
                elif event.key == pygame.K_ESCAPE:
                    return "continue"
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for idx, option in enumerate(options):
                    option_rect = pygame.Rect(WIN_WIDTH // 2 - 100, 100 + idx * 50, 200, 40)
                    if option_rect.collidepoint(pos):
                        result = option.lower().replace(" ", "_")
                        if result == "main_menu":
                            result = "menu"
                        return result
        screen.fill((250, 248, 239))
        title = font.render("Пауза", True, (119, 110, 101))
        screen.blit(title, (WIN_WIDTH // 2 - title.get_width() // 2, 40))
        for idx, option in enumerate(options):
            color = (255, 0, 0) if idx == selected else (0, 0, 0)
            option_rect = pygame.Rect(WIN_WIDTH // 2 - 100, 100 + idx * 50, 200, 40)
            pygame.draw.rect(screen, (205, 193, 180), option_rect)
            option_text = font.render(option, True, color)
            screen.blit(option_text, (option_rect.x + (option_rect.width - option_text.get_width()) // 2,
                                      option_rect.y + (option_rect.height - option_text.get_height()) // 2))
        pygame.display.flip()
        clock.tick(30)


# ---------------- Экран окончания игры ----------------
def game_over(screen, clock, game, grid_size):
    font = pygame.font.Font(None, 48)
    sub_font = pygame.font.Font(None, 36)
    options = ["New Game", "Main Menu", "Leaderboard"]
    selected = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    result = options[selected].lower().replace(" ", "_")
                    if result == "main_menu":
                        result = "menu"
                    return result
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for idx, option in enumerate(options):
                    option_rect = pygame.Rect(WIN_WIDTH // 2 - 100, 250 + idx * 50, 200, 40)
                    if option_rect.collidepoint(pos):
                        result = option.lower().replace(" ", "_")
                        if result == "main_menu":
                            result = "menu"
                        return result
        screen.fill((250, 248, 239))
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        screen.blit(game_over_text, (WIN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
        for idx, option in enumerate(options):
            color = (255, 0, 0) if idx == selected else (0, 0, 0)
            option_rect = pygame.Rect(WIN_WIDTH // 2 - 100, 250 + idx * 50, 200, 40)
            pygame.draw.rect(screen, (205, 193, 180), option_rect)
            option_text = sub_font.render(option, True, color)
            screen.blit(option_text, (option_rect.x + (option_rect.width - option_text.get_width()) // 2,
                                      option_rect.y + (option_rect.height - option_text.get_height()) // 2))
        pygame.display.flip()
        clock.tick(30)


# ---------------- Основной игровой цикл (во время игры) ----------------
def run_game(screen, clock, grid_size):
    game = Game2048(grid_size)
    running = True
    while running:
        # Определяем кнопки "Menu" и "New Game" (в правом верхнем углу)
        menu_button_rect = pygame.Rect(WIN_WIDTH - 210, 10, 100, 40)
        new_game_button_rect = pygame.Rect(WIN_WIDTH - 105, 10, 100, 40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_score_to_leaderboard(grid_size, game.score)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move('left')
                elif event.key == pygame.K_RIGHT:
                    game.move('right')
                elif event.key == pygame.K_UP:
                    game.move('up')
                elif event.key == pygame.K_DOWN:
                    game.move('down')
                elif event.key == pygame.K_ESCAPE:
                    action = pause_menu(screen, clock, grid_size)
                    if action == "continue":
                        pass
                    elif action == "new_game":
                        return "new_game"
                    elif action == "menu":
                        return "menu"
                    elif action == "leaderboard":
                        display_leaderboard(screen, clock, grid_size)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if menu_button_rect.collidepoint(pos):
                    action = pause_menu(screen, clock, grid_size)
                    if action == "continue":
                        pass
                    elif action == "new_game":
                        return "new_game"
                    elif action == "menu":
                        return "menu"
                    elif action == "leaderboard":
                        display_leaderboard(screen, clock, grid_size)
                elif new_game_button_rect.collidepoint(pos):
                    return "new_game"
        screen.fill((187, 173, 160))
        draw_game(screen, game)
        # Отрисовка кнопок "Menu" и "New Game"
        pygame.draw.rect(screen, (205, 193, 180), menu_button_rect)
        menu_text = pygame.font.Font(None, 24).render("Menu", True, (0, 0, 0))
        screen.blit(menu_text, (menu_button_rect.x + (menu_button_rect.width - menu_text.get_width()) // 2,
                                menu_button_rect.y + (menu_button_rect.height - menu_text.get_height()) // 2))
        pygame.draw.rect(screen, (205, 193, 180), new_game_button_rect)
        new_game_text = pygame.font.Font(None, 24).render("New Game", True, (0, 0, 0))
        screen.blit(new_game_text,
                    (new_game_button_rect.x + (new_game_button_rect.width - new_game_text.get_width()) // 2,
                     new_game_button_rect.y + (new_game_button_rect.height - new_game_text.get_height()) // 2))
        pygame.display.flip()
        if not game.can_move():
            save_score_to_leaderboard(grid_size, game.score)
            action = game_over(screen, clock, game, grid_size)
            if action == "new_game":
                return "new_game"
            elif action == "menu":
                return "menu"
            elif action == "leaderboard":
                display_leaderboard(screen, clock, grid_size)
                return "menu"
        clock.tick(60)


# ---------------- Главный цикл приложения ----------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("2048")
    clock = pygame.time.Clock()
    while True:
        grid_size = menu(screen, clock)
        # Вложенный цикл: играем в выбранную разметку, пока не выберем возврат в меню
        while True:
            action = run_game(screen, clock, grid_size)
            if action == "new_game":
                continue  # запускаем новую игру с той же разметкой
            elif action == "menu":
                break  # возвращаемся в главное меню
        # После break вернёмся в цикл и снова вызовем menu()


if __name__ == '__main__':
    main()
