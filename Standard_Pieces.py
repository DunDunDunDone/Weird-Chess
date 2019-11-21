from abc import ABC, abstractmethod #abstract base classes
from Pieces import *
from Weird_Pieces import *
import pygame
from math import *

### This file contains the code for all standard chess pieces ###

class King(Piece):
    images = {1:pygame.image.load('king.png'), 2: pygame.image.load('black_king.jpg')}

    movement_components = [Castle(),
                           RookUp(0, 1),
                           RookDown(0, 1),
                           RookLeftRight(0, 1),
                           DiagonalUp(0, 1),
                           DiagonalDown(0, 1)]
    
    def __init__(self, screen, team, direction): #Needs to be implemented later
        Piece.__init__(self, screen, team, direction) # Direction not implemented
        self.can_castle = True

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
            self.can_castle = False # Should be changed eventually
            new_state = self.board_deep_copy(state)
            if abs(col-newcol) == 2: # If you castled, run this
                delta = int(copysign(1, col-newcol)) #
                col_to_check = col-delta
                # col, cur_piece in enumerate((col[y] for col in state[x+1:])): # 
                while 0 <= col_to_check < len(state): # Todo: Change loop to use enumerate
                    piece = state[col_to_check][row]
                    if piece and piece.can_castle and piece.team == self.team:
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
    
    movement_components = [RookUp(0, float("inf")),
                           RookDown(0, float("inf")),
                           DiagonalUp(0, float("inf")),
                           DiagonalDown(0, float("inf")),
                           RookLeftRight(0, float("inf"))]
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, team, direction)

class Rook(Piece):
    images = {1:pygame.image.load('rook.jpg'), 2: pygame.image.load('black_rook.jpg')}

    movement_components = [RookUp(0, float("inf")),
                           RookDown(0, float("inf")),
                           RookLeftRight(0, float("inf"))]
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, team, direction)
        self.can_castle = True

class Bishop(Piece): # This class has all the methods it needs
    images = {1:pygame.image.load('bishop.jpg'), 2: pygame.image.load('black_bishop.jpg')}
    movement_components = [DiagonalUp(0, float("inf")),
                           DiagonalDown(0, float("inf"))]
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, team, direction)

class Knight(Piece):
    images = {1:pygame.image.load('knight.png'), 2: pygame.image.load('black_knight.png')}
    movement_components = [KnightMove(0, 0)]
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, team, direction)


class Pawn(Piece):
    images = {1:pygame.image.load('pawn.png'), 2: pygame.image.load('black_pawn.png')}
    movement_components = [DiagonalUp(1, 1), RookUp(2, 1), Charge(2, 2, 6)] # Todo: Change pawn to not be hardcoded
    
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


