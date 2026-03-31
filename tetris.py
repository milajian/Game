import random
import sys
from typing import Dict, List, Tuple

import pygame


SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
PLAY_WIDTH = 300
PLAY_HEIGHT = 600
BLOCK_SIZE = 30

TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT - 20

ROWS = PLAY_HEIGHT // BLOCK_SIZE
COLS = PLAY_WIDTH // BLOCK_SIZE

FPS = 60
FALL_SPEED_START = 0.5
LEVEL_UP_LINES = 10


Shape = List[List[str]]
Position = Tuple[int, int]


SHAPES: Dict[str, Shape] = {
    "S": [
        [".....", ".....", "..00.", ".00..", "....."],
        [".....", "..0..", "..00.", "...0.", "....."],
    ],
    "Z": [
        [".....", ".....", ".00..", "..00.", "....."],
        [".....", "..0..", ".00..", ".0...", "....."],
    ],
    "I": [
        ["..0..", "..0..", "..0..", "..0..", "....."],
        [".....", "0000.", ".....", ".....", "....."],
    ],
    "O": [
        [".....", ".....", ".00..", ".00..", "....."],
    ],
    "J": [
        [".....", ".0...", ".000.", ".....", "....."],
        [".....", "..00.", "..0..", "..0..", "....."],
        [".....", ".....", ".000.", "...0.", "....."],
        [".....", "..0..", "..0..", ".00..", "....."],
    ],
    "L": [
        [".....", "...0.", ".000.", ".....", "....."],
        [".....", "..0..", "..0..", "..00.", "....."],
        [".....", ".....", ".000.", ".0...", "....."],
        [".....", ".00..", "..0..", "..0..", "....."],
    ],
    "T": [
        [".....", "..0..", ".000.", ".....", "....."],
        [".....", "..0..", "..00.", "..0..", "....."],
        [".....", ".....", ".000.", "..0..", "....."],
        [".....", "..0..", ".00..", "..0..", "....."],
    ],
}

SHAPE_COLORS = {
    "S": (48, 214, 200),
    "Z": (241, 79, 80),
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "J": (60, 90, 220),
    "L": (255, 170, 0),
    "T": (168, 80, 255),
}


class Piece:
    def __init__(self, x: int, y: int, shape_key: str) -> None:
        self.x = x
        self.y = y
        self.shape_key = shape_key
        self.shape = SHAPES[shape_key]
        self.color = SHAPE_COLORS[shape_key]
        self.rotation = 0


