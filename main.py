import pygame
import random
import os
from GUI import GUI, Button

# Const
size = screen_w, screen_h = 500, 500
# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_BLUE = (153, 217, 234)
GREY = (185, 185, 185)
GRID_GREY = (105, 105, 105)
# Complexity levels
# a, b means that amount of mines is in [a, b]
complexity_levels = {'easy': [5, 10], 'medium': [20 - 30], 'hard': [30 - 40], 'impossible': [40 - 50]}
# a, b, c means that field will be a x b with cell side of c
field_metrics = {'easy': [10, 9, 50], 'medium': [16, 15, 30], 'hard': [20, 18, 25], 'impossible': [25, 22, 20]}
# Fps
fps = 60
# Cell status const
mine = 10
flag = 11
lose_mine = 100
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


# Pre-loads
intro_image = load_image('logo.jpg')
background_image = load_image('background.bmp')
cell_image = load_image('unopened.png')
flag_image = load_image('flag.png')
mine_image = load_image('mine.png')
lose_mine_image = load_image('lose_mine.png')
number_images = [load_image('{}.png'.format(i)) for i in range(1, 9)]


# Describes player board
class Board:
    # Creates board width x height with start point in (left, top) and quadratic cells
    def __init__(self, width, height, left, top, cell_size, complexity):
        self.width = width
        self.height = height
        self.left = left
        self.top = top
        self.cell_size = cell_size
        # Rescaling images to cell size
        cell_scale = (cell_size, cell_size)
        self.cell_image = pygame.transform.scale(cell_image, cell_scale)
        self.flag_image = pygame.transform.scale(flag_image, cell_scale)
        self.mine_image = pygame.transform.scale(mine_image, cell_scale)
        self.lose_mine_image = pygame.transform.scale(lose_mine_image, cell_scale)
        self.number_images = list(map(lambda x: pygame.transform.scale(x, cell_scale), number_images))

        # Board is the board that player sees
        # Fill board with random mines. Amount of mines depends on complexity level (random number in range)
        self.board = [[unopened for i in range(width)] for j in range(height)]

        # Create full opened board(board with all mines and numbers of mines)
        self.original_board = [[0 for i in range(width)] for i in range(height)]
        self.mines_count = random.randrange(*complexity_levels[complexity])
        # Randomly placing mines
        goal = self.mines_count
        while goal > 0:
            x = random.randrange(0, width - 1)
            y = random.randrange(0, height - 1)
            if self.original_board[y][x] is not mine:
                goal -= 1
                self.original_board[y][x] = mine
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
        neighbours = [(x1, y1) for x1, y1 in self._get_neighbours(x, y) if self.board[y1][x1] is unopened]
        for x1, y1 in neighbours:
            self.board[y1][x1] = self.original_board[y1][x1]
            if self.original_board[y1][x1] == 0:
                self._open_neighbours(x1, y1)

    # Draws board and it's objects on screen
    def render(self):
        side = self.cell_size
        for y in range(self.height):
            for x in range(self.width):
                cell_pos = (self.left + x * side, self.top + y * side)
                if self.board[y][x] is mine:
                    # Draw mine image
                    screen.blit(self.mine_image, cell_pos)
                elif self.board[y][x] is flag:
                    # Draw flag image
                    screen.blit(self.flag_image, cell_pos)
                elif self.board[y][x] is unopened:
                    screen.blit(self.cell_image, cell_pos)
                elif 0 < self.board[y][x] <= 8:
                    # Draw number of mines around
                    screen.blit(self.number_images[self.original_board[y][x] - 1], cell_pos)
                elif self.board[y][x] is lose_mine:
                    # Draw lose mine image
                    screen.blit(self.lose_mine_image, cell_pos)
                pygame.draw.rect(screen, GRID_GREY, (self.left + x * side, self.top + y * side, side, side), 1)

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
            elif self.original_board[y][x] is not mine:
                self.board[y][x] = self.original_board[y][x]
            elif self.original_board[y][x] is mine:
                self.board[y][x] = lose_mine
                game.lose()

    # Puts flag on self.board
    def put_flag(self, cell_cords):
        x, y = cell_cords
        if self.board[y][x] is unopened:
            self.board[y][x] = flag
        elif self.board[y][x] is flag:
            self.board[y][x] = unopened

    # Makes board react on events
    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.get_cell(event.pos) is not None:
            pos = self.get_cell(event.pos)
            if event.button == 1:
                self.open_cell(pos)
            elif event.button == 3:
                self.put_flag(pos)


# Used to control global game processes
class Game:
    def __init__(self):
        # Definition of game variables
        # Gui
        self.gui = GUI()
        main_menu_elements = [Button((0, 125, 500, 65), 'Play', 75, BLACK, GREY, action=self.play),
                              Button((0, 190, 500, 65), 'Mines: 10-20', 75, BLACK, GREY),
                              Button((0, 255, 500, 65), 'Exit', 75, BLACK, GREY, action=lambda: 0 / 0)]
        self.gui.add_page('main', main_menu_elements)
        # Game board
        self.board = None
        # Complexity
        self.complexity = 'easy'

        # Open main menu
        self.open_menu()

        # Launch game intro
        self.intro()

    # Shows game intro (lasts 3 sec)
    def intro(self):
        alpha = 0
        d_alpha = 1
        # Smooth appearance and disappearance of image by changing its alpha
        while True:
            alpha += d_alpha
            if alpha == 200:
                d_alpha = -2
            if alpha < 0:
                break
            intro_image.set_alpha(alpha)
            screen.fill(BLACK)
            screen.blit(intro_image, (0, 0))
            pygame.display.flip()
            clock.tick(100)

    # Turns game off with printing error on screen if needed
    def shutdown(self, error_message='division by zero'):
        if error_message != 'division by zero':
            # print error message in middle of screen and wait 1 sec
            screen.fill(WHITE)
            rendered_text = font.render(error_message, 20, BLACK)
            pos = ((screen_w - rendered_text.get_width()) / 2, (screen_h - rendered_text.get_height()) / 2)
            screen.blit(rendered_text, pos)
            pygame.display.flip()
            pygame.time.wait(3000)
        pygame.quit()
        # Exit from main loop
        global running
        running = False

    # Opens main menu
    def open_menu(self):
        self.gui.open_page('main')

    # Reacts on game events
    def get_event(self, event):
        # Raise zero division error that will be caught and game will be turned off
        if event.type == pygame.QUIT:
            0 / 0
        if not self.gui.is_active():
            self.board.get_event(event)
        else:
            self.gui.get_event(event)

    # Draws game on screen
    def render(self):
        screen.fill(GREY)
        if self.gui.is_active():
            screen.blit(background_image, (0, 0))
        else:
            self.board.render()
        self.gui.render(screen)
        pygame.display.flip()

    # Creates game session
    def play(self):
        self.gui.close()
        width, height, cell_size = field_metrics[self.complexity]
        self.board = Board(width, height, 0, 50, cell_size, self.complexity)

    # Lose
    def lose(self):
        # draw board with "lose mine"
        self.render()
        # play boom sound
        pass
        # wait 2 sec and go main menu
        pygame.time.wait(2000)
        self.open_menu()


game = Game()

# Main loop
while running:
    try:
        for event in pygame.event.get():
            game.get_event(event)
        game.render()
        clock.tick(fps)
    except ZeroDivisionError as error:
        game.shutdown(str(error))
