# AI engine for chess game
# Supports both Minimax and Stockfish

import random
import copy
from constants import *

class MinimaxAI:
    def __init__(self, depth=3):
        self.depth = depth
        # Improved piece values (standard chess values)
        self.piece_values = {
            'pawn': 100,
            'knight': 320,
            'bishop': 330,
            'rook': 500,
            'queen': 900,
            'king': 20000
        }
        
        # Piece-square tables for positional evaluation
        self.pawn_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]
        
        self.knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
        
        self.bishop_table = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ]
        
        self.rook_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [0,  0,  0,  5,  5,  0,  0,  0]
        ]
        
        self.queen_table = [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [-5,  0,  5,  5,  5,  5,  0, -5],
            [0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ]
        
        self.king_table = [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [20, 20,  0,  0,  0,  0, 20, 20],
            [20, 30, 10,  0,  0, 10, 30, 20]
        ]
    
    def get_move(self, game_state):
        """Get the best move using minimax algorithm"""
        if game_state.turn_step >= 2:  # Black's turn
            best_move = self._minimax(game_state, self.depth, True, float('-inf'), float('inf'))
            if best_move:
                return best_move[1]
        return None
    
    def _minimax(self, state, depth, maximizing, alpha, beta):
        """Minimax algorithm with alpha-beta pruning and move ordering"""
        if depth == 0 or state.game_over:
            return (self._evaluate(state), None)
        
        if maximizing:  # Black's turn (AI)
            max_eval = float('-inf')
            best_move = None
            moves = self._get_all_moves(state, 'black')
            
            # Move ordering: prioritize captures and checks
            moves = self._order_moves(state, moves, 'black')
            
            for move in moves:
                new_state = self._make_test_move(state, move, 'black')
                if new_state:
                    # Quiescence search for captures at leaf nodes
                    if depth == 1:
                        eval_score = self._quiescence(new_state, alpha, beta, False)
                    else:
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
            
            # Move ordering
            moves = self._order_moves(state, moves, 'white')
            
            for move in moves:
                new_state = self._make_test_move(state, move, 'white')
                if new_state:
                    if depth == 1:
                        eval_score = self._quiescence(new_state, alpha, beta, True)
                    else:
                        eval_score = self._minimax(new_state, depth - 1, True, alpha, beta)[0]
                    
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_move = move
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break  # Alpha-beta pruning
            return (min_eval, best_move)
    
    def _quiescence(self, state, alpha, beta, maximizing):
        """Quiescence search for captures"""
        stand_pat = self._evaluate(state)
        
        if maximizing:
            if stand_pat >= beta:
                return beta
            if alpha < stand_pat:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if beta > stand_pat:
                beta = stand_pat
        
        # Only search captures
        moves = self._get_capture_moves(state, 'black' if maximizing else 'white')
        moves = self._order_moves(state, moves, 'black' if maximizing else 'white')
        
        for move in moves[:5]:  # Limit to top 5 captures
            new_state = self._make_test_move(state, move, 'black' if maximizing else 'white')
            if new_state:
                score = self._quiescence(new_state, alpha, beta, not maximizing)
                if maximizing:
                    if score >= beta:
                        return beta
                    if score > alpha:
                        alpha = score
                else:
                    if score <= alpha:
                        return alpha
                    if score < beta:
                        beta = score
        
        return alpha if maximizing else beta
    
    def _get_capture_moves(self, state, color):
        """Get only capture moves"""
        moves = []
        if color == 'black':
            pieces = state.black_pieces
            locations = state.black_locations
            options = state.black_options
            enemy_locations = state.white_locations
        else:
            pieces = state.white_pieces
            locations = state.white_locations
            options = state.white_options
            enemy_locations = state.black_locations
        
        for i in range(len(pieces)):
            for move in options[i]:
                if move in enemy_locations:
                    moves.append((locations[i], move))
        return moves
    
    def _order_moves(self, state, moves, color):
        """Order moves by priority (captures first, then by piece value)"""
        def move_priority(move):
            from_pos, to_pos = move
            priority = 0
            
            # Check if it's a capture
            if color == 'black':
                if to_pos in state.white_locations:
                    captured_idx = state.white_locations.index(to_pos)
                    captured_piece = state.white_pieces[captured_idx]
                    priority += self.piece_values.get(captured_piece, 0)
            else:
                if to_pos in state.black_locations:
                    captured_idx = state.black_locations.index(to_pos)
                    captured_piece = state.black_pieces[captured_idx]
                    priority += self.piece_values.get(captured_piece, 0)
            
            # Check piece value (prefer moving valuable pieces)
            if color == 'black':
                if from_pos in state.black_locations:
                    piece_idx = state.black_locations.index(from_pos)
                    piece = state.black_pieces[piece_idx]
                    priority += self.piece_values.get(piece, 0) // 10
            else:
                if from_pos in state.white_locations:
                    piece_idx = state.white_locations.index(from_pos)
                    piece = state.white_pieces[piece_idx]
                    priority += self.piece_values.get(piece, 0) // 10
            
            return priority
        
        moves.sort(key=move_priority, reverse=True)
        return moves
    
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
        """Evaluate the board position with advanced heuristics"""
        score = 0
        
        # Check for checkmate
        if state.winner == 'white':
            return 100000
        elif state.winner == 'black':
            return -100000
        
        # Material evaluation
        white_material = sum(self.piece_values.get(piece, 0) for piece in state.white_pieces)
        black_material = sum(self.piece_values.get(piece, 0) for piece in state.black_pieces)
        score += white_material - black_material
        
        # Position evaluation using piece-square tables
        score += self._position_score(state.white_pieces, state.white_locations, True)
        score -= self._position_score(state.black_pieces, state.black_locations, False)
        
        # Mobility (number of legal moves)
        white_mobility = sum(len(moves) for moves in state.white_options)
        black_mobility = sum(len(moves) for moves in state.black_options)
        score += (white_mobility - black_mobility) * 2
        
        # King safety
        score += self._king_safety(state, True) - self._king_safety(state, False)
        
        # Pawn structure
        score += self._pawn_structure(state, True) - self._pawn_structure(state, False)
        
        return score
    
    def _position_score(self, pieces, locations, is_white):
        """Position evaluation using piece-square tables"""
        score = 0
        
        for i, piece in enumerate(pieces):
            if i >= len(locations):
                continue
            col, row = locations[i]
            
            # Flip table for black pieces
            table_row = row if is_white else 7 - row
            
            if piece == 'pawn':
                score += self.pawn_table[table_row][col]
            elif piece == 'knight':
                score += self.knight_table[table_row][col]
            elif piece == 'bishop':
                score += self.bishop_table[table_row][col]
            elif piece == 'rook':
                score += self.rook_table[table_row][col]
            elif piece == 'queen':
                score += self.queen_table[table_row][col]
            elif piece == 'king':
                score += self.king_table[table_row][col]
        
        return score
    
    def _king_safety(self, state, is_white):
        """Evaluate king safety"""
        score = 0
        if is_white:
            if 'king' in state.white_pieces:
                king_idx = state.white_pieces.index('king')
                king_pos = state.white_locations[king_idx]
                # Check if king is in check
                for moves in state.black_options:
                    if king_pos in moves:
                        score -= 50  # Penalty for being in check
        else:
            if 'king' in state.black_pieces:
                king_idx = state.black_pieces.index('king')
                king_pos = state.black_locations[king_idx]
                for moves in state.white_options:
                    if king_pos in moves:
                        score -= 50
        return score
    
    def _pawn_structure(self, state, is_white):
        """Evaluate pawn structure"""
        score = 0
        pawns = state.white_pieces if is_white else state.black_pieces
        locations = state.white_locations if is_white else state.black_locations
        
        pawn_locations = [locations[i] for i, p in enumerate(pawns) if p == 'pawn']
        
        # Doubled pawns (penalty)
        cols = [loc[0] for loc in pawn_locations]
        for col in set(cols):
            if cols.count(col) > 1:
                score -= 20 * (cols.count(col) - 1)
        
        # Isolated pawns (penalty)
        for col, row in pawn_locations:
            has_neighbor = False
            for c, r in pawn_locations:
                if abs(c - col) == 1:
                    has_neighbor = True
                    break
            if not has_neighbor:
                score -= 15
        
        # Passed pawns (bonus)
        for col, row in pawn_locations:
            is_passed = True
            enemy_pawns = state.black_locations if is_white else state.white_locations
            enemy_pawn_pieces = state.black_pieces if is_white else state.white_pieces
            
            for i, piece in enumerate(enemy_pawn_pieces):
                if piece == 'pawn':
                    e_col, e_row = enemy_pawns[i]
                    if abs(e_col - col) <= 1 and ((is_white and e_row > row) or (not is_white and e_row < row)):
                        is_passed = False
                        break
            
            if is_passed:
                score += 30
        
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
            import os
            
            # Common paths for Stockfish
            if platform.system() == 'Windows':
                stockfish_paths = [
                    'stockfish.exe',
                    './stockfish.exe',
                    os.path.join(os.getcwd(), 'stockfish.exe'),
                    'C:/stockfish/stockfish.exe',
                    os.path.expanduser('~/stockfish.exe')
                ]
            else:
                stockfish_paths = [
                    'stockfish',
                    './stockfish',
                    '/usr/bin/stockfish',
                    '/usr/local/bin/stockfish',
                    '/opt/homebrew/bin/stockfish'  # macOS Apple Silicon
                ]
            
            stockfish_path = None
            for path in stockfish_paths:
                try:
                    # Check if file exists
                    if not os.path.exists(path):
                        continue
                    # Try to run it
                    result = subprocess.run([path, '--help'], capture_output=True, timeout=2)
                    if result.returncode == 0 or 'Stockfish' in str(result.stderr) or 'Stockfish' in str(result.stdout):
                        stockfish_path = path
                        print(f"Found Stockfish at: {path}")
                        break
                except Exception as e:
                    continue
            
            if stockfish_path:
                try:
                    self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
                    # Configure for maximum strength
                    self.engine.configure({
                        "Skill Level": 20,  # Maximum skill (0-20)
                        "UCI_LimitStrength": False,
                        "Threads": 4,
                        "Hash": 512,  # More hash for better play
                        "MultiPV": 1,
                        "Contempt": 0
                    })
                    self.chess_board = chess.Board()
                    print("Stockfish engine initialized successfully!")
                except Exception as e:
                    print(f"Error starting Stockfish engine: {e}")
                    self.engine = None
            else:
                print("Stockfish not found. Attempting to download...")
                # Try to download Stockfish
                try:
                    from install_stockfish import install_stockfish
                    downloaded_path = install_stockfish()
                    if downloaded_path and os.path.exists(downloaded_path):
                        self.engine = chess.engine.SimpleEngine.popen_uci(downloaded_path)
                        self.engine.configure({
                            "Skill Level": 20,
                            "UCI_LimitStrength": False,
                            "Threads": 4,
                            "Hash": 512
                        })
                        self.chess_board = chess.Board()
                        print("Stockfish downloaded and initialized!")
                    else:
                        print("Could not download Stockfish. Falling back to minimax.")
                        self.engine = None
                except Exception as e:
                    print(f"Could not download Stockfish: {e}")
                    print("Please download Stockfish manually from: https://stockfishchess.org/download/")
                    print("Or install via package manager.")
                    self.engine = None
        except ImportError:
            print("python-chess not installed. Install with: pip install python-chess")
            self.engine = None
        except Exception as e:
            print(f"Error initializing Stockfish: {e}")
            import traceback
            traceback.print_exc()
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
                
                # Get best move from Stockfish with maximum strength
                # Use both time and depth limits for best play
                result = self.engine.play(board, chess.engine.Limit(time=2.0, depth=20))
                move = result.move
                
                # Log the move for debugging
                print(f"Stockfish move: {move} (from {move.from_square} to {move.to_square})")
                
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
