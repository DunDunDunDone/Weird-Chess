from abc import ABC, abstractmethod #abstract base classes
from Pieces import *
from Weird_Pieces import *
import pygame
from math import *

### This file contains the code for all standard chess pieces ###

class King(Piece):
    images = {1:pygame.image.load('king.png'), 2: pygame.image.load('black_king.jpg')}
    
    def __init__(self, screen, team, direction): #Needs to be implemented later
        Piece.__init__(self, screen, team, direction) # Direction not implemented
        self.can_castle = True        

    def get_legal_moves(self, state, x, y, turn = None, last_move = None):
        state = self.convert_state_to_teams(state)
        if self.can_castle and False: # Todo: Replace False with castling conditions
            pass
        else:
            return (self.rook_left_right(state, x, y, 1)
                   + self.rook_up(state, x, y, 1)
                   + self.rook_down(state, x, y, 1)
                   + self.diagonal_up(state, x, y, 1)
                   + self.diagonal_down(state, x, y, 1))

    def get_captured(self, state, col, row):
        self.kill()
        raise KingCaptured(state, self.team)

class Queen(Piece):
    images = {1:pygame.image.load('queen.png'), 2: pygame.image.load('black_queen.jpg')}
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, team, direction)

    def get_legal_moves(self, state, x, y, turn = None, last_move = None):
        state = self.convert_state_to_teams(state)
        return (self.rook_left_right(state, x, y)
                + self.rook_up(state, x, y)
                + self.rook_down(state, x, y)
                + self.diagonal_up(state, x, y)
                + self.diagonal_down(state, x, y))

class Rook(Piece):
    images = {1:pygame.image.load('rook.jpg'), 2: pygame.image.load('black_rook.jpg')}
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, team, direction)
        self.can_castle = True

    def get_legal_moves(self, state, x, y, turn = None, last_move = None):
        state = self.convert_state_to_teams(state)
        return (self.rook_left_right(state, x, y)
                + self.rook_up(state, x, y)
                + self.rook_down(state, x, y))

class Bishop(Piece): # This class has all the methods it needs
    images = {1:pygame.image.load('bishop.jpg'), 2: pygame.image.load('black_bishop.jpg')}
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, team, direction)

    def get_legal_moves(self, state, x, y, turn = None, last_move = None):
        state = self.convert_state_to_teams(state)
        return (self.diagonal_up(state, x, y)
                + self.diagonal_down(state, x, y))

class Knight(Piece):
    images = {1:pygame.image.load('knight.png'), 2: pygame.image.load('black_knight.png')}
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, team, direction)

    def get_legal_moves(self, state, x, y, turn = None, last_move = None):
        state = self.convert_state_to_teams(state)
        return self.knight_move(state, x, y)

class Pawn(Piece):
    images = {1:pygame.image.load('pawn.png'), 2: pygame.image.load('black_pawn.png')}
    
    def __init__(self, screen, team, direction):
        Piece.__init__(self, screen, team, direction)

    def get_legal_moves(self, state, x, y, turn = None, last_move = None):
        state = self.convert_state_to_teams(state)
        if y == len(state[0])-2: # If the pawn is on the second rank (-2 because of indexing)...
            return (self.diagonal_up(state, x, y, attack_range = 1, attack_mode = 1)
                    + self.rook_up(state, x, y, attack_range = 2, attack_mode = 2))
        else:
            return (self.diagonal_up(state, x, y, attack_range = 1, attack_mode = 1)
                    + self.rook_up(state, x, y, attack_range = 1, attack_mode = 2))

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


