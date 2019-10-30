from abc import ABC, abstractmethod #abstract base classes
from Pieces import *
import pygame
from math import *

### This file contains the code for the weird chess pieces ###

class Baron(Piece):
    images = {1:pygame.image.load('baron.png'), 2: pygame.image.load('black_baron.png')}

    
    def __init__(self, screen, team, direction): #Needs to be implemented later
        Piece.__init__(self, screen, team, direction) # Direction not implemented

    def get_legal_moves(self, state, x, y, turn = None, last_move = None):
        return (self.rook_left_right(state, x, y, attack_mode = 2)
                + self.rook_up(state, x, y, attack_mode = 2)
                + self.rook_down(state, x, y, attack_mode = 2)
                + self.diagonal_up(state, x, y, attack_mode = 1)
                + self.diagonal_down(state, x, y, attack_mode = 1))

class Baroness(Piece):
    images = {1:pygame.image.load('baroness.png'), 2: pygame.image.load('black_baroness.png')}

    
    def __init__(self, screen, team, direction): #Needs to be implemented later
        Piece.__init__(self, screen, team, direction) # Direction not implemented

    def get_legal_moves(self, state, x, y, turn = None, last_move = None):
        return (self.rook_left_right(state, x, y, attack_mode = 1)
                + self.rook_up(state, x, y, attack_mode = 1)
                + self.rook_down(state, x, y, attack_mode = 1)
                + self.diagonal_up(state, x, y, attack_mode = 2)
                + self.diagonal_down(state, x, y, attack_mode = 2))

class Chancellor(Piece):
    images = {1:pygame.image.load('chancellor.png'), 2: pygame.image.load('black_chancellor.png')}

    
    def __init__(self, screen, team, direction): #Needs to be implemented later
        Piece.__init__(self, screen, team, direction) # Direction not implemented

    def get_legal_moves(self, state, x, y, turn = None, last_move = None):
        return (self.rook_up(state, x, y)
                + self.diagonal_down(state, x, y))





