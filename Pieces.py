from abc import ABC, abstractmethod #abstract base classes
#from abc import *
import pygame
from math import *
from functools import reduce
from operator import add

class PromotionError(Exception):
    """This exception should be raised when a piece promotes to another piece"""
    '''try, except PromotionError as err'''
    def __init__(self, state, promoted_piece, piece_options):
        self.msg = "This " + str(promoted_piece) + " got a promotion!"
        self.state = state
        self.piece = promoted_piece
        self.new_pieces = piece_options

class IllegalMove(Exception):
    """Raised whenever a piece is told to make an illegal move

        args:
            piece (Piece): Piece that will be mentioned in the error message"""
    def __init__(self, piece = "unknown source"):
        self.msg = "An illegal move was made by a(n) " + str(piece)

class KingCaptured(Exception):
    """Raised whenever a king is captured

        args:
            team (int): Team that just had its king captured
            state (2D array): The state that the king was captured in"""
    def __init__(self, state, team = 0):
        self.state = state
        self.msg = "You lost since your king was captured"


class Piece(pygame.sprite.Sprite, ABC): #
    '''This class holds all the data about a chess piece'''
    '''To be coded using the code for bishops and rooks'''
    elephant_disp = ((2, 2), (-2, -2), (2, -2), (-2, 2)) # Holds the elephant displacement
    movement_components = ()
    knight_disp = ((2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2))
    images = {1: None, 2: None} # A team number gives the corresponding image for the piece
    
    direction_to_rotation = {"N": 0, "E": 1, "S": 2, "W": 3}
    
    def __init__(self, screen, team, direction): #Remove i and j # Todo Remove x and y since the board knows that
        # Direction will be N, S, E, or W
        self.team = team #1 for white, 2 for black # TODO Rewrite comments and use row, col for board positions and x, y for pixel pos
        self.direction = direction
        self.can_castle = False # Will be changed after first move # Todo: Implement or refactor
        self.can_en_passant = False # Is this piece capable of en passant in general # Todo: Implement or refactor # This should stay outside compenets

        pygame.sprite.Sprite.__init__(self) # Todo: Document
        self.screen = screen
        self.r = 0
        #self.image  = pygame.Surface((self.r,self.r))
        #self.image.fill((0, 0, 0))
        
        #self.rect = self.image.get_rect()
        #self.rect.left = 0 # These will be changed when it gets rendered
        #self.rect.top = 0

    def convert_state_to_teams(self, state): # Todo: Document
        return [[(0 if (not pc) else pc.team) for pc in col] for col in state]
    
    def get_legal_moves(self, state, x, y, turn = None):
        '''The state of the board (0 for empty, 1 for white piece, 2 for black piece) and turn (first turn is 1)'''
        '''Returns a list of tuples'''
        return reduce(add, [comp(state, x, y, self) for comp in self.movement_components])
                
    def __str__(self):
        """Returns the piece name"""
        return type(self).__name__

    def make_move(self, state, col, row, newcol, newrow): # Todo: Implement or refactor (Refactor in King too)
        """Moves a piece from col, row to newcol, newrow

        Note: Pieces with different movement behavior
              from just capturing should reimplement this method   
        
        args:
            state (2D array): The current state of the board
            col, row (int): The current column and row of the piece
            newcol, newrow (int): The new column and row of the piece

        returns:
            2D array with the new board state

        raises:
            IllegalMove: Raised when an illegal move is attempted"""
        if not ((newcol, newrow) in self.get_legal_moves(state, col, row)):
            raise IllegalMove(self)
        else:
            self.can_castle = False # Should be changed eventually
            new_state = self.board_deep_copy(state)
            new_state[col][row] = None
            captured_piece = new_state[newcol][newrow]
            new_state[newcol][newrow] = self
            if captured_piece:
                return captured_piece.get_captured(new_state, newcol, newrow)
            else:
                return new_state

    def board_deep_copy(self, state):
        """Returns a deep copy of state"""
        return [[x for x in col] for col in state]

    def get_rotations(self): # Todo: Document
        """Gets the number of counterclockwise rotations of the board so this piece can move properly"""
        return self.direction_to_rotation[self.direction] # Based on direction

    def get_captured(self, state, col, row):
        """Runs events that happen when the piece is captured and
            removes it from all sprite groups

        args:
            state (2D array): The state without the capture piece and with
                              the new piece moved to the new location.
            col, row (int): The former position of this piece
        returns:
            The new state (which will just be state for most pieces)"""
        self.kill()
        return state

    def draw_piece(self, x, y, scale, sprite_group):
        """Drwas this piece at x, y scaled up by scale, and adds it to sprite_group"""
        image = pygame.transform.scale(self.images[self.team], (scale, scale))
        self.image = image
        sprite_group.add(self) # Todo: Stop re-adding piece to the same sprite group
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y

    def update(self):
        pass