def create_grid(locked_positions: Dict[Position, Tuple[int, int, int]]) -> List[List[Tuple[int, int, int]]]:
    grid = [[(25, 25, 35) for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLS:
            grid[y][x] = color
    return grid


def convert_shape_format(piece: Piece) -> List[Position]:
    positions: List[Position] = []
    rotation = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(rotation):
        for j, column in enumerate(line):
            if column == "0":
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    accepted_positions = {(x, y) for y in range(ROWS) for x in range(COLS) if grid[y][x] == (25, 25, 35)}
    for pos in convert_shape_format(piece):
        x, y = pos
        if y > -1 and (x, y) not in accepted_positions:
            return False
        if x < 0 or x >= COLS or y >= ROWS:
            return False
    return True


def check_lost(positions: Dict[Position, Tuple[int, int, int]]) -> bool:
    return any(y < 1 for (_, y) in positions.keys())


def get_shape() -> Piece:
    shape_key = random.choice(list(SHAPES.keys()))
    return Piece(COLS // 2, 0, shape_key)


def draw_text_center(surface: pygame.Surface, text: str, size: int, color: Tuple[int, int, int], y_offset: int = 0) -> None:
    font = pygame.font.SysFont("simhei,arial", size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, SCREEN_HEIGHT // 2 - label.get_height() // 2 + y_offset))


def clear_rows(grid: List[List[Tuple[int, int, int]]], locked: Dict[Position, Tuple[int, int, int]]) -> int:
    rows_cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if (25, 25, 35) not in grid[y]:
            rows_cleared += 1
            for x in range(COLS):
                locked.pop((x, y), None)
        elif rows_cleared > 0:
            for x in range(COLS):
                if (x, y) in locked:
                    locked[(x, y + rows_cleared)] = locked.pop((x, y))
    return rows_cleared


def draw_grid(surface: pygame.Surface, grid: List[List[Tuple[int, int, int]]]) -> None:
    for y in range(ROWS):
        pygame.draw.line(
            surface, (50, 50, 65), (TOP_LEFT_X, TOP_LEFT_Y + y * BLOCK_SIZE), (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + y * BLOCK_SIZE)
        )
    for x in range(COLS):
        pygame.draw.line(
            surface, (50, 50, 65), (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT)
        )


def draw_next_shape(piece: Piece, surface: pygame.Surface) -> None:
    font = pygame.font.SysFont("simhei,arial", 28)
    label = font.render("下一个", True, (230, 230, 230))

    start_x = TOP_LEFT_X + PLAY_WIDTH + 20
    start_y = TOP_LEFT_Y + 80

    surface.blit(label, (start_x, start_y - 40))
    fmt = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(fmt):
        for j, col in enumerate(line):
            if col == "0":
                pygame.draw.rect(surface, piece.color, (start_x + j * BLOCK_SIZE, start_y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), border_radius=4)
                pygame.draw.rect(
                    surface, (255, 255, 255), (start_x + j * BLOCK_SIZE, start_y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1, border_radius=4
                )


def draw_window(
    surface: pygame.Surface,
    grid: List[List[Tuple[int, int, int]]],
    score: int,
    level: int,
    lines: int,
) -> None:
    surface.fill((12, 14, 25))

    title_font = pygame.font.SysFont("simhei,arial", 40, bold=True)
    title = title_font.render("俄罗斯方块", True, (247, 247, 247))
    surface.blit(title, (TOP_LEFT_X + PLAY_WIDTH // 2 - title.get_width() // 2, 12))

    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(
                surface,
                grid[y][x],
                (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                border_radius=3,
            )
            if grid[y][x] != (25, 25, 35):
                pygame.draw.rect(
                    surface,
                    (255, 255, 255),
                    (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    1,
                    border_radius=3,
                )

    pygame.draw.rect(surface, (240, 240, 240), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 2)
    draw_grid(surface, grid)

    info_font = pygame.font.SysFont("simhei,arial", 24)
    score_label = info_font.render(f"得分: {score}", True, (240, 240, 240))
    level_label = info_font.render(f"等级: {level}", True, (240, 240, 240))
    lines_label = info_font.render(f"消行: {lines}", True, (240, 240, 240))
    tip_label = pygame.font.SysFont("simhei,arial", 18).render("← → 移动  ↑ 旋转  ↓ 加速", True, (180, 180, 190))

    surface.blit(score_label, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 280))
    surface.blit(level_label, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 320))
    surface.blit(lines_label, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 360))
    surface.blit(tip_label, (TOP_LEFT_X, TOP_LEFT_Y + PLAY_HEIGHT + 8))


def game_loop(window: pygame.Surface) -> None:
    locked_positions: Dict[Position, Tuple[int, int, int]] = {}
    grid = create_grid(locked_positions)

    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0.0

    score = 0
    lines = 0
    level = 1
    running = True

    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick(FPS)

        fall_speed = max(0.12, FALL_SPEED_START - (level - 1) * 0.04)
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                for pos in convert_shape_format(current_piece):
                    locked_positions[pos] = current_piece.color
                current_piece = next_piece
                next_piece = get_shape()
                grid = create_grid(locked_positions)
                cleared = clear_rows(grid, locked_positions)
                if cleared:
                    lines += cleared
                    score += [0, 100, 300, 500, 800][cleared] * level
                    level = lines // LEVEL_UP_LINES + 1
                if check_lost(locked_positions):
                    running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not valid_space(current_piece, grid):
                        current_piece.rotation -= 1
                elif event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1

        for x, y in convert_shape_format(current_piece):
            if y >= 0:
                grid[y][x] = current_piece.color

        draw_window(window, grid, score, level, lines)
        draw_next_shape(next_piece, window)
        pygame.display.update()

    window.fill((12, 14, 25))
    draw_text_center(window, "游戏结束", 52, (245, 75, 95), -20)
    draw_text_center(window, f"最终得分: {score}", 34, (240, 240, 240), 40)
    draw_text_center(window, "按任意键退出", 24, (185, 185, 195), 90)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN):
                waiting = False
        clock.tick(15)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("俄罗斯方块 - Python")
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game_loop(window)
    pygame.quit()


if __name__ == "__main__":
    main()
