from abc import ABC, abstractmethod #abstract base classes
from collections.abc import MutableMapping
#from abc import *
import pygame
from math import *
from functools import reduce
from operator import or_
from copy import copy

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
    '''This class holds all the data for a generic chess piece'''

    elephant_disp = ((2, 2), (-2, -2), (2, -2), (-2, 2)) # Holds the elephant displacement
    movement_components = ()
    knight_disp = ((2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2))
    images = {1: None, 2: None} # A team number gives the corresponding image for the piece
    
    direction_to_rotation = {"N": 0, "E": 1, "S": 2, "W": 3}
    
    def __init__(self, screen, team, direction, attributes = {"castle": False, "en passant": False}): #Remove i and j # Todo Remove x and y 
        """
        Instantiates a piece
        args:
            screen (Screen): Screen to render the piece on # Todo: remove
            team (int): Team for the piece
            direction ("N", "S", "E", or "W"): Direction the piece faces on the board
            attributes (dict): Attribute that the piece has (castling, en passant, etc.)
        """
        self.team = team #1 for white, 2 for black # TODO Rewrite comments and use row, col for board positions and x, y for pixel pos
        self.direction = direction
        self.attributes = copy(attributes) # This dictionary holds all the attributes for a piece (castling, en passant, etc.).
        # Stylistically, this should just be the name of the move
        #   An entry might look like "castle: False"
        # Copy allows for safe modification

        pygame.sprite.Sprite.__init__(self) # Todo: Document
        self.screen = screen
        self.r = 0
        #self.image  = pygame.Surface((self.r,self.r))
        #self.image.fill((0, 0, 0))
        
        #self.rect = self.image.get_rect()
        #self.rect.left = 0 # These will be changed when it gets rendered
        #self.rect.top = 0

    def convert_state_to_teams(self, state): # Todo: state vs. board consistancy
        """
        Converts a board into just the teams of pieces
        args:
            state (board): Board to convert
        returns:
            2D array of ints (team or 0 for no piece)"""
        return [[(0 if (not pc) else pc.team) for pc in col] for col in state]
    
    def get_legal_moves(self, state, x, y, turn = None):
        """
        Returns the legal moves for this piece
        args:
            state (board): Current state of the board
            x, y (ints): Location of the piece on the board
            turn (int): Turn of the game
        returns:
            The list of legal moves (where a move is a tuple of the form (col, row))"""
        return reduce(or_, [comp(state, x, y, self) for comp in self.movement_components], set())
                
    def __str__(self):
        """Returns the piece name"""
        return type(self).__name__

    def __copy__(self):
        """
        Creates a copy of this piece
        returns:
            A Piece object identical to this one"""
        piece = type(self)(self.screen, self.team, self.direction)
        piece.attributes = copy(self.attributes)
        return piece

    def make_move(self, state, col, row, newcol, newrow): # Todo: Implement or refactor (Refactor in King too)
        """Moves a piece from col, row to newcol, newrow

        Note: Pieces with different movement behavior
              from just capturing should reimplement this method   
        
        args:
            state (2D array): The current state of the board
            col, row (int): The current column and row of the piece
            newcol, newrow (int): The new column and row of the piece

        returns:
            (Turn movement [0 means same player moves again, 2 means skip a player, 1 is normal],
                2D array with the new board state)

        raises:
            IllegalMove: Raised when an illegal move is attempted"""
        if not ((newcol, newrow) in self.get_legal_moves(state, col, row)):
            raise IllegalMove(self)
        else:
            self.attributes["castle"] = False # Should be changed eventually
            new_state = self.board_deep_copy(state)
            new_state[col][row] = None
            captured_piece = new_state[newcol][newrow]
            new_state[newcol][newrow] = self
            if captured_piece:
                return (1, captured_piece.get_captured(new_state, newcol, newrow))
            else:
                return (1, new_state)

    def board_deep_copy(self, state): # This type of thing should be removed
        """Returns a deep copy of state
        args:
            state (2D array): The board to be copied
        returns:
            A deepcopy of the board"""
        return [[x for x in col] for col in state]

    def get_rotations(self): # Todo: Document, maybe merge with general indexing
        """
        Gets the number of counterclockwise rotations of the board so this piece can move properly
        returns:
            The number of rotations the board should be rotated when moving this piece"""
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
        """
        Drwas this piece
        args:
            x, y (ints): The location on the screen to draw this piece
            scale (int): Scale factor for the piece
            sprite_group (Sprite Group): Sprite group the pieces get added to"""
        image = pygame.transform.scale(self.images[self.team], (scale, scale))
        self.image = image
        sprite_group.add(self) # Todo: Stop re-adding piece to the same sprite group
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y

    def update(self):
        pass

        # Below are all the code that allows for accessing the various state attributes of a piece

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

