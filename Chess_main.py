import pygame
from Standard_Pieces import *
from Controllers import *
from copy import *

pygame.init()
pieces = {}

class Illegal_Place_For_Created_Piece(Exception):
    def __init__(self, x, y):
        self.msg = "Illegal piece created at " + str(x) + " " + str(y)

class Board:
    
    def __init__(self, screen, cols, rows, square_sprite_group):
        """
        Initialize a board

        args:
            screen (screen): screen for the board
            cols, rows (int, int): number of columns and rows for the board
            sprintgroup (group): group for all the squares
        """
        self.moves = [] # This stores the move in the form ((Piece, col, row), (Captured Piece (or None), new col, new row))
        self.screen = screen
        self.state = [[None for i in range(rows)] for j in range(cols)]  # None for no piece, a piece object if there is
        self.squares = [[None for i in range(rows)] for j in range(cols)]  # [x or column], [y or row] #0 is the highest row

        size = max(cols, rows)

        if screen.get_width() == screen.get_height():
            startx, starty = 0, 0 # This is the starting position for the first square
            square_size = screen.get_width()/size # This makes the square size fit the screen size
        elif screen.get_width() > screen.get_height(): # This looks kind of broken
            startx, starty = (screen.get_width()-screen.get_height())/2, 0
            square_size = screen.get_height()/size
        elif screen.get_width() < screen.get_height(): # This looks kind of broken
            startx, starty = (screen.get_height()-screen.get_width())/2, 0  # This is the starting x and y position for the first square
            square_size = screen.get_width()/size
        
        for i in range(cols):
            for j in range(rows): #screen.get_width()
                x = square((startx + i*square_size, starty + j*square_size),
                           square_size,
                           screen,
                           (DARKTAN if ((i+j)%2 == 1) else TAN),
                           square_sprite_group)
                self.squares[i][j] = x #DrawSqures
        #Setup Board

    def __str__(self): # Todo: Redo with better iteration
        """
        returns:
            A string designed to be printed in the shell for debugging purposes.
                Do NOT use in actual code!"""
        total_string = (7*len(self.state))*'-'+"---\n"
        for row in range(len(self.state[0])):
            for col in range(len(self.state)):
                if self.state[col][row]:
                    total_string += ' | ' + str(self.state[col][row])[0:3]+str(self.state[col][row].team)
                else:
                    total_string += ' | ' + "    "
            total_string += ' | \n---'+(7*len(self.state))*'-'+'\n'
        return total_string + '\n\n\n\n\n'
                    

    def convert_board_state_to_teams(self, num): # Redocument
        """
        Converts this board's state into the just the teams (0 for no piece)
        args:
            num (int): The number of rotations to rotate the board before getting the teams
        returns:
            2D array of ints"""
        return [[(0 if (not pc) else pc.team) for pc in col] for col in self.rotate_board(num)]

    def render_board(self):
        """
        This method redraws the board with all
            the piece sprites at their current locations
        """
        for sqrs, col in zip(self.state, self.squares): # Todo: Redo with better iteration
            for piece, sqr in zip(sqrs, col):
                if piece:
                    sqr.render_piece(piece, piece_sprites)

    def unhighlight_all_squares(self):
        """
        Unhighlights all the squares"""
        for col in self.squares: # Redo with better iteration
            for sqr in col:
                sqr.unhighlight()

    def board_iterator(self, board, coords = True):
        """
        Takes a 2D array and iterates over it starting at (0, 0), then going to (0, 1), etc.
        args:
            board (2d array): Board to be iterated over
            coords (bool): Setting for result; when set to True the coordinates will be attached to each item
        return:
            (col, row, item) if coords otherwise just the items"""
        if coords:
            for col_pos, column in enumerate(board): # Redo with better iteration
                for row_pos, item in enumerate(column):
                    yield (col_pos, row_pos, item)
        else:
            for column in board: # Redo with better iteration
                for item in column:
                    yield item

    def get_piece(self, col, row): # Todo: use
        """
        args:
            col (int): Column to be checked
            row (int): Row to be checked
        return:
            Piece at position col,row otherwise None"""
        return self.state[col][row]

    def create_piece(self, piece, col, row, team, direction, sprite_group):
        """
        Creates a Piece object at x, y with the inputed team and direction

        args:
            piece (Piece): The piece type to be created
            col (int): Column for the new piece
            row (int): Row for the new piece
            team (int): Team for the new piece
            direction ("N", "S", "E", "W"): Direction the piece is facing
            sprite_group (Group): Spritegroup to be added to"""

        #assert self.get_piece(col, row), "Illegal Place For Created Piece"
        self.state[col][row] = piece(self.screen, team, direction)
        self.squares[col][row].render_piece(self.state[col][row], sprite_group)
        self.render_board()

    def get_deep_copy(self):
        """
        Creates a deep copy of this board's state
        returns:
            A deep copy of this board's state"""
        return [[x for x in col] for col in self.state]

    def rotate_board(self, num): # It does this by reflecting over x = y and  y = k # Todo: Implement or refactor
        """
        Rotates the board's state
        args:
            num (int): Number of 90 degree rotations counter-clockwise
        returns:
            The rotated board""" # Todo: Rework to use less memory
        #new_new_board = Use self.make_new_board(len(self.state), len(self.state[0])) # Todo: Rework to be correct. Doesn't change when num changes
        new_new_board = self.get_deep_copy()
        for i in range(num): # Keeo following list comprehension
            new_board = [[None for row in new_new_board] for col in new_new_board[0]] # Changes dimensions if necessary
            for col_num, column in enumerate(new_new_board): # Swap over x = y
                for row_num, row in enumerate(column):
                    new_board[row_num][col_num] = row # row_num and col_num are swapped from the normal order
            height = len(new_board[0])-1
            new_new_board = [[None for row in col] for col in new_board]
            for col_num, column in enumerate(new_board): # Swap over y = middle
                for row_num, row in enumerate(column):
                    new_new_board[col_num][height-row_num] = row
        return new_new_board

    def rotate_coordinates(self, pos, num):
        """
        Rotates pos num counter-clockwise rotations around the center of the board
        args:
            pos (tuple of ints): The coordinates to be rotated
            num (int): The number of rotations counter-clockwise to rotate them
        returns:
            The rotated coordinates"""
        for rotations_done in range(num):
            if rotations_done%2 == 1:
                pos = (pos[1], len(self.state[0])-pos[0]-1)
            else:
                pos = (pos[1], len(self.state)-pos[0]-1)
        return pos

    def make_new_board(self, width, height): # Todo Use
        """
        Creates an empty board with width width and height height
        args:
            width (int): Width of the new board
            height (int): Height of the new board

        returns:
            2D array containing Nones with the inputed width and height"""
        return [[None for row in range(height)] for col in range(width)]

    def board_change_positions(self, newstate): # Todo: document
        '''Returns the positions of changes from self.state to newstate'''
        return tuple([old_pc_data for old_pc_data, new_pc_data in zip(self.board_iterator(self.state), self.board_iterator(newstate)) if not (old_pc_data[2] is new_pc_data[2])])

    def move_piece(self, col, row, newcol, newrow): # Todo: Fix
        """
        Moves the piece at col, row to newcol, newrow
        args:
            col, row (ints): Original column and row of the piece
            newcol, newrow (ints): New column and row for the piece

        returns:
            1 if the move is legal and was made, 0 otherwise"""
        selected_piece = self.get_piece(col, row)
        initial_pos = self.rotate_coordinates((col, row), selected_piece.get_rotations()) # Rotates piece coordinates before checking if it's legal
        new_pos = self.rotate_coordinates((newcol, newrow), selected_piece.get_rotations()) # Change to newcol, newrow if possible Check before changing since I believe it ruins turn storing
        if new_pos in selected_piece.get_legal_moves(self.rotate_board(selected_piece.get_rotations()), initial_pos[0], initial_pos[1]):
            try:
                copied_state = [[copy(pc) for pc in col] for col in self.state] # Use deepcopy ??? Todo
                oldstate = [[pc for pc in col] for col in self.state] # Can't use deepcopy
                self.state = selected_piece.make_move(self.rotate_board(selected_piece.get_rotations()), initial_pos[0], initial_pos[1], new_pos[0], new_pos[1])
                self.state = self.rotate_board(4-selected_piece.get_rotations()) # Unrotates board
                # This adds the move to the moves list
                # A move is stored as follows: ((square column, square row, former occupant), (other column, other row, other former occupant)... )
                self.moves.append(tuple(map(lambda pc_change_data: (pc_change_data[0], pc_change_data[1], copied_state[pc_change_data[0]][pc_change_data[1]]), self.board_change_positions(oldstate))))
                return (1, None)
    
            except KingCaptured as err: #(kick up to controller)
                self.state = err.state
                self.state = self.rotate_board(4-selected_piece.get_rotations()) # Unrotates board
                return (1, err)
                
            except PromotionError as err: # Todo: Change to allow promotions other than queens (kick up to controller)
                self.state = err.state
                self.create_piece(Queen, new_pos[0], new_pos[1], err.piece.team, err.piece.direction, piece_sprites) # Todo: Change Sprite_group to class sprite_group don't hardcode
                self.state = self.rotate_board(4-selected_piece.get_rotations()) # Unrotates board
                return (1, err)

        else: # This should get documented eventually
            return (0, None)

    def undo(self):
        """
        Undoes the last move
        returns:
            1 if the undo is successful and 0 otherwise"""
        if self.moves:
            move_data = self.moves.pop(-1)
            for data in move_data:
                if self.state[data[0]][data[1]]:
                    self.state[data[0]][data[1]].kill()
                self.state[data[0]][data[1]] = data[2]
            return 1
        else:
            print('No moves to undo')
            return 0

