from abc import ABC, abstractmethod #abstract base classes
from Pieces import *
import pygame
from math import *

### This file contains the code for the weird chess pieces ###

class Baron(Piece):
    images = {1:pygame.image.load('baron.png'), 2: pygame.image.load('black_baron.png')}
    movement_components = [RookUp(float("inf"), 2),
                           RookDown(float("inf"), 2),
                           DiagonalUp(float("inf"), 1),
                           DiagonalDown(float("inf"), 1),
                           RookLeftRight(float("inf"), 2)]
                
    def __init__(self, screen, team, direction): #Needs to be implemented later
        Piece.__init__(self, screen, team, direction) # Direction not implemented
        self.can_castle = True


class Baroness(Piece):
    images = {1:pygame.image.load('baroness.png'), 2: pygame.image.load('black_baroness.png')}
    movement_components = [RookUp(float("inf"), 1),
                           RookDown(float("inf"), 1),
                           DiagonalUp(float("inf"), 2),
                           DiagonalDown(float("inf"), 2),
                           RookLeftRight(float("inf"), 1)]
    
class Chancellor(Piece):
    images = {1:pygame.image.load('chancellor.png'), 2: pygame.image.load('black_chancellor.png')}
    movement_components = [RookUp(float("inf"), 0),
                           DiagonalDown(float("inf"), 0)]
