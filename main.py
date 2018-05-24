import pygame
import random

# Const
size = w, h = 500, 500
# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
# Fps
fps = 60
# Cell status const
mine = 10
flag = 11
unopened = -1
# Main loop status
running = True

# Setup
pygame.init()
screen = pygame.display.set_mode(size)
# Clock for fps limitation
clock = pygame.time.Clock()
# Font
font = pygame.font.Font(None, 46)


class Board:
    def __init__(self, width, height, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.width = width
        self.height = height
        # Fill board with random mines
        self.board = [[unopened for i in range(width)] for j in range(height)]
        # Create full opened board
        self.original_board = [[(mine if random.randrange(4, 11) is mine else 0) for i in range(width)] for j in
                               range(height)]
        for y in range(self.height):
            for x in range(self.width):
                if self.original_board[y][x] is mine:
                    for x1, y1 in self._get_neighbours(x, y):
                        if self.original_board[y1][x1] is not mine:
                            self.original_board[y1][x1] += 1

    def _get_neighbours(self, x, y):
        w = self.width
        h = self.height
        neighbour_cords = [(x + i, y + 1) for i in range(-1, 2)] + \
                          [(x + i, y - 1) for i in range(-1, 2)] + \
                          [(x - 1, y), (x + 1, y)]
        valid_neighbour_cords = [(x, y) for x, y in neighbour_cords if (0 <= x < w) and (0 <= y < h)]
        return valid_neighbour_cords

    def _open_neighbours(self, x, y):
        neighbours = [(x1, y1) for x1, y1 in self._get_neighbours(x, y) if self.original_board[y1][x1] == 0
                      and self.board[y1][x1] is unopened]
        for x1, y1 in neighbours:
            self.board[y1][x1] = self.original_board[y1][x1]
            if self.original_board[y1][x1] == 0:
                self._open_neighbours(x1, y1)

    def render(self):
        side = self.cell_size
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] is mine:
                    # Draw mine
                    pygame.draw.rect(screen, RED,
                                     (self.left + x * side + 1, self.top + y * side + 1, side - 2, side - 2))
                elif self.board[y][x] is flag:
                    pygame.draw.rect(screen, GREEN,
                                     (self.left + x * side + 1, self.top + y * side + 1, side - 2, side - 2))
                elif self.board[y][x] is not unopened:
                    # Draw number of mines around
                    text = font.render(str(self.original_board[y][x]), 1, (255, 255, 255))
                    screen.blit(text, (x * self.cell_size + 2 + self.left, y * self.cell_size + 2 + self.top))
                pygame.draw.rect(screen, WHITE, (self.left + x * side, self.top + y * side, side, side), 1)

    # Gets position in grid by mouse cords, returns None if cords don't belong to grid
    def get_cell(self, mouse_pos):
        cords = (round((mouse_pos[0] - self.left) // self.cell_size),
                 round((mouse_pos[1] - self.top) // self.cell_size))
        if 0 <= cords[0] < self.width and 0 <= cords[1] < self.height:
            return cords
        else:
            return None

    def open_cell(self, cell_cords):
        x, y = cell_cords
        if self.board[y][x] is unopened:
            if self.original_board[y][x] == 0:
                self.board[y][x] = 0
                self._open_neighbours(x, y)
            else:
                self.board[y][x] = self.original_board[y][x]

    def put_flag(self, cell_cords):
        x, y = cell_cords
        if self.board[y][x] is unopened:
            self.board[y][x] = flag
        elif self.board[y][x] is flag:
            self.board[y][x] = unopened

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell is not None:
            self.on_click(cell)


board = Board(10, 10, 0, 0, 50)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and board.get_cell(event.pos) is not None:
            pos = board.get_cell(event.pos)
            if event.button == 1:
                board.open_cell(pos)
            elif event.button == 3:
                board.put_flag(pos)

    screen.fill(BLACK)
    board.render()
    clock.tick(fps)
    pygame.display.flip()


