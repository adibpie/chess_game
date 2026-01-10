# Core chess game logic (framework-agnostic)
from constants import *

# These will be set by additions.py to avoid circular imports
check_options = None
check_ep = None

def set_move_functions(options_func, ep_func):
    """Set the move checking functions from additions.py"""
    global check_options, check_ep
    check_options = options_func
    check_ep = ep_func

class GameState:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        self.white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                            'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
        self.white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                               (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
        self.black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                            'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
        self.black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                               (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
        self.white_moved = [False] * 16
        self.black_moved = [False] * 16
        self.captured_pieces_white = []
        self.captured_pieces_black = []
        self.turn_step = 0
        self.selection = 100
        self.valid_moves = []
        self.white_ep = (100, 100)
        self.black_ep = (100, 100)
        self.white_promote = False
        self.black_promote = False
        self.promo_index = 100
        self.check = False
        self.castling_moves = []
        self.winner = ''
        self.game_over = False
        self.white_options = []
        self.black_options = []
        self.selected_piece = None
        self._update_options()
    
    def _update_options(self):
        if check_options:
            # Store current state temporarily for move checking functions
            # The check_options function uses global variables from additions.py
            # We need to update those before calling check_options
            self.white_options = check_options(self.white_pieces, self.white_locations, 'white')
            self.black_options = check_options(self.black_pieces, self.black_locations, 'black')
        else:
            self.white_options = []
            self.black_options = []
    
    def get_board_state(self):
        """Return serializable board state for online play"""
        return {
            'whitePieces': self.white_pieces.copy(),
            'whiteLocations': [[loc[0], loc[1]] for loc in self.white_locations],
            'blackPieces': self.black_pieces.copy(),
            'blackLocations': [[loc[0], loc[1]] for loc in self.black_locations],
            'capturedPiecesWhite': self.captured_pieces_white.copy(),
            'capturedPiecesBlack': self.captured_pieces_black.copy(),
            'turnStep': self.turn_step,
            'whiteEp': list(self.white_ep) if self.white_ep != (100, 100) else [100, 100],
            'blackEp': list(self.black_ep) if self.black_ep != (100, 100) else [100, 100],
            'winner': self.winner,
            'gameOver': self.game_over
        }
    
    def load_board_state(self, state):
        """Load board state from serialized data"""
        # Handle both old and new format
        if 'whitePieces' in state:
            self.white_pieces = state['whitePieces']
            self.white_locations = [tuple(loc) for loc in state['whiteLocations']]
            self.black_pieces = state['blackPieces']
            self.black_locations = [tuple(loc) for loc in state['blackLocations']]
            self.captured_pieces_white = state.get('capturedPiecesWhite', [])
            self.captured_pieces_black = state.get('capturedPiecesBlack', [])
            self.turn_step = state.get('turnStep', 0)
            self.white_ep = tuple(state.get('whiteEp', [100, 100]))
            self.black_ep = tuple(state.get('blackEp', [100, 100]))
            self.winner = state.get('winner', '')
            self.game_over = state.get('gameOver', False)
        else:
            # Old format compatibility
            self.white_pieces = state.get('white_pieces', state.get('whitePieces', []))
            self.white_locations = [tuple(loc) if isinstance(loc, list) else loc for loc in state.get('white_locations', state.get('whiteLocations', []))]
            self.black_pieces = state.get('black_pieces', state.get('blackPieces', []))
            self.black_locations = [tuple(loc) if isinstance(loc, list) else loc for loc in state.get('black_locations', state.get('blackLocations', []))]
            self.captured_pieces_white = state.get('captured_pieces_white', state.get('capturedPiecesWhite', []))
            self.captured_pieces_black = state.get('captured_pieces_black', state.get('capturedPiecesBlack', []))
            self.turn_step = state.get('turn_step', state.get('turnStep', 0))
            self.white_ep = tuple(state.get('white_ep', state.get('whiteEp', [100, 100]))) if isinstance(state.get('white_ep', state.get('whiteEp', [100, 100])), list) else state.get('white_ep', state.get('whiteEp', (100, 100)))
            self.black_ep = tuple(state.get('black_ep', state.get('blackEp', [100, 100]))) if isinstance(state.get('black_ep', state.get('blackEp', [100, 100])), list) else state.get('black_ep', state.get('blackEp', (100, 100)))
            self.winner = state.get('winner', '')
            self.game_over = state.get('game_over', state.get('gameOver', False))
        self._update_options()
    
    def make_move(self, from_pos, to_pos, promotion_piece=None):
        """Make a move and return True if successful"""
        if self.game_over:
            return False
        
        # Determine which player is moving
        if self.turn_step < 2:
            if from_pos not in self.white_locations:
                return False
            piece_index = self.white_locations.index(from_pos)
            piece = self.white_pieces[piece_index]
            
            # Check if move is valid
            valid_moves = self.white_options[piece_index]
            if to_pos not in valid_moves:
                # Check castling
                if piece == 'king':
                    for castle_move in self.castling_moves:
                        if to_pos == castle_move[0]:
                            return self._execute_castle(True, castle_move)
                return False
            
            # Execute move
            self._execute_white_move(piece_index, to_pos)
            return True
        else:
            if from_pos not in self.black_locations:
                return False
            piece_index = self.black_locations.index(from_pos)
            piece = self.black_pieces[piece_index]
            
            # Check if move is valid
            valid_moves = self.black_options[piece_index]
            if to_pos not in valid_moves:
                # Check castling
                if piece == 'king':
                    for castle_move in self.castling_moves:
                        if to_pos == castle_move[0]:
                            return self._execute_castle(False, castle_move)
                return False
            
            # Execute move
            self._execute_black_move(piece_index, to_pos)
            return True
    
    def _execute_white_move(self, piece_index, to_pos):
        from_pos = self.white_locations[piece_index]
        if check_ep:
            self.white_ep = check_ep(from_pos, to_pos)
        else:
            self.white_ep = (100, 100)
        self.white_locations[piece_index] = to_pos
        self.white_moved[piece_index] = True
        
        # Check for captures
        if to_pos in self.black_locations:
            black_piece = self.black_locations.index(to_pos)
            self.captured_pieces_white.append(self.black_pieces[black_piece])
            if self.black_pieces[black_piece] == 'king':
                self.winner = 'white'
            self.black_pieces.pop(black_piece)
            self.black_locations.pop(black_piece)
            self.black_moved.pop(black_piece)
        
        # Check en passant
        if to_pos == self.black_ep:
            black_piece = self.black_locations.index((self.black_ep[0], self.black_ep[1] - 1))
            self.captured_pieces_white.append(self.black_pieces[black_piece])
            self.black_pieces.pop(black_piece)
            self.black_locations.pop(black_piece)
            self.black_moved.pop(black_piece)
        
        self._update_options()
        self.turn_step = 2
        self.selection = 100
        self.valid_moves = []
    
    def _execute_black_move(self, piece_index, to_pos):
        from_pos = self.black_locations[piece_index]
        if check_ep:
            self.black_ep = check_ep(from_pos, to_pos)
        else:
            self.black_ep = (100, 100)
        self.black_locations[piece_index] = to_pos
        self.black_moved[piece_index] = True
        
        # Check for captures
        if to_pos in self.white_locations:
            white_piece = self.white_locations.index(to_pos)
            self.captured_pieces_black.append(self.white_pieces[white_piece])
            if self.white_pieces[white_piece] == 'king':
                self.winner = 'black'
            self.white_pieces.pop(white_piece)
            self.white_locations.pop(white_piece)
            self.white_moved.pop(white_piece)
        
        # Check en passant
        if to_pos == self.white_ep:
            white_piece = self.white_locations.index((self.white_ep[0], self.white_ep[1] + 1))
            self.captured_pieces_black.append(self.white_pieces[white_piece])
            self.white_pieces.pop(white_piece)
            self.white_locations.pop(white_piece)
            self.white_moved.pop(white_piece)
        
        self._update_options()
        self.turn_step = 0
        self.selection = 100
        self.valid_moves = []
    
    def _execute_castle(self, is_white, castle_move):
        if is_white:
            piece_index = self.white_locations.index((3, 0)) if (3, 0) in self.white_locations else None
            if piece_index is None:
                return False
            self.white_locations[piece_index] = castle_move[0]
            self.white_moved[piece_index] = True
            if castle_move[0] == (1, 0):
                rook_coords = (0, 0)
            else:
                rook_coords = (7, 0)
            rook_index = self.white_locations.index(rook_coords)
            self.white_locations[rook_index] = castle_move[1]
        else:
            piece_index = self.black_locations.index((3, 7)) if (3, 7) in self.black_locations else None
            if piece_index is None:
                return False
            self.black_locations[piece_index] = castle_move[0]
            self.black_moved[piece_index] = True
            if castle_move[0] == (1, 7):
                rook_coords = (0, 7)
            else:
                rook_coords = (7, 7)
            rook_index = self.black_locations.index(rook_coords)
            self.black_locations[rook_index] = castle_move[1]
        
        self._update_options()
        if is_white:
            self.turn_step = 2
        else:
            self.turn_step = 0
        self.selection = 100
        self.valid_moves = []
        return True
    
    def check_promotion(self):
        self.white_promote = False
        self.black_promote = False
        self.promo_index = 100
        
        for i in range(len(self.white_pieces)):
            if self.white_pieces[i] == 'pawn' and self.white_locations[i][1] == 7:
                self.white_promote = True
                self.promo_index = i
                return
        
        for i in range(len(self.black_pieces)):
            if self.black_pieces[i] == 'pawn' and self.black_locations[i][1] == 0:
                self.black_promote = True
                self.promo_index = i
                return
    
    def promote_pawn(self, piece_type):
        if self.white_promote and self.promo_index < len(self.white_pieces):
            self.white_pieces[self.promo_index] = piece_type
            self.white_promote = False
        elif self.black_promote and self.promo_index < len(self.black_pieces):
            self.black_pieces[self.promo_index] = piece_type
            self.black_promote = False
        self._update_options()

# Note: check_options and check_ep functions are defined in additions.py
# They will be imported when needed