class MovementComponent:
    def __init__(self, attack_range, attack_mode, max_jumps = 0):
        """
        Component for pieces. It returns valid moves for a certain type of movement (Rook up, bishop down, etc.)
            attack_range (int or inf): How many squares the piece can move (inclusive). Should be at least 1
            attack_mode (0, 1, or 2): The mode of the piece. 0 means it can both capture and make a non-capturing move, 1 means it must capture, 2 means it cannot capture
            exact_jumps (int or inf): The maximum number of pieces (friendly or unfriendly) this piece can jump over"""
        self.attack_mode = attack_mode
        self.attack_range = attack_range
        self.max_jumps = max_jumps

    @abstractmethod
    def __call__(self, state, x, y, piece):
        """
        Returns this movement component's legal moves
        args:
            state (board): Board state the moves should be checked with
            x, y (ints): Position of the piece
            piece (piece): The piece object that the moves might be made by

        returns:
            set of legal moves"""
        pass

    def convert_state_to_teams(self, state):
        """
        Converts state into the just the teams (0 for no piece)
        args:
            state (board): Board to be converted
        returns:
            2D array of ints"""
        return [[(0 if (not pc) else pc.team) for pc in col] for col in state]

class CompoundComponent(MovementComponent):
    def __init__(self, first_component, second_component, max_jumps = 0):
        """
        Component for combining components. It returns valid moves for a certain combinations of movement
            first_component (MovementComponent): The first component to be used
            second_component (MovementComponent): The second component to be used"""
        MovementComponent.__init__(self, None, None)
        self.first_component = first_component
        self.second_component = second_component

### All the following classes follow the above design pattern and
###     represent different types/combinations of movement

class RookUp(MovementComponent):
    def __init__(self, attack_range, attack_mode, max_jumps = 0):
        MovementComponent.__init__(self, attack_range, attack_mode, max_jumps)
    
    def __call__(self, state, x, y, piece): # Todo: Refactor Loop since it's the same for all of them
        """
        Returns the upwards orthogonal moves"""
        state = self.convert_state_to_teams(state)
        legal_moves = set()
        jumps_left = self.max_jumps
        for pos, piece_team in board_iterator(x, y-1, x, y-self.attack_range, 0, -1, state):
            if piece_team: # This ends the movement (since rook movement can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.add(pos)
                if jumps_left:
                    jumps_left -= 1
                else:
                    break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.add(pos)
        return legal_moves

class RookDown(MovementComponent):
    def __init__(self, attack_range, attack_mode, max_jumps = 0):
        MovementComponent.__init__(self, attack_range, attack_mode, max_jumps)
    
    def __call__(self, state, x, y, piece):
        """
        Returns the downwards orthogonal moves"""
        state = self.convert_state_to_teams(state)
        legal_moves = set()
        jumps_left = self.max_jumps
        for pos, piece_team in board_iterator(x, y+1, x, y+self.attack_range, 0, 1, state):
            if piece_team: # This ends the movement (since rook movement can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.add(pos)
                if jumps_left:
                    jumps_left -= 1
                else:
                    break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.add(pos)
        return legal_moves

