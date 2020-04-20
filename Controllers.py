import pygame
from Standard_Pieces import *
from Weird_Pieces import *

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
        """
        Changes the color of the TurnMarker to match the team given
        args:
            team (int): The team to change this object to"""
        self.team = team
        self.image.fill((255,255,255,0))
        self.color = self.team_to_color_dict[self.team]
        pygame.draw.circle(self.image, self.color, (85, 15), 10, 0)

    def update(self):
        pass

# Controller API
# Controller(inputs)
# Inputs:
# piece_modifiers: list of functions
#       The are executed in order on every new piece. They should handle any piece type and then modify the piece or return a new piece.    
#       Because of the potential for an entirely new piece, create_piece should make a basic piece, the use the following loop
#           for mod in piece_modifiers: new_piece = mod(new_piece)
#           return new_piece
# end turn functions?
# custom? (bool) points (int)
# bug_house (bool)
# crazy_house (bool)
# end_of_turn_func (func)
# start (list of piece inputs)
# Win condition
# Draw move number

# Board: The board is basically the state of the game. It holds both the pieces and the squares so it can be rendered.
#           Includes helper methods for rotation and such
# Controller: How a Game interacts with the board. All game logic is either here or in the pieces. Oblivious to graphics
# Game: Knows all the settings for the game including graphics. Creates board (since it needs to pass on graphics information, which controller is oblivious to)

class GenController: # Todo: Move sprites out of controller (and turnmarker)
    """The controller converts screen events to moves on the board"""
    """Keeps track of turns and win conditions. Handles clicks and events even though it shouldn't"""
    def __init__(self, GUI_sprites, piece_sprites, board, initial_board_state, number_of_players, end_game_condition, moves_needed_for_draw = 50, piece_modifiers = [], end_of_turn_functions = [], custom_start_points = False, bug_house = False, crazy_house = False):
        """
        args:
            GUI_sprites, piece_sprites (Sprite Groups): These are used for piece creation and turn marker creation
            board (Board): This should be a blank board object with the correct dimensions
            initial_board_state (Tuple[Tuples[Piece, int, int, int, str], ...]): Used to set up the board. Inner tuples might look like this: (Pawn, 2, 1, 2, "S").
                The row and col must be in the board, team must be at most the number of players, and the direction must be "N", "S", "E", "W"
            number_of_players (int): Number of players in the game
            end_game_condition (fuction): Takes in a board and determines if the game has ended, and if so, who won
            moves_needed_for_draw (int): Number of king moves before a draw
            piece_modifiers (Sequence[functions, ...]): Each new piece will passed into each of the functions to potentially be modified.
                These functions must all return a piece (whether or not it is the same piece that was passed in)
            end_of_turn_functions (Sequence[functions, ...]): At the end of the turn, each function will be run (in order).
                They should take in a board object and return nothing
            custom_start_points (False or tuple of ints (with len number_of_players)): If it's false, no setup will take place.
                Otherwise, both players will get points to set up their side of the board in addition to the normal setup
            bug_house (bool): Whether or not the game is bug house
            crazy_house (bool): Whether or not the game is crazy house
            """
        self.turn = 1 #1 means white's, 0 for black
        self.board = board
        self.selected_piece = None
        self.selected_pos = None
        self.turn = 0 # 1 for white, 2 for black, 3 for ...
        self.turn_marker = TurnMarker(500, 0, 1, {1: (255, 255, 255), 2: (0, 0, 0)}, GUI_sprites)
                                      
        self.set_up(piece_sprites, initial_board_state)


    def click_responder(self, x, y): # Todo:  or refactor to include fewer references to squares
        """
        Responds to a click at x, y
        
        args:
            x, y (int): position of click on the board"""
        self.board.unhighlight_all_squares() # Anything that's highlighted won't be after a click 
        for sqrx, col in enumerate(self.board.squares): # Redo with better iteration
            for sqry, sqr in enumerate(col):
                if sqr.rect.collidepoint(x,y):
                    piece = self.board.state[sqrx][sqry] # Todo: Add highlighting in
                    if self.selected_piece == None:
                        if piece and piece.team%2 != (self.turn+1)%2 and False:#Todo: Fix later. Remove false for different piece selection
                            break
                        self.selected_piece = piece
                        self.selected_pos = (sqrx, sqry)
                        if self.selected_piece:
                            sqr.highlight()
                            sqrx, sqry = self.board.rotate_coordinates((sqrx, sqry), self.selected_piece.get_rotations()) # Todo: Clean all this up
                            if (piece == self.board.must_move or not self.board.must_move):
                                for move in self.selected_piece.get_legal_moves(self.board.rotate_board(self.selected_piece.get_rotations()), sqrx, sqry): # There's some rotation issue so this should be in board
                                    move = self.board.rotate_coordinates(move, self.selected_piece.get_rotations())
                                    if self.board.state[move[0]][move[1]]: # Todo: Define var for board.state
                                        self.board.squares[move[0]][move[1]].target_highlight()
                                    else:
                                        self.board.squares[move[0]][move[1]].dot_highlight()
                    elif self.selected_piece == piece:
                        self.reset_selection()
                    else: 
                        if self.can_move(self.selected_piece):
                            success, err = self.board.move_piece(self.selected_pos[0], self.selected_pos[1], sqrx, sqry)
                            self.turn += success
                            self.board.render_board()
                            self.reset_selection()
                            self.turn_marker.change_turn((self.turn)%2+1)
                        else:
                            print("Illegal Move")
                            self.reset_selection()

    def end_of_turn(self): #Todo: Implement
        pass

    def reset_selection(self):
        self.selected_piece = None
        self.selected_pos = None

    def can_move(self, piece):
        return self.selected_piece.team == self.turn%2+1 and (piece == self.board.must_move or not self.board.must_move)
    
    #def hightlight_piece(self..... Factoring out code

    def set_up(self, piece_sprites, initial_state):
        """
        Sets up the board with all the pieces in the inputed sprite group
        args:
            piece_sprites (Sprite Group): Sprite group to add the pieces to"""
        for pc in initial_state:
            self.board.create_piece(*pc, piece_sprites)
        
    def undo_last_move(self):
        self.board.unhighlight_all_squares()
        if self.board.undo():
            self.selected_piece = None
            self.selected_pos = None
            self.turn -= 1
        self.board.render_board() # Bring into controller class
        self.turn_marker.change_turn((self.turn)%2+1)

