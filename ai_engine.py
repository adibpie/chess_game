# AI engine for chess game
# Supports both Minimax and Stockfish

import random
import copy
from constants import *

class MinimaxAI:
    def __init__(self, depth=3):
        self.depth = depth
        self.piece_values = {
            'pawn': 100,
            'knight': 320,
            'bishop': 330,
            'rook': 500,
            'queen': 900,
            'king': 20000
        }
    
    def get_move(self, game_state):
        """Get the best move using minimax algorithm"""
        if game_state.turn_step >= 2:  # Black's turn
            best_move = self._minimax(game_state, self.depth, True, float('-inf'), float('inf'))
            if best_move:
                return best_move[1]
        return None
    
    def _minimax(self, state, depth, maximizing, alpha, beta):
        """Minimax algorithm with alpha-beta pruning"""
        if depth == 0 or state.game_over:
            return (self._evaluate(state), None)
        
        if maximizing:  # Black's turn (AI)
            max_eval = float('-inf')
            best_move = None
            moves = self._get_all_moves(state, 'black')
            random.shuffle(moves)  # Add some randomness
            
            for move in moves:
                new_state = self._make_test_move(state, move, 'black')
                if new_state:
                    eval_score = self._minimax(new_state, depth - 1, False, alpha, beta)[0]
                    if eval_score > max_eval:
                        max_eval = eval_score
                        best_move = move
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break  # Alpha-beta pruning
            return (max_eval, best_move)
        else:  # White's turn (opponent)
            min_eval = float('inf')
            best_move = None
            moves = self._get_all_moves(state, 'white')
            
            for move in moves:
                new_state = self._make_test_move(state, move, 'white')
                if new_state:
                    eval_score = self._minimax(new_state, depth - 1, True, alpha, beta)[0]
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_move = move
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break  # Alpha-beta pruning
            return (min_eval, best_move)
    
    def _get_all_moves(self, state, color):
        """Get all possible moves for a color"""
        moves = []
        if color == 'black':
            pieces = state.black_pieces
            locations = state.black_locations
            options = state.black_options
        else:
            pieces = state.white_pieces
            locations = state.white_locations
            options = state.white_options
        
        for i in range(len(pieces)):
            for move in options[i]:
                moves.append((locations[i], move))
        return moves
    
    def _make_test_move(self, state, move, color):
        """Create a test state with a move applied"""
        try:
            new_state = copy.deepcopy(state)
            from_pos, to_pos = move
            
            if color == 'black':
                if from_pos not in new_state.black_locations:
                    return None
                piece_index = new_state.black_locations.index(from_pos)
                new_state.black_locations[piece_index] = to_pos
                new_state.black_moved[piece_index] = True
                
                # Check for captures
                if to_pos in new_state.white_locations:
                    white_piece = new_state.white_locations.index(to_pos)
                    new_state.white_pieces.pop(white_piece)
                    new_state.white_locations.pop(white_piece)
                    new_state.white_moved.pop(white_piece)
                
                new_state.turn_step = 0
            else:
                if from_pos not in new_state.white_locations:
                    return None
                piece_index = new_state.white_locations.index(from_pos)
                new_state.white_locations[piece_index] = to_pos
                new_state.white_moved[piece_index] = True
                
                # Check for captures
                if to_pos in new_state.black_locations:
                    black_piece = new_state.black_locations.index(to_pos)
                    new_state.black_pieces.pop(black_piece)
                    new_state.black_locations.pop(black_piece)
                    new_state.black_moved.pop(black_piece)
                
                new_state.turn_step = 2
            
            # Update options
            new_state._update_options()
            return new_state
        except:
            return None
    
    def _evaluate(self, state):
        """Evaluate the board position"""
        score = 0
        
        # Material evaluation
        for piece in state.white_pieces:
            score += self.piece_values.get(piece, 0)
        for piece in state.black_pieces:
            score -= self.piece_values.get(piece, 0)
        
        # Check for checkmate
        if state.winner == 'white':
            return 100000
        elif state.winner == 'black':
            return -100000
        
        # Position evaluation (simple piece-square tables)
        score += self._position_score(state.white_pieces, state.white_locations, True)
        score -= self._position_score(state.black_pieces, state.black_locations, False)
        
        return score
    
    def _position_score(self, pieces, locations, is_white):
        """Simple position evaluation based on piece placement"""
        score = 0
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        
        for i, piece in enumerate(pieces):
            pos = locations[i]
            # Reward centralization
            if pos in center_squares:
                score += 20
            
            # Piece-specific bonuses
            if piece == 'pawn':
                if is_white:
                    score += (7 - pos[1]) * 5  # Reward advancing pawns
                else:
                    score += pos[1] * 5
            elif piece == 'knight' or piece == 'bishop':
                if pos in center_squares:
                    score += 10
        
        return score


