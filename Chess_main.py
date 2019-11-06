import pygame
from Standard_Pieces import *
from Controllers import *

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

        #Begin of test code#
        #king = King(1)
        #End of test code#
        size = max(cols, rows)
        
        if screen.get_width() == screen.get_height():
            startx, starty = 0, 0
            square_size = screen.get_width()/size
        elif screen.get_width() > screen.get_height():
            startx, starty = (screen.get_width()-screen.get_height())/2, 0
            square_size = screen.get_height()/size
        elif screen.get_width() < screen.get_height():
            startx, starty = (screen.get_height()-screen.get_width())/2, 0  # This is the starting x and y position for the first square
            square_size = screen.get_width()/size
        
        for i in range(cols):
            for j in range(rows): #screen.get_width()
                x = square((startx + i*square_size, starty + j*square_size), square_size, screen, (DARKTAN if ((i+j)%2 == 1) else TAN), square_sprite_group)
                self.squares[i][j] = x #DrawSqures
        #Setup Board

    def __str__(self): # Redo with better iteration
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
        Converts this board's state into the just the teams

        returns:
            2D array"""
        rotated_board = self.rotate_board(num)
        return [[(0 if (not pc) else pc.team) for pc in col] for col in rotated_board]

    def render_board(self):
        """
        This method redraws the board with all
            the piece sprites at their current locations
        """
        for sqrs, col in zip(self.state, self.squares):
            for piece, sqr in zip(sqrs, col):
                if piece:
                    sqr.render_piece(piece, piece_sprites)

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

        if self.get_piece(col, row):
            raise Illegal_Place_For_Created_Piece(col, row) # Not a real error yet
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
        """num is the number of 90 degree rotations counter-clockwise""" # Todo: Rework to use less memory
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

    def rotate_coordinates(self, pos, num): # Todo: Document
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
                self.moves.append(((col, row, self.get_piece(col, row)), (newcol, newrow, self.get_piece(newcol, newrow)))) # Todo Change this so it works
                self.state = selected_piece.make_move(self.rotate_board(selected_piece.get_rotations()), initial_pos[0], initial_pos[1], new_pos[0], new_pos[1])
                self.state = self.rotate_board(4-selected_piece.get_rotations()) # Unrotates board
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

        else:
            return (0, None)

    def undo(self):
        """Undoes the last move. Returns 1 if successful and 0 otherwise"""
        try:
            moved_piece_data, captured_piece_data = self.moves.pop(-1)
            if self.state[moved_piece_data[0]][moved_piece_data[1]]:
                self.state[moved_piece_data[0]][moved_piece_data[1]].kill()
            if self.state[captured_piece_data[0]][captured_piece_data[1]]:
                self.state[captured_piece_data[0]][captured_piece_data[1]].kill()
            self.state[moved_piece_data[0]][moved_piece_data[1]] = moved_piece_data[2]
            self.state[captured_piece_data[0]][captured_piece_data[1]] = captured_piece_data[2]
            return 1
        except IndexError:
            print('No moves to undo')
            return 0



class square(pygame.sprite.Sprite):
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
        
        sprite_group.add(self)

    def update(self):
        pass
        #self.image.fill(tuple([x+3 for x in self.image.get_at(1, 5)]))
        #self.rect = self.rect.move((1, 1))
        #self.rect.x or pos

    def render_piece(self, piece, piece_sprites):
        '''Draws a piece in this square and scales it. Also adds it to piece_sprites''' #TODO Gives Piece a draw method that takes a position and a scale, have this method call it; board should have a drawboard method
        piece.draw_piece(self.rect.left, self.rect.top, int(self.r), piece_sprites)


    def highlight(self): # Todo: Implement
        self.image.fill(BLUEGRAY)
        ###HIGHLIGHT THIS SQUARE###
        #square.highlighted = self

    def unhighlight(self): # Todo: Implement
        self.image.fill(self.color) #Unhighlights duh

    def dot_highlight(self): # Todo: Implement
        print("dot highlighted")
        pass #Puts a small dot as an indicator

class TurnMarker(pygame.sprite.Sprite):
    """
    This is a marker that can change color when the turn changes"""
    def __init__(self, x, y, start_team, team_to_color, sprite_group):
        """
        args:
            x, y (ints): Screen position for marker
            start_team (int): Initial team
            team_to_color (dict, int: (r, g, b, trans)): Turns team numbers into colors
            sprite_group (group): Sprite group to be added to"""
        self.team = start_team
        self.team_to_color_dict = team_to_color

        pygame.sprite.Sprite.__init__(self)
        self.color = (255, 255, 255, 255)
        self.bgcolor = (0, 0, 0, 0)
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA, 32)
        self.image.fill(self.bgcolor)
        pygame.draw.circle(self.image, self.color, (85, 15), 10, 0)
        # Sets bg color as transparent!

        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y

        sprite_group.add(self)

    def change_turn(self, team):
        self.team = team
        self.image.fill((255,255,255,0))
        self.color = self.team_to_color_dict[self.team]
        pygame.draw.circle(self.image, self.color, (85, 15), 10, 0)

    def update(self):
        pass

                    


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
board_cols = 8
board_rows = 8
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
game_controller = Controller(curboard, None, GUI_sprites, piece_sprites)


#curboard.create_piece(piece, col, row, team, direction, sprite_group)


while not closed: # Todo: Implement or refactor
    if game:
        #rook_image = pygame.image.load(r'C:\Users\user\Pictures\.jpg')
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
### Consider a component based architecture
### Document
### Merge Board Method