def multiply_by_sign(n1, n2):
    """Returns n1 multiplied by the sign of n2 (for 0 it remains the same)"""
    if n2 < 0:
        return -n1
    else:
        return n1

def board_iterator(startx, starty, limx, limy, dx, dy, state):
    """Iterates from startx to limx (inclusive) and starty to limy (or until done with state) with steps of (dx, dy).
        If it encounters limx or limy it breaks. Returns things of the form (pos, square)"""
    curx = startx
    cury = starty
    broundx = len(state) # The bround on x given the width of state
    broundy = len(state[0]) # The bround on y given the length of state
    assert not ((limx < startx and dx > 0) or (limx > startx and dx < 0) or (dx == 0 and limx != startx)), "You've used board_iterator with dx going the wrong way"
    assert not ((limy < starty and dy > 0) or (limy > starty and dy < 0) or (dy == 0 and limy != starty)), "You've used board_iterator with dy going the wrong way"
    while 0 <= curx < broundx and 0 <= cury < broundy and multiply_by_sign(curx, dx) <= multiply_by_sign(limx, dx) and multiply_by_sign(cury, dy) <= multiply_by_sign(limy, dy):
        # Checks if it's less than (or greater than) the limits and in the board
        yield ((curx, cury), state[curx][cury])
        curx += dx
        cury += dy
    

class MovementComponent: # Todo: Document
    def __init__(self, attack_range, attack_mode):
        """
        Component for pieces. It returns valid moves for a certain type of movement (Rook up, bishop down, etc.)
            attack_range (int or inf): How many squares the piece can move (inclusive). Should be at least 1
            attack_mode (0, 1, or 2): The mode of the piece. 0 means it can both capture and make a non-capturing move, 1 means it must capture, 2 means it cannot capture"""
        self.attack_mode = attack_mode
        self.attack_range = attack_range

    @abstractmethod
    def __call__(self, state, x, y, piece):
        """Todo: Document"""
        pass

    def convert_state_to_teams(self, state): # Todo: Document
        return [[(0 if (not pc) else pc.team) for pc in col] for col in state]

class RookUp(MovementComponent):
    def __init__(self, attack_range, attack_mode):
        MovementComponent.__init__(self, attack_range, attack_mode)
    
    def __call__(self, state, x, y, piece): # Todo: Refactor
        """
        Returns the upwards orthogonal moves
        args:
            state (2D array): The state of the board where the piece is moving on
            x, y (ints): Positions of the piece
        returns:
            A list of tuples representing legal moves"""
        state = self.convert_state_to_teams(state)
        legal_moves = []
        for pos, piece_team in board_iterator(x, y-1, x, y-self.attack_range, 0, -1, state):
            if piece_team: # This ends the movement (since rook movement can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append(pos)
                break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append(pos)
        return legal_moves

class RookDown(MovementComponent):
    def __init__(self, attack_range, attack_mode):
        MovementComponent.__init__(self, attack_range, attack_mode)
    
    def __call__(self, state, x, y, piece):
        """
        Returns the downwards orthogonal moves
        args:
            state (2D array): The state of the board where the piece is moving on
            x, y (ints): Positions of the piece
            piece (Piece): The piece object so the component knows attributes about the piece (for castling and the like)
        returns:
            A list of tuples representing legal moves"""
        state = self.convert_state_to_teams(state)
        legal_moves = []
        for pos, piece_team in board_iterator(x, y+1, x, y+self.attack_range, 0, 1, state):
            if piece_team: # This ends the movement (since rook movement can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append(pos)
                break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append(pos)
        return legal_moves