class StockfishAI:
    def __init__(self, skill_level=10):
        """Initialize Stockfish AI"""
        self.skill_level = skill_level
        self.engine = None
        self._init_stockfish()
    
    def _init_stockfish(self):
        """Initialize Stockfish engine"""
        try:
            import chess
            import chess.engine
            
            # Try to find Stockfish
            import subprocess
            import platform
            
            # Common paths for Stockfish
            if platform.system() == 'Windows':
                stockfish_paths = [
                    'stockfish.exe',
                    'C:/stockfish/stockfish.exe',
                    './stockfish.exe'
                ]
            else:
                stockfish_paths = [
                    'stockfish',
                    '/usr/bin/stockfish',
                    '/usr/local/bin/stockfish',
                    './stockfish'
                ]
            
            stockfish_path = None
            for path in stockfish_paths:
                try:
                    result = subprocess.run([path, '--help'], capture_output=True, timeout=1)
                    if result.returncode == 0 or 'Stockfish' in str(result.stderr):
                        stockfish_path = path
                        break
                except:
                    continue
            
            if stockfish_path:
                self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
                # Configure for stronger play
                self.engine.configure({
                    "Skill Level": 20,  # Maximum skill
                    "UCI_LimitStrength": False,
                    "Threads": 4,
                    "Hash": 256
                })
                self.chess_board = chess.Board()
            else:
                print("Stockfish not found. Falling back to minimax.")
                self.engine = None
        except ImportError:
            print("python-chess not installed. Install with: pip install python-chess")
            self.engine = None
        except Exception as e:
            print(f"Error initializing Stockfish: {e}")
            self.engine = None
    
    def get_move(self, game_state):
        """Get move from Stockfish"""
        if not self.engine:
            # Fallback to minimax if Stockfish not available
            minimax = MinimaxAI(depth=3)
            return minimax.get_move(game_state)
        
        if game_state.turn_step >= 2:  # Black's turn
            try:
                # Ensure game state is up to date
                game_state._update_options()
                
                # Convert game state to chess.Board
                board = self._state_to_board(game_state)
                
                # Verify board is valid
                if not board.is_valid():
                    print("Warning: Invalid board state, using minimax fallback")
                    minimax = MinimaxAI(depth=3)
                    return minimax.get_move(game_state)
                
                # Get best move from Stockfish with better time limit and depth
                result = self.engine.play(board, chess.engine.Limit(time=1.5, depth=18))
                move = result.move
                
                # Convert chess.Move to our format
                # chess library: square = row * 8 + col, where row 0 is bottom (a1)
                # Our system: (col, row) where row 0 is top (white pieces)
                from_square = move.from_square
                to_square = move.to_square
                
                # Convert from chess square to our coordinates
                from_col = from_square % 8
                from_row = 7 - (from_square // 8)  # Flip row
                to_col = to_square % 8
                to_row = 7 - (to_square // 8)  # Flip row
                
                from_pos = (from_col, from_row)
                to_pos = (to_col, to_row)
                
                return (from_pos, to_pos)
            except Exception as e:
                print(f"Error getting Stockfish move: {e}")
                import traceback
                traceback.print_exc()
                # Fallback to minimax
                minimax = MinimaxAI(depth=3)
                return minimax.get_move(game_state)
        return None
    
    def _state_to_board(self, game_state):
        """Convert game state to chess.Board"""
        import chess
        
        board = chess.Board()
        board.clear()
        
        # Set up white pieces
        for i, piece in enumerate(game_state.white_pieces):
            if i < len(game_state.white_locations):
                pos = game_state.white_locations[i]
                # Our system: (col, row) where row 0 is top
                # chess: square = row * 8 + col, where row 0 is bottom
                col, row = pos[0], pos[1]
                chess_row = 7 - row  # Flip row coordinate
                square = chess.square(col, chess_row)
                piece_type = self._piece_to_chess_piece(piece, True)
                if piece_type:
                    board.set_piece_at(square, piece_type)
        
        # Set up black pieces
        for i, piece in enumerate(game_state.black_pieces):
            if i < len(game_state.black_locations):
                pos = game_state.black_locations[i]
                col, row = pos[0], pos[1]
                chess_row = 7 - row  # Flip row coordinate
                square = chess.square(col, chess_row)
                piece_type = self._piece_to_chess_piece(piece, False)
                if piece_type:
                    board.set_piece_at(square, piece_type)
        
        # Set turn (0-1 = white, 2-3 = black)
        board.turn = chess.WHITE if game_state.turn_step < 2 else chess.BLACK
        
        # Set castling rights based on moved pieces
        board.castling_rights = chess.BB_ALL
        if game_state.white_moved and len(game_state.white_moved) > 3:
            if game_state.white_moved[3]:  # King moved
                board.castling_rights &= ~chess.BB_RANK_1
            if game_state.white_moved[0]:  # Rook a1 moved
                board.castling_rights &= ~chess.BB_A1
            if game_state.white_moved[7]:  # Rook h1 moved
                board.castling_rights &= ~chess.BB_H1
        if game_state.black_moved and len(game_state.black_moved) > 3:
            if game_state.black_moved[3]:  # King moved
                board.castling_rights &= ~chess.BB_RANK_8
            if game_state.black_moved[0]:  # Rook a8 moved
                board.castling_rights &= ~chess.BB_A8
            if game_state.black_moved[7]:  # Rook h8 moved
                board.castling_rights &= ~chess.BB_H8
        
        return board
    
    def _piece_to_chess_piece(self, piece_name, is_white):
        """Convert piece name to chess.Piece"""
        import chess
        
        piece_map = {
            'pawn': chess.PAWN,
            'rook': chess.ROOK,
            'knight': chess.KNIGHT,
            'bishop': chess.BISHOP,
            'queen': chess.QUEEN,
            'king': chess.KING
        }
        
        color = chess.WHITE if is_white else chess.BLACK
        return chess.Piece(piece_map[piece_name], color)
    
    def __del__(self):
        """Clean up Stockfish engine"""
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass
