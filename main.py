import pygame
import random
import os

# Const
size = screen_w, screen_h = 500, 500
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
# Fonts
error_font = pygame.font.Font(None, 350)
font = pygame.font.Font(None, 46)


# Used to load image with error-holding
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        return image
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)


# Describes player board
class Board:
    # Creates board width x height with start point in (left, top) and quadratic cells
    def __init__(self, width, height, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.width = width
        self.height = height
        # Board is the board that player sees
        # Fill board with random mines. Amount of mines depends on complexity level (random number in range)
        self.board = [[unopened for i in range(width)] for j in range(height)]
        # Create full opened board(board with all mines and numbers of mines)
        self.original_board = [[(mine if random.randrange(4, 11) is mine else 0) for i in range(width)] for j in
                               range(height)]
        # Filling cells with numbers using wave algorithm
        for y in range(self.height):
            for x in range(self.width):
                # All cells around mine are getting increased by 1
                if self.original_board[y][x] is mine:
                    for x1, y1 in self._get_neighbours(x, y):
                        if self.original_board[y1][x1] is not mine:
                            self.original_board[y1][x1] += 1

    # Method that takes cords of cell and returns all valid neighbours of cell
    def _get_neighbours(self, x, y):
        w = self.width
        h = self.height
        neighbour_cords = [(x + i, y + 1) for i in range(-1, 2)] + \
                          [(x + i, y - 1) for i in range(-1, 2)] + \
                          [(x - 1, y), (x + 1, y)]
        valid_neighbour_cords = [(x, y) for x, y in neighbour_cords if (0 <= x < w) and (0 <= y < h)]
        return valid_neighbour_cords

    # Takes cords of cell and opens it in self.board(if value in origin board is 0 it happens recursively)
    def _open_neighbours(self, x, y):
        neighbours = [(x1, y1) for x1, y1 in self._get_neighbours(x, y) if self.original_board[y1][x1] == 0
                      and self.board[y1][x1] is unopened]
        for x1, y1 in neighbours:
            self.board[y1][x1] = self.original_board[y1][x1]
            if self.original_board[y1][x1] == 0:
                self._open_neighbours(x1, y1)

    # Draws board and it's objects on screen
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

    # Replaces value on self.board with value of self.origin_board
    def open_cell(self, cell_cords):
        x, y = cell_cords
        if self.board[y][x] is unopened:
            if self.original_board[y][x] == 0:
                self.board[y][x] = 0
                self._open_neighbours(x, y)
            else:
                self.board[y][x] = self.original_board[y][x]

    # Puts flag on self.board
    def put_flag(self, cell_cords):
        x, y = cell_cords
        if self.board[y][x] is unopened:
            self.board[y][x] = flag
        elif self.board[y][x] is flag:
            self.board[y][x] = unopened


# Used to control global game processes
class Game:
    def __init__(self):
        # Definition of game variables
        pass
        # Game intro
        self.intro()

    # Shows game intro (lasts 4 sec)
    def intro(self):
        intro_image = load_image('logo.jpg')
        alpha = 0
        d_alpha = 1
        # Smooth appearance and disappearance of image by changing its alpha
        while True:
            alpha += d_alpha
            if alpha == 200:
                pygame.time.wait(1000)
                d_alpha = -2
            if alpha < 0:
                break
            intro_image.set_alpha(alpha)
            screen.fill(BLACK)
            screen.blit(intro_image, (0, 0))
            pygame.display.flip()
            clock.tick(100)

    # Turning game off with printing error on screen if needed
    def shutdown(self, error_message=None):
        if error_message:
            # print error message in middle of screen and wait 1 sec
            screen.fill(WHITE)
            rendered_text = font.render(error_message, 20, BLACK)
            pos = ((screen_w - rendered_text.get_width()) / 2, (screen_h - rendered_text.get_height()) / 2)
            screen.blit(rendered_text, pos)
            pygame.display.flip()
            pygame.time.wait(3000)

    #def


game = Game()

'''
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
'''