class RookLeftRight(MovementComponent): # TODO rename and redocument; Make general board iterator for diagonal and horizontal that takes (start, end, and step)
    def __init__(self, attack_range, attack_mode):
        MovementComponent.__init__(self, attack_range, attack_mode)
    
    def __call__(self, state, x, y, piece):
        """ # Todo: Implement or refactor
        Returns the orthogonal moves in the left and right directions
        args:
            state (2D array): The state of the board where the piece is moving on
            x, y (ints): Positions of the piece
            piece (Piece): The piece object so the component knows attributes about the piece (for castling and the like)
        returns:
            A list of tuples representing legal moves"""
        state = self.convert_state_to_teams(state)
        legal_moves = []
        for pos, piece_team in board_iterator(x+1, y, x+self.attack_range, y, 1, 0, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since rook movement can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append(pos)
                break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append(pos)
        for pos, piece_team in board_iterator(x-1, y, x-self.attack_range, y, -1, 0, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since rook movement can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append(pos)
                break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append(pos)
        return legal_moves

class DiagonalUp(MovementComponent):
    def __init__(self, attack_range, attack_mode):
        MovementComponent.__init__(self, attack_range, attack_mode)

    def __call__(self, state, x, y, piece):
        legal_moves = []
        state = self.convert_state_to_teams(state)
        for pos, piece_team in board_iterator(x+1, y-1, x+self.attack_range, y-self.attack_range, 1, -1, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since bishop's can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append(pos)
                break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append(pos)
        for pos, piece_team in board_iterator(x-1, y-1, x-self.attack_range, y-self.attack_range, -1, -1, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since bishop's can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append(pos)
                break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append(pos)
        return legal_moves
        
class DiagonalDown(MovementComponent):
    def __init__(self, attack_range, attack_mode):
        MovementComponent.__init__(self, attack_range, attack_mode)
		
    def __call__(self, state, x, y, piece):
        legal_moves = []
        state = self.convert_state_to_teams(state)
        for pos, piece_team in board_iterator(x+1, y+1, x+self.attack_range, y+self.attack_range, 1, 1, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since bishop's can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append(pos)
                break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append(pos)
        for pos, piece_team in board_iterator(x-1, y+1, x-self.attack_range, y+self.attack_range, -1, 1, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since bishop's can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append(pos)
                break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append(pos)
        return legal_moves
        
class KnightMove(MovementComponent):
    knight_disp = ((2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2)) # Holds the knight displacement

    def __init__(self):
        MovementComponent.__init__(self, None, None)

    def __call__(self, state, x, y, piece):
        legal_moves = []
        state = self.convert_state_to_teams(state)
        for delta in self.knight_disp:
            if 0 <= x+delta[0] < len(state) and 0 <= y+delta[1] < len(state[0]): # Checks if it's a legal square 
                if not (state[x+delta[0]][y+delta[1]] == piece.team):
                    legal_moves.append((x+delta[0], y+delta[1]))
        return legal_moves

class Charge(MovementComponent):

    def __init__(self, attack_range, attack_mode, charge_row):
        self.charge_row = charge_row
        self.helper_component = RookUp(2, 2) # Component to find moves
        MovementComponent.__init__(self, attack_range, attack_mode)

    def __call__(self, state, x, y, piece):
        if y == self.charge_row:
            return self.helper_component(state, x, y, piece)
        else:
            return []

class Castle(MovementComponent):

    def __init__(self):
        MovementComponent.__init__(self, None, None)

    def __call__(self, state, x, y, piece): # Todo Check for check
        legal_moves = []
        if not piece.can_castle:
            return []
        for cur_piece in (col[y] for col in state[x+1:]): # Castle right code
            if cur_piece:
                if piece.team == cur_piece.team and cur_piece.can_castle:
                    legal_moves.append((x+2, y))
                break
        for cur_piece in (col[y] for col in state[:x]): # Castle left code
            if cur_piece:
                if piece.team == cur_piece.team and cur_piece.can_castle:
                    legal_moves.append((x-2, y))
                break
        return legal_moves


