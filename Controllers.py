import pygame
from Standard_Pieces import *

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

class Controller: # Todo: Make controller inherit
    """The controller converts screen events to moves on the board"""
    """Keeps track of turns and win conditions. Handles clicks and events"""
    def __init__(self, board, mode, GUI_sprites, piece_sprites):
        self.turn = 1 #1 means white's, 0 for black
        self.board = board
        self.selected_piece = None
        self.selected_pos = None
        self.turn = 0 # 1 for white, 2 for black, 3 for ...
        self.turn_marker = TurnMarker(500, 0, 1, {1: (255, 255, 255), 2: (0, 0, 0)}, GUI_sprites)
                                      
        #raise NotImplemented
        self.set_up(piece_sprites)


    def click_responder(self, x, y): # Todo: Implement or refactor
        """
        Responds to a click at x, y
        
        args:
            x, y (int): position of click on the board"""
        #print(self.selected_piece)
        for sqrx, col in enumerate(self.board.squares):
            for sqry, sqr in enumerate(col):
                sqr.unhighlight() # Anything that's highlighted won't be after a click 
                if sqr.rect.collidepoint(x,y):
                    piece = self.board.state[sqrx][sqry] # Todo: Add highlighting in
                    if self.selected_piece == None:
                        self.selected_piece = piece
                        self.selected_pos = (sqrx, sqry)
                        if self.selected_piece:
                            sqr.highlight()
                    elif self.selected_piece == piece:
                        self.selected_piece = None
                        self.selected_pos = None
                    else: 
                        if self.selected_piece.team == self.turn%2+1:
                            success, err = self.board.move_piece(self.selected_pos[0], self.selected_pos[1], sqrx, sqry)
                            self.turn += success
                            self.board.render_board()
                            self.selected_piece = None
                            self.selected_pos = None
                            self.turn_marker.change_turn((self.turn)%2+1)
                        else:
                            print("Illegal Move")
                            self.selected_piece = None
                            self.selected_pos = None

    def set_up(self, piece_sprites):
        for col in range(8):
            self.board.create_piece(Pawn, col, 1, 2, "S", piece_sprites)
        self.board.create_piece(Baron, 0, 0, 2, "S", piece_sprites)
        self.board.create_piece(Baron, 7, 0, 2, "S", piece_sprites)
        self.board.create_piece(Baroness, 2, 0, 2, "S", piece_sprites)
        self.board.create_piece(Baroness, 5, 0, 2, "S", piece_sprites)
        self.board.create_piece(Knight, 1, 0, 2, "S", piece_sprites)
        self.board.create_piece(Chancellor, 3, 0, 2, "S", piece_sprites)
        self.board.create_piece(King, 4, 0, 2, "S", piece_sprites)
        self.board.create_piece(Knight, 6, 0, 2, "S", piece_sprites)
        for col in range(8):
            self.board.create_piece(Pawn, col, 6, 1, "N", piece_sprites)
        self.board.create_piece(Baron, 0, 7, 1, "N", piece_sprites)
        self.board.create_piece(Baron, 7, 7, 1, "N", piece_sprites)
        self.board.create_piece(Baroness, 2, 7, 1, "N", piece_sprites)
        self.board.create_piece(Baroness, 5, 7, 1, "N", piece_sprites)
        self.board.create_piece(Knight, 1, 7, 1, "N", piece_sprites)
        self.board.create_piece(Chancellor, 3, 7, 1, "N", piece_sprites)
        self.board.create_piece(King, 4, 7, 1, "N", piece_sprites)
        self.board.create_piece(Knight, 6, 7, 1, "N", piece_sprites)

    def undo_last_move(self):
        
        if self.board.undo():
            self.selected_piece = None
            self.selected_pos = None
            self.turn -= 1
        self.board.render_board() # Bring into controller class
        self.turn_marker.change_turn((self.turn)%2+1)

class DegenerateController: # Needs to be updated
    """The controller converts screen events to moves on the board"""
    """Keeps track of turns and win conditions. Handles clicks and events"""
    def __init__(self, board, mode, GUI_sprites, piece_sprites):
        self.turn = 1 #1 means white's, 0 for black
        self.board = board
        self.selected_piece = None
        self.selected_pos = None
        self.turn = 0 # 1 for white, 2 for black, 3 for ...
        self.turn_marker = TurnMarker(500, 0, 1, {1: (255, 255, 255), 2: (0, 0, 0)}, GUI_sprites)
                                      
        #raise NotImplemented
        self.set_up(piece_sprites)


    def click_responder(self, x, y): # Todo: Implement or refactor
        """
        Responds to a click at x, y
        
        args:
            x, y (int): position of click on the board"""
        #print(self.selected_piece)
        for sqrx, col in enumerate(self.board.squares):
            for sqry, sqr in enumerate(col):
                sqr.unhighlight() # Anything that's highlighted won't be after a click 
                if sqr.rect.collidepoint(x,y):
                    piece = self.board.state[sqrx][sqry] # Todo: Add highlighting in
                    if self.selected_piece == None:
                        self.selected_piece = piece
                        self.selected_pos = (sqrx, sqry)
                        if self.selected_piece:
                            sqr.highlight()
                    elif self.selected_piece == piece:
                        self.selected_piece = None
                        self.selected_pos = None
                    else: 
                        if self.selected_piece.team == self.turn%2+1:
                            success, err = self.board.move_piece(self.selected_pos[0], self.selected_pos[1], sqrx, sqry)
                            self.turn += success
                            self.board.render_board()
                            self.selected_piece = None
                            self.selected_pos = None
                            self.turn_marker.change_turn((self.turn)%2+1)
                        else:
                            print("Illegal Move")
                            self.selected_piece = None
                            self.selected_pos = None

    def set_up(self, piece_sprites):
        for col in range(4):
            self.board.create_piece(Pawn, col, 1, 2, "S", piece_sprites)
        self.board.create_piece(Rook, 0, 0, 2, "S", piece_sprites)
        self.board.create_piece(Bishop, 2, 0, 2, "S", piece_sprites)
        self.board.create_piece(Knight, 1, 0, 2, "S", piece_sprites)
        self.board.create_piece(King, 3, 0, 2, "S", piece_sprites)
        for col in range(4):
            self.board.create_piece(Pawn, col, 6, 1, "N", piece_sprites)
        self.board.create_piece(Rook, 3, 7, 1, "N", piece_sprites)
        self.board.create_piece(Bishop, 1, 7, 1, "N", piece_sprites)
        self.board.create_piece(Knight, 2, 7, 1, "N", piece_sprites)
        self.board.create_piece(King, 0, 7, 1, "N", piece_sprites)
                    
