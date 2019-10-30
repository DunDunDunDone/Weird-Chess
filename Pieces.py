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
    knight_disp = ((2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2)) # Holds the knight displacement
    elephant_disp = ((2, 2), (-2, -2), (2, -2), (-2, 2)) # Holds the elephant displacement
    images = {1: None, 2: None} # A team number gives the corresponding image for the piece
    
    direction_to_rotation = {"N": 0, "E": 1, "S": 2, "W": 3}
    
    def __init__(self, screen, team, direction): #Remove i and j # Todo Remove x and y since the board knows that
        # Direction will be N, S, E, or W
        self.team = team #1 for white, 2 for black # TODO Rewrite comments and use row, col for board positions and x, y for pixel pos
        self.direction = direction
        self.can_castle = False # Will be changed after first move # Todo: Implement or refactor
        self.can_en_passant = False # Is this piece capable of en passant in general # Todo: Implement or refactor

        pygame.sprite.Sprite.__init__(self) # Todo: Document
        self.screen = screen
        self.r = 0
        #self.image  = pygame.Surface((self.r,self.r))
        #self.image.fill((0, 0, 0))
        
        #self.rect = self.image.get_rect()
        #self.rect.left = 0 # These will be changed when it gets rendered
        #self.rect.top = 0
    
    @abstractmethod
    def get_legal_moves(self, state, turn = None):
        '''The state of the board (0 for empty, 1 for white piece, 2 for black piece) and turn (first turn is 1)'''
        '''Returns a list of tuples'''
        pass

    def rook_left_right(self, state, x, y, attack_range = float("inf"), attack_mode = 0): # TODO rename and redocument; Make general board iterator for diagonal and horizontal that takes (start, end, and step)
        """ # Todo: Implement or refactor
        Returns the orthogonal moves in the left and right directions
        args:
            state (2D array): The state of the board where the piece is moving on
            x, y (ints): Positions of the piece
            attack_range (int): How many squares the piece can move (inclusive). Should be at least 1
            attack_mode (0, 1, or 2): The mode of the piece. 0 means it can both capture and make a non-capturing move, 1 means it must capture, 2 means it cannot capture
        returns:
            A list of tuples representing legal moves"""
        legal_moves = []
        for col in range(x+1, min(x+1+attack_range, len(state))):#min(attack_range, len(state))): #Finds squares to the right
            if state[col][y]: #Checks for a piece of any kind
                if state[col][y] == self.team:
                    break #Rooks can't jump and can't capture their own pieces
                else:
                    if attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append((col, y))
                    break #Rooks can't jump but can capture other pieces
            else:
                if attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append((col, y))
        for col in range(x-1, max(-1, x-attack_range-1), -1): #Finds squares to the left
            if state[col][y]: #Checks for a piece of any kind
                if state[col][y] == self.team:
                    break #Rooks can't jump and can't capture their own pieces
                else:
                    if attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append((col, y))
                    break #Rooks can't jump but can capture other pieces
            else:
                if attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append((col, y))
        return legal_moves

    def rook_up(self, state, x, y, attack_range = float("inf"), attack_mode = 0):
        """
        Returns the upwards orthogonal moves
        args:
            state (2D array): The state of the board where the piece is moving on
            x, y (ints): Positions of the piece
            attack_range (int): How many squares the piece can move (inclusive). Should be at least 1
            attack_mode (0, 1, or 2): The mode of the piece. 0 means it can both capture and make a non-capturing move, 1 means it must capture, 2 means it cannot capture
        returns:
            A list of tuples representing legal moves"""
        legal_moves = []
        for row in range(y-1, max(-1, y-attack_range-1), -1): #Gives the indices of the rows starting with the square above the piece
            if state[x][row]: #Checks for a piece of any kind
                if state[x][row] == self.team:
                    break #Rooks can't jump and can't capture their own pieces
                else:
                    if attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append((x, row))
                    break #Rooks can't jump but can capture other pieces
            else:
                if attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append((x, row))
        return legal_moves
            
    def rook_down(self, state, x, y, attack_range = float("inf"), attack_mode = 0): #This method is just rook_up in the opposite direction
        """
        Returns the downwards orthogonal moves
        args:
            state (2D array): The state of the board where the piece is moving on
            x, y (ints): Positions of the piece
            attack_range (int): How many squares the piece can move (inclusive). Should be at least 1
            attack_mode (0, 1, or 2): The mode of the piece. 0 means it can both capture and make a non-capturing move, 1 means it must capture, 2 means it cannot capture
        returns:
            A list of tuples representing legal moves"""
        legal_moves = []
        for row in range(y+1, min(y+1+attack_range, len(state[x]))):#len(state[x])): #Gives the indices of the rows starting with the square above the piece
            if state[x][row]: #Checks for a piece of any kind
                if state[x][row] == self.team:
                    break #Rooks can't jump and can't capture their own pieces
                else:
                    if attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append((x, row))
                    break #Rooks can't jump but can capture other pieces
            else:
                if attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append((x, row))
        return legal_moves

    def diagonal_up(self, state, x, y, attack_range = float("inf"), attack_mode = 0):
        legal_moves = []
        for delta in range(1, min(attack_range, (min(x, y)))+1): # Diagonal up left
            if state[x-delta][y-delta]: #Checks for a piece of any kind
                if state[x-delta][y-delta] == self.team:
                    break # Bishops can't jump and can't capture their own pieces
                else:
                    if attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append((x-delta, y-delta))
                    break # Bishops can't jump but can capture other pieces
            else:
                if attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append((x-delta, y-delta))
        for delta in range(1, min(attack_range, min(len(state)-x-1, y))+1): # Diagonal up right
            if state[x+delta][y-delta]: #Checks for a piece of any kind
                if state[x+delta][y-delta] == self.team:
                    break # Bishops can't jump and can't capture their own pieces
                else:
                    if attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append((x+delta, y-delta))
                    break # Bishops can't jump but can capture other pieces
            else:
                if attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append((x+delta, y-delta))
        return legal_moves

    def diagonal_down(self, state, x, y, attack_range = float("inf"), attack_mode = 0):
        legal_moves = []
        for delta in range(1, min(attack_range, min(x, len(state[0])-y-1))+1): # Diagonal down left # Todo: Combine min statements
            if state[x-delta][y+delta]: #Checks for a piece of any kind
                if state[x-delta][y+delta] == self.team:
                    break # Bishops can't jump and can't capture their own pieces
                else:
                    if attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append((x-delta, y+delta))
                    break # Bishops can't jump but can capture other pieces
            else:
                if attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append((x-delta, y+delta))
        for delta in range(1, min(attack_range, min(len(state)-x-1, len(state[0])-y-1))+1): # Diagonal down right
            if state[x+delta][y+delta]: #Checks for a piece of any kind
                if state[x+delta][y+delta] == self.team:
                    break # Bishops can't jump and can't capture their own pieces
                else:
                    if attack_mode != 2: # If the piece cannot capture, this code won't be run
                        legal_moves.append((x+delta, y+delta))
                    break # Bishops can't jump but can capture other pieces
            else:
                if attack_mode != 1: # If the piece must capture (attack_mode = 1), this code won't be run
                    legal_moves.append((x+delta, y+delta))
        return legal_moves

    def knight_move(self, state, x, y):
        legal_moves = []
        for delta in self.knight_disp:
            if 0 <= x+delta[0] < len(state) and 0 <= y+delta[1] < len(state[0]): # Checks if it's a legal square 
                if not (state[x+delta[0]][y+delta[1]] == self.team):
                    legal_moves.append((x+delta[0], y+delta[1]))
        return legal_moves
                
    def __str__(self):
        """Returns the piece name"""
        return type(self).__name__

    def make_move(self, state, col, row, newcol, newrow): # Todo: Implement or refactor
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
        self.can_castle = False
        if not ((newcol, newrow) in self.get_legal_moves(state, col, row)):
            raise IllegalMove(self)
        else:  
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

    def draw_piece(self, x, y, scale, sprite_group): # Todo Create scaling
        """Drwas this piece at x, y scaled up by scale, and adds it to sprite_group"""
        image = pygame.transform.scale(self.images[self.team], (scale, scale))
        self.image = image
        sprite_group.add(self) # Todo: Stop re-adding piece to the same sprite group
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        #self.image.inflate(scale, scale)
        #self.rect.fit(scale)
        #self.rect.size = (1000*scale, 1000*scale)
        #print(dir(self.rect))
        #print(self.image)
        #1/0

    def update(self):
        pass