class square(pygame.sprite.Sprite):
    base_target_coordinates = (((0, 0), (0.20, 0), (0, 0.20)),
                               ((0, 1), (0, .80), (.20, 1.00)),
                               ((.80, 0), (1.00, 0), (1.00, .20)),
                               ((1.00, 1.00), (1.00, .80), (.80, 1.00)))
    # This is a tuple containg triplets of points for drawing the target highlight. It should be scaled based on self.r
    
    def __init__(self, pos, size, screen, color, sprite_group):
        """
        Creates a board square for holding chess pieces

        args:
            pos (tuple of two ints): position on the screen
            size (int): size of the square on the screen
            screen (screen): screen where the square is to be rendered
            color (tuple of three ints): RGB color value for the square
            sprite_group (group): Sprite group to add this object to"""
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.pos = pos
        self.screen = screen
        self.r = size
        self.image  = pygame.Surface((self.r,self.r))
        self.image.fill(color)
        
        self.rect = self.image.get_rect()
        self.rect.left = pos[0]
        self.rect.top = pos[1]
        # Scales the coordinates for target highlight
        self.target_coordinates = tuple(map(lambda trip: tuple(map(lambda coord: (coord[0]*self.r, coord[1]*self.r), trip)), self.base_target_coordinates))
        
        sprite_group.add(self)

    def update(self):
        pass
        #self.image.fill(tuple([x+3 for x in self.image.get_at(1, 5)]))
        #self.rect = self.rect.move((1, 1))
        #self.rect.x or pos

    def render_piece(self, piece, piece_sprites):
        """
        Draws a given piece in this square, scales it to the correct size,
            and adds it to a sprite group
        args:
            piece (Piece): Piece to be drawn
            piece_sprites (Sprite Group): Sprite Group that piece gets added to""" #TODO board should have a drawboard method
        piece.draw_piece(self.rect.left, self.rect.top, int(self.r), piece_sprites)


    def highlight(self):
        """Highlights this square by changing the background to blue-gray"""
        self.image.fill(BLUEGRAY)

    def unhighlight(self): # Todo: Implement
        """Unhighlights this square by removing highlight modifications"""
        self.image.fill(self.color) #Unhighlights duh

    def dot_highlight(self): # Todo: Implement
        """Highlights this square by putting a blue-gray dot in the center"""
        pygame.draw.circle(self.image, BLUEGRAY, (int(self.r/2), int(self.r/2)), int(self.r/14))
        #print("dot highlighted") 

    def target_highlight(self):
        """Highlights this square by putting triangles in the corners"""
        for tri in self.target_coordinates:
            pygame.draw.polygon(self.image, BLUEGRAY, tri)


