'''
CPSC 415 -- Homework #3 support file
Stephen Davies, University of Mary Washington, fall 2017
'''

from collections import UserDict
from copy import deepcopy
import logging

from chess_piece import *

'''A Board object represents the state of a chess board. It is itself a
dictionary that maps locations (in chess notation) to Piece objects; i.e., if
you have an object "my_board", you can say "my_board['C5']" to get the Piece
object that is currently on space C5. (Third column from left, fifth row from
bottom.) You can also use ".items()" in the usual way to iterate through it.

Here are the legal operations you may use on a Board object:
1. Read-only dictionary operations such as [], .get(), .items(), and 
.contains().
2. Calling "deepcopy()" on a Board (from the "copy" module) to clone it.
3. .get_all_available_legal_moves(color)
4. .make_move(original_location, new_location)
5. .get_king_location(color)
6. .is_king_in_check(color)
7. .is_king_in_checkmate(color)

Anything else is considered cheating, and will result in public flogging.
'''
class Board(UserDict):

    def __init__(self):
        super().__init__()
        self.last_side_to_move = 'black'

    '''
    To clone a board so you can investigate what will happen as you make moves
    on it, use "deepcopy()" function:

    from copy import deepcopy
    hypothetical_board = deepcopy(board)
    hypothetical_board.make_move('E2','E4')
    '''

    def get_all_available_legal_moves(self, color):
        '''Returns a list of 2-tuples of strings, containing an original
        square and a destination square, in chess notation (e.g., 'D7'). All
        of these moves are guaranteed to be legal to play.'''
        moves = []
        for loc, piece in self.items():
            if piece.color == color:
                piece_moves = piece._moves_available(loc)
                for curr_loc, new_loc in piece_moves:
                    try:
                        self._assert_legal_move(curr_loc, new_loc)
                        moves.append((curr_loc, new_loc))
                    except:
                        pass
        return moves

    def make_move(self, orig_loc, loc):
        '''Actually make a move on this chess board. Do *not* call this to
        experiment (look ahead) with hypothetical moves. (Use deepcopy() to do
        that; see above.)
        This method raises an exception if you attempt to move illegally.'''
        self._assert_legal_move(orig_loc, loc)
        self[orig_loc]._move_yourself(orig_loc, loc)

    def get_king_location(self, color):
        '''Return the chess notation for the square on which the king of the
        given color rests.'''
        for loc, piece in self.items():
            if isinstance(piece, King) and piece.color==color:
                return loc
        logging.critical('Whoa -- no {} king!'.format(color))

    def is_king_in_check(self, color):
        '''Return True if the player whose color is passed is currently in
        check.'''
        king_loc = self.get_king_location(color)
        return king_loc in [ loc for _,loc in self._get_all_available_moves(
            'white' if color=='black' else 'black')]

    def is_king_in_checkmate(self, color):
        '''"Game over, man."  -- Private Hudson'''
        return self.is_king_in_check(color) and self._no_way_out_of_check(color)

    def _reset(self):
        self.clear()
        for position, notation in cfg.START_POSITION.items():
            self[position] = Piece.from_notation(notation, self)

    def all_occupied_positions(self, color=['white','black']):
        if type(color) != list:
            color = [color]
        return { pos for pos, piece in self.items()
            if piece.color in color }

    def _get_all_available_moves(self, color):
        '''Some of these moves may not be entirely legal (they may place the
        moving player's king in check, for instance.'''
        moves = []
        for loc, piece in self.items():
            if piece.color == color:
                moves.extend(piece._moves_available(loc))
        return moves

    def _no_way_out_of_check(self, color):
        for orig_loc, loc in self._get_all_available_moves(color):
            modified_model = deepcopy(self)
            modified_model[loc] = modified_model.pop(orig_loc)
            if not modified_model.is_king_in_check(color):
                return False
        return True

    def _is_stalemated(self, color):
        return (not self.is_king_in_check(color) and 
            self._no_way_out_of_check(color))

    def _assert_legal_move(self, orig_loc, loc):
        piece = self[orig_loc]
        if orig_loc == loc:
            # False alarm. They must have put the piece down on the same
            # square. Throw an exception so this isn't registered as a move
            # in the game, but don't give it any message to display.
            raise IllegalMoveException('')
        if loc in [ l for _,l in piece._moves_available(orig_loc) ]:
            modified_model = deepcopy(self)
            modified_model[loc] = modified_model.pop(orig_loc)
            if modified_model.is_king_in_check(piece.color):
                if self.is_king_in_check(piece.color):
                    raise IllegalMoveException("You're in check, bruh!")
                else:
                    raise IllegalMoveException(
                        'That would put your king in check!')
            return
        raise IllegalMoveException("Can't move there, bruh!")

class IllegalMoveException(Exception):
    pass


class Game():

    def __init__(self):
        super().__init__()
        self.player_turn = ''  # hack
        self.board = Board()

    def _reset(self):
        self.captured_pieces = { 'white': [], 'black': [] }
        self.player_turn = 'white'
        self.started = True
        self.board._reset()



# Using the module as a 'singleton.'
game = Game()