class RookLeftRight(MovementComponent): # TODO rename and redocument; Make general board iterator for diagonal and horizontal that takes (start, end, and step)
    def __init__(self, attack_range, attack_mode, max_jumps = 0):
        MovementComponent.__init__(self, attack_range, attack_mode, max_jumps)
    
    def __call__(self, state, x, y, piece):
        """
        Returns the orthogonal moves in the left and right directions"""
        state = self.convert_state_to_teams(state)
        legal_moves = set()
        jumps_left = self.max_jumps
        for pos, piece_team in board_iterator(x+1, y, x+self.attack_range, y, 1, 0, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since rook movement can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.add(pos)
                if jumps_left:
                    jumps_left -= 1
                else:
                    break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.add(pos)
        jumps_left = self.max_jumps
        for pos, piece_team in board_iterator(x-1, y, x-self.attack_range, y, -1, 0, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since rook movement can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.add(pos)
                if jumps_left:
                    jumps_left -= 1
                else:
                    break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.add(pos)
        return legal_moves

class DiagonalUp(MovementComponent):
    def __init__(self, attack_range, attack_mode, max_jumps = 0):
        MovementComponent.__init__(self, attack_range, attack_mode, max_jumps)

    def __call__(self, state, x, y, piece):
        """
        Returns the upwards diagonal moves"""
        legal_moves = set()
        jumps_left = self.max_jumps
        state = self.convert_state_to_teams(state)
        for pos, piece_team in board_iterator(x+1, y-1, x+self.attack_range, y-self.attack_range, 1, -1, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since bishop's can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.add(pos)
                if jumps_left:
                    jumps_left -= 1
                else:
                    break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.add(pos)
        jumps_left = self.max_jumps
        for pos, piece_team in board_iterator(x-1, y-1, x-self.attack_range, y-self.attack_range, -1, -1, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since bishop's can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.add(pos)
                if jumps_left:
                    jumps_left -= 1
                else:
                    break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.add(pos)
        return legal_moves
        
class DiagonalDown(MovementComponent):
    def __init__(self, attack_range, attack_mode, max_jumps = 0):
        MovementComponent.__init__(self, attack_range, attack_mode, max_jumps)
        
    def __call__(self, state, x, y, piece):
        """
        Returns the downwards diagonal moves"""
        legal_moves = set()
        jumps_left = self.max_jumps
        state = self.convert_state_to_teams(state)
        for pos, piece_team in board_iterator(x+1, y+1, x+self.attack_range, y+self.attack_range, 1, 1, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since bishop's can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.add(pos)
                if jumps_left:
                    jumps_left -= 1
                else:
                    break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.add(pos)
        jumps_left = self.max_jumps
        for pos, piece_team in board_iterator(x-1, y+1, x-self.attack_range, y+self.attack_range, -1, 1, state): # Right movement code #Todo: x, y -> col, row
            if piece_team: # This ends the movement (since bishop's can't jump) so we break no matter what
                if piece_team != piece.team: # Checks to make sure the piece is on a different team
                    if self.attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.add(pos)
                if jumps_left:
                    jumps_left -= 1
                else:
                    break
            else:
                if self.attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.add(pos)
        return legal_moves
        
class KnightMove(MovementComponent):
    knight_disp = ((2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2)) # Holds the knight displacement

    def __init__(self):
        MovementComponent.__init__(self, None, None)

    def __call__(self, state, x, y, piece, max_jumps = 0):
        """
        Returns the knight moves"""
        legal_moves = set()
        state = self.convert_state_to_teams(state)
        for delta in self.knight_disp:
            if 0 <= x+delta[0] < len(state) and 0 <= y+delta[1] < len(state[0]): # Checks if it's a legal square 
                if not (state[x+delta[0]][y+delta[1]] == piece.team):
                    legal_moves.add((x+delta[0], y+delta[1]))
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
            return set()

class Castle(MovementComponent):

    def __init__(self):
        MovementComponent.__init__(self, None, None)

    def __call__(self, state, x, y, piece): # Todo Check for check
        """
        Returns legal castling options"""
        legal_moves = set() # Bug: Castling with adjacent piees
        if not piece.attributes["castle"]:
            return set()
        if x != len(state)-1:
            for cur_piece in (col[y] for col in state[x+1:]): # Castle right code
                if cur_piece:
                    if piece.team == cur_piece.team and cur_piece.attributes["castle"]:
                        legal_moves.add((x+2, y))
                    break
        if x != 0:
            for cur_piece in (col[y] for col in state[x-1::-1]): # Castle left code
                if cur_piece:
                    if piece.team == cur_piece.team and cur_piece.attributes["castle"]:
                        legal_moves.add((x-2, y))
                    break
        return legal_moves

class Intersection(CompoundComponent):
    def __init__(self, *comps):
        """
        Only returns the moves that both components return
            Note that this must take at least two comps"""
        assert len(comps) > 1
        if len(comps) == 2:
            CompoundComponent.__init__(self, comps[0], comps[1])
        else:
            CompoundComponent.__init__(self, comps[0], Intersection(*comps[1:]))

    def __call__(self, state, x, y, piece):
        return self.first_component(state, x, y, piece) & self.second_component(state, x, y, piece)

class Union(CompoundComponent): #Change intersection and composition to match
    def __init__(self, *comps):
        """
        Returns moves that either component returns
            Note that this must take at least two comps"""
        assert len(comps) > 1
        if len(comps) == 2:
            CompoundComponent.__init__(self, comps[0], comps[1])
        else:
            CompoundComponent.__init__(self, comps[0], Union(*comps[1:]))

    def __call__(self, state, x, y, piece):
        return self.first_component(state, x, y, piece) | self.second_component(state, x, y, piece)

class Subtraction(CompoundComponent):
    def __init__(self, *comps):
        """
        Returns moves that the first component returns and the second, third, fourth... don't
            Note that this must take at least two comps"""
        assert len(comps) > 1
        if len(comps) == 2:
            CompoundComponent.__init__(self, comps[0], comps[1])
        else:
            # Yes, union is correct. It makes it so ALL of the non-first components are subtracted
            CompoundComponent.__init__(self, comps[0], Union(*comps[1:]))

    def __call__(self, state, x, y, piece):
        return self.first_component(state, x, y, piece) - self.second_component(state, x, y, piece)

class Composition(CompoundComponent):
    def __init__(self, first_component, second_component):
        """
        Returns moves that the first component returns from each of the second component's moves from each of the third...
            Note that this doesn't change the piece's state so castling and en passant might not work as intended
            Does not return the piece's original square
            Does not update the state after each move
            Note that this must take at least two comps"""
        
        assert len(comps) > 1
        if len(comps) == 2:
            CompoundComponent.__init__(self, comps[0], comps[1])
        else:
            CompoundComponent.__init__(self, comps[0], Composition(*comps[1:]))



    def __call__(self, state, x, y, piece):
        legal_moves = set()
        for move in self.second_component(state, x, y, piece):
            legal_moves |= self.first_component(state, move[0], move[1], piece)