BLACK = (0, 0, 0)
LIGHTGRAY = (200, 200, 200)
GRAY = (150, 150, 150)
WHITE = (255, 255, 255)
RED = (240, 0, 0)
GREEN = (0, 240, 0)
YELLOW = (245, 240, 0)
BLUE = (0, 0, 230)
TAN = (239, 217, 183)
DARKTAN = (180, 136, 102)
BLUEGRAY = (20, 30, 50)

mode = 0
while not (mode in [1, 2, 3]):
    try:
        mode = int(input("Which gamemode do you want? (1, 2 or 3) "))
    except:
        pass

###---------------Board size settings---------------###
    
board_cols = 0

if mode == 1:
    board_cols = 8
    board_rows = 8
elif mode == 2:
    board_cols = 4
    board_rows = 8
elif mode == 3:
    board_cols = 8
    board_rows = 8


###---------------End of Section---------------###

width = round(600/board_cols)*board_cols # Makes the screen size mimic the board size more closely
height = round(600/board_rows)*board_rows

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Chess")
clock = pygame.time.Clock()

background = pygame.Surface(screen.get_size())
background.fill(BLACK)
screen.blit(background, (0, 0))

closed = False
game = True
sprites = pygame.sprite.Group()
piece_sprites = pygame.sprite.Group()
GUI_sprites = pygame.sprite.Group()
curboard = Board(screen, board_cols, board_rows, sprites)

###---------------Controller settings---------------###

if mode == 1:
    game_controller = Controller(curboard, None, GUI_sprites, piece_sprites)
elif mode == 2:
    game_controller = DegenerateController(curboard, None, GUI_sprites, piece_sprites)
elif mode == 3:
    game_controller = ChasmController(curboard, None, GUI_sprites, piece_sprites)

###---------------End of Section---------------###

while not closed: # Todo: Implement or refactor
    if game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                closed = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                game_controller.click_responder(x, y)
            if event.type == pygame.KEYDOWN:
                game_controller.undo_last_move()
                
    screen.blit(background, (0, 0))
    sprites.clear(screen, background)
    piece_sprites.clear(screen, background)
    sprites.update()
    sprites.draw(screen)
    piece_sprites.update()
    piece_sprites.draw(screen)
    GUI_sprites.update()
    GUI_sprites.draw(screen)
    pygame.display.update()
    clock.tick(30)

pygame.quit()


### TODO make event loop seperate
### Check style with flake8
### Immutable Pieces Literally doesn't make sense because castling
### Separate into more files
### Tetris chess
### Create documentation for everything
### Document
### Merge Board Method
### Fix degenerate castling
### Image example code: pygame.image.load(r'C:\Users\user\Pictures\.jpg')
