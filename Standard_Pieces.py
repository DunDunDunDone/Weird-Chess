from abc import ABC, abstractmethod #abstract base classes
from Generic_Piece import *
import pygame
from math import *


"""
This file contains the code for the standard chess pieces.
Movement components are added at the beginning of the class
    by modifying the movement_components variable
"""

class EveryTeam: # Document, Singleton?
    """This object makes a piece act like it's on every team
            when the piece's team is set to this object"""
    def __eq__(self, x):
        return True

    def __hash__(self):
        return 16161616161616161616

    def __mod__(self, x):
        return 0

class EmptySquare(Piece):
    images = {EveryTeam():pygame.image.load('black_square.png')}
    movement_components = []
    """
    This looks like a hole on the board and
        can't be captured or moved over"""
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, EveryTeam(), direction)

class King(Piece):
    images = {1:pygame.image.load('king.png'), 2: pygame.image.load('black_king.jpg')}

    movement_components = [Castle(),
                           RookUp(1, 0),
                           RookDown(1, 0),
                           RookLeftRight(1, 0),
                           DiagonalUp(1, 0),
                           DiagonalDown(1, 0)]
    
    def __init__(self, screen, team, direction): #Needs to be implemented later
        Piece.__init__(self, screen, team, direction) # Direction not implemented
        self.attributes["castle"] = True

    def get_captured(self, state, col, row):
        self.kill()
        raise KingCaptured(state, self.team)

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
        if not ((newcol, newrow) in self.get_legal_moves(state, col, row)):
            raise IllegalMove(self)
        else:
            self.attributes["castle"] = False # Should be changed eventually
            new_state = self.board_deep_copy(state)
            if abs(col-newcol) == 2: # If you castled, run this
                delta = int(copysign(1, col-newcol)) #
                col_to_check = col-delta
                # col, cur_piece in enumerate((col[y] for col in state[x+1:])): # 
                while 0 <= col_to_check < len(state): # Todo: Change loop to use enumerate
                    piece = state[col_to_check][row]
                    if piece and piece.attributes["castle"] and piece.team == self.team:
                        new_state[col][row] = None # Todo: Check for check
                        new_state[col_to_check][row] = None
                        new_state[newcol][newrow] = self
                        new_state[newcol+delta][newrow] = piece
                        #print(new_state)
                        return new_state
                    col_to_check -= delta
            else:
                new_state[col][row] = None
                captured_piece = new_state[newcol][newrow]
                new_state[newcol][newrow] = self
                if captured_piece:
                    return captured_piece.get_captured(new_state, newcol, newrow)
                else:
                    return new_state

class Queen(Piece):
    images = {1:pygame.image.load('queen.png'), 2: pygame.image.load('black_queen.jpg')}
    
    movement_components = [RookUp(float("inf"), 0),
                           RookDown(float("inf"), 0),
                           DiagonalUp(float("inf"), 0),
                           DiagonalDown(float("inf"), 0),
                           RookLeftRight(float("inf"), 0)]

class Rook(Piece):
    images = {1:pygame.image.load('rook.jpg'), 2: pygame.image.load('black_rook.jpg')}

    movement_components = [RookUp(float("inf"), 0),
                           RookDown(float("inf"), 0),
                           RookLeftRight(float("inf"), 0)]
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, team, direction)
        self.attributes["castle"] = True

class Bishop(Piece): # This class has all the methods it needs
    images = {1:pygame.image.load('bishop.jpg'), 2: pygame.image.load('black_bishop.jpg')}
    movement_components = [DiagonalUp(float("inf"), 0),
                           DiagonalDown(float("inf"), 0)]

class Knight(Piece):
    images = {1:pygame.image.load('knight.png'), 2: pygame.image.load('black_knight.png')}
    movement_components = [KnightMove()]


class Pawn(Piece):
    images = {1:pygame.image.load('pawn.png'), 2: pygame.image.load('black_pawn.png')}
    movement_components = [DiagonalUp(1, 1), RookUp(1, 2), Charge(2, 2, 6)] # Todo: Change pawn to not be hardcoded
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, team, direction)

    '''    def get_legal_moves(self, state, x, y, turn = None, last_move = None):
        state = self.convert_state_to_teams(state)
        if y == len(state[0])-2: # If the pawn is on the second rank (-2 because of indexing)...'''

    def make_move(self, state, col, row, newcol, newrow):
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
            IllegalMove: Raised when an illegal move is attempted
            PromotionError: Raised when this piece promotes which lets the controller know what to do"""
        if not ((newcol, newrow) in self.get_legal_moves(state, col, row)):
            raise IllegalMove(self)
        else:  
            new_state = self.board_deep_copy(state)
            new_state[col][row] = None
            captured_piece = new_state[newcol][newrow]
            if newrow == 0:
                new_state[newcol][newrow] = None
                self.kill() # Removes the image
                if captured_piece:
                    raise PromotionError(captured_piece.get_captured(new_state, newcol, newrow), self, [Bishop, Knight, Rook, Queen])
                else:
                    raise PromotionError(new_state, self, [Bishop, Knight, Rook, Queen])
            else:
                new_state[newcol][newrow] = self
                if captured_piece:
                    return captured_piece.get_captured(new_state, newcol, newrow)
                else:
                    return new_state


