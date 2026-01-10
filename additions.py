# two player chess in python with Pygame!
# pawn double space checking
# castling
# en passant
# pawn promotion
# Enhanced with menu system and multiple game modes

import pygame
from constants import *
from menu import Menu
from game_logic import GameState, set_move_functions
import sys

pygame.init()

# Global game state
game_state = GameState()
menu = Menu()
current_mode = None
ai_opponent = None
online_client = None

# Set move functions in game_logic to avoid circular imports
def _setup_game_logic():
    set_move_functions(check_options, check_ep)

# Make these accessible for move checking functions
white_pieces = game_state.white_pieces
white_locations = game_state.white_locations
black_pieces = game_state.black_pieces
black_locations = game_state.black_locations
white_moved = game_state.white_moved
black_moved = game_state.black_moved
captured_pieces_white = game_state.captured_pieces_white
captured_pieces_black = game_state.captured_pieces_black
turn_step = game_state.turn_step
selection = game_state.selection
valid_moves = game_state.valid_moves
white_ep = game_state.white_ep
black_ep = game_state.black_ep
white_promote = game_state.white_promote
black_promote = game_state.black_promote
promo_index = game_state.promo_index
check = game_state.check
castling_moves = game_state.castling_moves
winner = game_state.winner
game_over = game_state.game_over
white_options = game_state.white_options
black_options = game_state.black_options
selected_piece = game_state.selected_piece

def sync_globals():
    """Sync global variables with game_state"""
    global white_pieces, white_locations, black_pieces, black_locations
    global white_moved, black_moved, captured_pieces_white, captured_pieces_black
    global turn_step, selection, valid_moves, white_ep, black_ep
    global white_promote, black_promote, promo_index, check, castling_moves
    global winner, game_over, white_options, black_options, selected_piece
    
    white_pieces = game_state.white_pieces
    white_locations = game_state.white_locations
    black_pieces = game_state.black_pieces
    black_locations = game_state.black_locations
    white_moved = game_state.white_moved
    black_moved = game_state.black_moved
    captured_pieces_white = game_state.captured_pieces_white
    captured_pieces_black = game_state.captured_pieces_black
    turn_step = game_state.turn_step
    selection = game_state.selection
    valid_moves = game_state.valid_moves
    white_ep = game_state.white_ep
    black_ep = game_state.black_ep
    white_promote = game_state.white_promote
    black_promote = game_state.black_promote
    promo_index = game_state.promo_index
    check = game_state.check
    castling_moves = game_state.castling_moves
    winner = game_state.winner
    game_over = game_state.game_over
    white_options = game_state.white_options
    black_options = game_state.black_options
    selected_piece = game_state.selected_piece
    
    # Update game_state options after syncing globals (needed for move checking)
    game_state._update_options()
    white_options = game_state.white_options
    black_options = game_state.black_options

# draw main game board
def draw_board():
    for i in range(32):
        column = i % 4
        row = i // 4
        if row % 2 == 0:
            pygame.draw.rect(screen, 'light gray', [600 - (column * 200), row * 100, 100, 100])
        else:
            pygame.draw.rect(screen, 'light gray', [700 - (column * 200), row * 100, 100, 100])
        pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
        pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
        pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)
        # Show AI thinking status
        if current_mode == GAME_MODE_AI and hasattr(game_state, 'ai_thinking') and game_state.ai_thinking:
            status_text = 'Black is deciding the move...'
            screen.blit(big_font.render(status_text, True, 'black'), (20, 820))
        else:
            status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
                           'Black: Select a Piece to Move!', 'Black: Select a Destination!']
            screen.blit(big_font.render(status_text[turn_step], True, 'black'), (20, 820))
        for i in range(9):
            pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
            pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)
        screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))
        if white_promote or black_promote:
            pygame.draw.rect(screen, 'gray', [0, 800, WIDTH - 200, 100])
            pygame.draw.rect(screen, 'gold', [0, 800, WIDTH - 200, 100], 5)
            screen.blit(big_font.render('Select Piece to Promote Pawn', True, 'black'), (20, 820))


# draw pieces onto board
def draw_pieces():
    for i in range(len(white_pieces)):
        index = piece_list.index(white_pieces[i])
        if white_pieces[i] == 'pawn':
            screen.blit(white_pawn, (white_locations[i][0] * 100 + 22, white_locations[i][1] * 100 + 30))
        else:
            screen.blit(white_images[index], (white_locations[i][0] * 100 + 10, white_locations[i][1] * 100 + 10))
        if turn_step < 2:
            if selection == i:
                pygame.draw.rect(screen, 'red', [white_locations[i][0] * 100 + 1, white_locations[i][1] * 100 + 1,
                                                 100, 100], 2)

    for i in range(len(black_pieces)):
        index = piece_list.index(black_pieces[i])
        if black_pieces[i] == 'pawn':
            screen.blit(black_pawn, (black_locations[i][0] * 100 + 22, black_locations[i][1] * 100 + 30))
        else:
            screen.blit(black_images[index], (black_locations[i][0] * 100 + 10, black_locations[i][1] * 100 + 10))
        if turn_step >= 2:
            if selection == i:
                pygame.draw.rect(screen, 'blue', [black_locations[i][0] * 100 + 1, black_locations[i][1] * 100 + 1,
                                                  100, 100], 2)


# function to check all pieces valid options on board
def check_options(pieces, locations, turn):
    global castling_moves
    moves_list = []
    all_moves_list = []
    castling_moves = []
    for i in range((len(pieces))):
        location = locations[i]
        piece = pieces[i]
        if piece == 'pawn':
            moves_list = check_pawn(location, turn)
        elif piece == 'rook':
            moves_list = check_rook(location, turn)
        elif piece == 'knight':
            moves_list = check_knight(location, turn)
        elif piece == 'bishop':
            moves_list = check_bishop(location, turn)
        elif piece == 'queen':
            moves_list = check_queen(location, turn)
        elif piece == 'king':
            moves_list, castling_moves = check_king(location, turn)
        all_moves_list.append(moves_list)
    return all_moves_list


# check king valid moves
def check_king(position, color):
    moves_list = []
    castle_moves = check_castling()
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    # 8 squares to check for kings, they can go one square any direction
    targets = [(1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list, castle_moves


# check queen valid moves
def check_queen(position, color):
    moves_list = check_bishop(position, color)
    second_list = check_rook(position, color)
    for i in range(len(second_list)):
        moves_list.append(second_list[i])
    return moves_list


# check bishop moves
def check_bishop(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    for i in range(4):  # up-right, up-left, down-right, down-left
        path = True
        chain = 1
        if i == 0:
            x = 1
            y = -1
        elif i == 1:
            x = -1
            y = -1
        elif i == 2:
            x = 1
            y = 1
        else:
            x = -1
            y = 1
        while path:
            if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                    0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                moves_list.append((position[0] + (chain * x), position[1] + (chain * y)))
                if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                    path = False
                chain += 1
            else:
                path = False
    return moves_list


# check rook moves
def check_rook(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    for i in range(4):  # down, up, right, left
        path = True
        chain = 1
        if i == 0:
            x = 0
            y = 1
        elif i == 1:
            x = 0
            y = -1
        elif i == 2:
            x = 1
            y = 0
        else:
            x = -1
            y = 0
        while path:
            if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                    0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                moves_list.append((position[0] + (chain * x), position[1] + (chain * y)))
                if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                    path = False
                chain += 1
            else:
                path = False
    return moves_list


# check valid pawn moves
def check_pawn(position, color):
    moves_list = []
    if color == 'white':
        if (position[0], position[1] + 1) not in white_locations and \
                (position[0], position[1] + 1) not in black_locations and position[1] < 7:
            moves_list.append((position[0], position[1] + 1))
            # indent the check for two spaces ahead, so it is only checked if one space ahead is also open
            if (position[0], position[1] + 2) not in white_locations and \
                    (position[0], position[1] + 2) not in black_locations and position[1] == 1:
                moves_list.append((position[0], position[1] + 2))
        if (position[0] + 1, position[1] + 1) in black_locations:
            moves_list.append((position[0] + 1, position[1] + 1))
        if (position[0] - 1, position[1] + 1) in black_locations:
            moves_list.append((position[0] - 1, position[1] + 1))
        # add en passant move checker
        if (position[0] + 1, position[1] + 1) == black_ep:
            moves_list.append((position[0] + 1, position[1] + 1))
        if (position[0] - 1, position[1] + 1) == black_ep:
            moves_list.append((position[0] - 1, position[1] + 1))
    else:
        if (position[0], position[1] - 1) not in white_locations and \
                (position[0], position[1] - 1) not in black_locations and position[1] > 0:
            moves_list.append((position[0], position[1] - 1))
            # indent the check for two spaces ahead, so it is only checked if one space ahead is also open
            if (position[0], position[1] - 2) not in white_locations and \
                    (position[0], position[1] - 2) not in black_locations and position[1] == 6:
                moves_list.append((position[0], position[1] - 2))
        if (position[0] + 1, position[1] - 1) in white_locations:
            moves_list.append((position[0] + 1, position[1] - 1))
        if (position[0] - 1, position[1] - 1) in white_locations:
            moves_list.append((position[0] - 1, position[1] - 1))
        # add en passant move checker
        if (position[0] + 1, position[1] - 1) == white_ep:
            moves_list.append((position[0] + 1, position[1] - 1))
        if (position[0] - 1, position[1] - 1) == white_ep:
            moves_list.append((position[0] - 1, position[1] - 1))
    return moves_list


# check valid knight moves
def check_knight(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    # 8 squares to check for knights, they can go two squares in one direction and one in another
    targets = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list


# check for valid moves for just selected piece
def check_valid_moves():
    if turn_step < 2:
        options_list = white_options
    else:
        options_list = black_options
    valid_options = options_list[selection]
    return valid_options


# draw valid moves on screen
def draw_valid(moves):
    if turn_step < 2:
        color = 'red'
    else:
        color = 'blue'
    for i in range(len(moves)):
        pygame.draw.circle(screen, color, (moves[i][0] * 100 + 50, moves[i][1] * 100 + 50), 5)


# draw captured pieces on side of screen
def draw_captured():
    for i in range(len(captured_pieces_white)):
        captured_piece = captured_pieces_white[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_black_images[index], (825, 5 + 50 * i))
    for i in range(len(captured_pieces_black)):
        captured_piece = captured_pieces_black[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_white_images[index], (925, 5 + 50 * i))


# draw a flashing square around king if in check
def draw_check():
    global check
    check = False
    if turn_step < 2:
        if 'king' in white_pieces:
            king_index = white_pieces.index('king')
            king_location = white_locations[king_index]
            for i in range(len(black_options)):
                if king_location in black_options[i]:
                    check = True
                    if counter < 15:
                        pygame.draw.rect(screen, 'dark red', [white_locations[king_index][0] * 100 + 1,
                                                              white_locations[king_index][1] * 100 + 1, 100, 100], 5)
    else:
        if 'king' in black_pieces:
            king_index = black_pieces.index('king')
            king_location = black_locations[king_index]
            for i in range(len(white_options)):
                if king_location in white_options[i]:
                    check = True
                    if counter < 15:
                        pygame.draw.rect(screen, 'dark blue', [black_locations[king_index][0] * 100 + 1,
                                                               black_locations[king_index][1] * 100 + 1, 100, 100], 5)


def draw_game_over():
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])
    screen.blit(font.render(f'{winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render(f'Press ENTER to Restart!', True, 'white'), (210, 240))


# check en passant because people on the internet won't stop bugging me for it
def check_ep(old_coords, new_coords):
    if turn_step <= 1:
        index = white_locations.index(old_coords)
        ep_coords = (new_coords[0], new_coords[1] - 1)
        piece = white_pieces[index]
    else:
        index = black_locations.index(old_coords)
        ep_coords = (new_coords[0], new_coords[1] + 1)
        piece = black_pieces[index]
    if piece == 'pawn' and abs(old_coords[1] - new_coords[1]) > 1:
        # if piece was pawn and moved two spaces, return EP coords as defined above
        pass
    else:
        ep_coords = (100, 100)
    return ep_coords


# add castling
def check_castling():
    # king must not currently be in check, neither the rook nor king has moved previously, nothing between
    # and the king does not pass through or finish on an attacked piece
    castle_moves = []  # store each valid castle move as [((king_coords), (castle_coords))]
    rook_indexes = []
    rook_locations = []
    king_index = 0
    king_pos = (0, 0)
    if turn_step > 1:
        for i in range(len(white_pieces)):
            if white_pieces[i] == 'rook':
                rook_indexes.append(white_moved[i])
                rook_locations.append(white_locations[i])
            if white_pieces[i] == 'king':
                king_index = i
                king_pos = white_locations[i]
        if not white_moved[king_index] and False in rook_indexes and not check:
            for i in range(len(rook_indexes)):
                castle = True
                if rook_locations[i][0] > king_pos[0]:
                    empty_squares = [(king_pos[0] + 1, king_pos[1]), (king_pos[0] + 2, king_pos[1]),
                                     (king_pos[0] + 3, king_pos[1])]
                else:
                    empty_squares = [(king_pos[0] - 1, king_pos[1]), (king_pos[0] - 2, king_pos[1])]
                for j in range(len(empty_squares)):
                    if empty_squares[j] in white_locations or empty_squares[j] in black_locations or \
                            empty_squares[j] in black_options or rook_indexes[i]:
                        castle = False
                if castle:
                    castle_moves.append((empty_squares[1], empty_squares[0]))
    else:
        for i in range(len(black_pieces)):
            if black_pieces[i] == 'rook':
                rook_indexes.append(black_moved[i])
                rook_locations.append(black_locations[i])
            if black_pieces[i] == 'king':
                king_index = i
                king_pos = black_locations[i]
        if not black_moved[king_index] and False in rook_indexes and not check:
            for i in range(len(rook_indexes)):
                castle = True
                if rook_locations[i][0] > king_pos[0]:
                    empty_squares = [(king_pos[0] + 1, king_pos[1]), (king_pos[0] + 2, king_pos[1]),
                                     (king_pos[0] + 3, king_pos[1])]
                else:
                    empty_squares = [(king_pos[0] - 1, king_pos[1]), (king_pos[0] - 2, king_pos[1])]
                for j in range(len(empty_squares)):
                    if empty_squares[j] in white_locations or empty_squares[j] in black_locations or \
                            empty_squares[j] in white_options or rook_indexes[i]:
                        castle = False
                if castle:
                    castle_moves.append((empty_squares[1], empty_squares[0]))
    return castle_moves


def draw_castling(moves):
    if turn_step < 2:
        color = 'red'
    else:
        color = 'blue'
    for i in range(len(moves)):
        pygame.draw.circle(screen, color, (moves[i][0][0] * 100 + 50, moves[i][0][1] * 100 + 70), 8)
        screen.blit(font.render('king', True, 'black'), (moves[i][0][0] * 100 + 30, moves[i][0][1] * 100 + 70))
        pygame.draw.circle(screen, color, (moves[i][1][0] * 100 + 50, moves[i][1][1] * 100 + 70), 8)
        screen.blit(font.render('rook', True, 'black'),
                    (moves[i][1][0] * 100 + 30, moves[i][1][1] * 100 + 70))
        pygame.draw.line(screen, color, (moves[i][0][0] * 100 + 50, moves[i][0][1] * 100 + 70),
                         (moves[i][1][0] * 100 + 50, moves[i][1][1] * 100 + 70), 2)


# add pawn promotion
def check_promotion():
    pawn_indexes = []
    white_promotion = False
    black_promotion = False
    promote_index = 100
    for i in range(len(white_pieces)):
        if white_pieces[i] == 'pawn':
            pawn_indexes.append(i)
    for i in range(len(pawn_indexes)):
        if white_locations[pawn_indexes[i]][1] == 7:
            white_promotion = True
            promote_index = pawn_indexes[i]
    pawn_indexes = []
    for i in range(len(black_pieces)):
        if black_pieces[i] == 'pawn':
            pawn_indexes.append(i)
    for i in range(len(pawn_indexes)):
        if black_locations[pawn_indexes[i]][1] == 0:
            black_promotion = True
            promote_index = pawn_indexes[i]
    return white_promotion, black_promotion, promote_index


def draw_promotion():
    pygame.draw.rect(screen, 'dark gray', [800, 0, 200, 420])
    if white_promote:
        color = 'white'
        for i in range(len(white_promotions)):
            piece = white_promotions[i]
            index = piece_list.index(piece)
            screen.blit(white_images[index], (860, 5 + 100 * i))
    elif black_promote:
        color = 'black'
        for i in range(len(black_promotions)):
            piece = black_promotions[i]
            index = piece_list.index(piece)
            screen.blit(black_images[index], (860, 5 + 100 * i))
    pygame.draw.rect(screen, color, [800, 0, 200, 420], 8)


def check_promo_select():
    mouse_pos = pygame.mouse.get_pos()
    left_click = pygame.mouse.get_pressed()[0]
    x_pos = mouse_pos[0] // 100
    y_pos = mouse_pos[1] // 100
    if white_promote and left_click and x_pos > 7 and y_pos < 4:
        game_state.promote_pawn(white_promotions[y_pos])
        sync_globals()
    elif black_promote and left_click and x_pos > 7 and y_pos < 4:
        game_state.promote_pawn(black_promotions[y_pos])
        sync_globals()


def reset_game():
    """Reset the game to initial state"""
    game_state.reset_game()
    # Clear AI thinking state
    if hasattr(game_state, 'ai_thinking'):
        game_state.ai_thinking = False
    if hasattr(game_state, 'ai_think_start_time'):
        delattr(game_state, 'ai_think_start_time')
    # Update options after reset
    sync_globals()
    # Re-sync after options are updated
    sync_globals()


# Setup game logic functions
_setup_game_logic()

# main game loop
counter = 0
run = True
in_menu = True

while run:
    timer.tick(fps)
    if counter < 30:
        counter += 1
    else:
        counter = 0
    
    if in_menu:
        screen.fill('dark gray')
        if menu.showing_ai_selection:
            buttons = menu.draw_ai_selection()
        elif menu.entering_room_code:
            buttons = menu.draw_online_menu()
        else:
            buttons = menu.draw_main_menu()
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = menu.handle_click(event.pos, buttons)
                if clicked == 'pvp':
                    current_mode = GAME_MODE_LOCAL
                    in_menu = False
                    reset_game()
                elif clicked == 'ai':
                    menu.showing_ai_selection = True
                elif clicked == 'online':
                    menu.entering_room_code = True
                elif clicked == 'create':
                    current_mode = GAME_MODE_ONLINE
                    from online_client import OnlineClient
                    online_client = OnlineClient(game_state)
                    if online_client.connect():
                        if online_client.create_room():
                            in_menu = False
                            reset_game()
                elif clicked == 'join':
                    if menu.room_code and len(menu.room_code) == 6:
                        current_mode = GAME_MODE_ONLINE
                        from online_client import OnlineClient
                        online_client = OnlineClient(game_state)
                        if online_client.connect():
                            if online_client.join_room(menu.room_code.upper()):
                                in_menu = False
                                reset_game()
                elif clicked == 'minimax':
                    current_mode = GAME_MODE_AI
                    menu.ai_type = AI_MINIMAX
                    in_menu = False
                    reset_game()
                    # Import AI engine here to avoid circular imports
                    from ai_engine import MinimaxAI
                    ai_opponent = MinimaxAI(menu.ai_difficulty)
                    # Initialize AI thinking state
                    game_state.ai_thinking = False
                elif clicked == 'stockfish':
                    current_mode = GAME_MODE_AI
                    menu.ai_type = AI_STOCKFISH
                    in_menu = False
                    reset_game()
                    from ai_engine import StockfishAI
                    ai_opponent = StockfishAI()
                    # Initialize AI thinking state
                    game_state.ai_thinking = False
                elif clicked == 'back':
                    menu.showing_ai_selection = False
                    menu.entering_room_code = False
                    menu.room_code = ""
                elif clicked == 'create':
                    # Will be handled in online_client
                    pass
                elif clicked == 'join':
                    # Will be handled in online_client
                    pass
            if event.type == pygame.KEYDOWN and menu.showing_ai_selection:
                if event.key == pygame.K_LEFT and menu.ai_type == 'minimax':
                    menu.ai_difficulty = max(1, menu.ai_difficulty - 1)
                elif event.key == pygame.K_RIGHT and menu.ai_type == 'minimax':
                    menu.ai_difficulty = min(5, menu.ai_difficulty + 1)
    else:
        # Game is running
        sync_globals()
        screen.fill('dark gray')
        draw_board()
        draw_pieces()
        draw_captured()
        draw_check()
        if not game_over:
            game_state.check_promotion()
            sync_globals()
            if white_promote or black_promote:
                draw_promotion()
                check_promo_select()
        if selection != 100:
            valid_moves = check_valid_moves()
            draw_valid(valid_moves)
            if selected_piece == 'king':
                draw_castling(castling_moves)
        
        # Handle AI moves
        if current_mode == GAME_MODE_AI and not game_over and turn_step >= 2 and ai_opponent:
            # AI's turn (black) - show thinking status
            if not hasattr(game_state, 'ai_thinking') or not game_state.ai_thinking:
                game_state.ai_thinking = True
                game_state.ai_think_start_time = pygame.time.get_ticks()
            
            # Wait 2 seconds before making move
            if hasattr(game_state, 'ai_think_start_time'):
                elapsed = pygame.time.get_ticks() - game_state.ai_think_start_time
                if elapsed >= 2000:  # 2 seconds
                    move = ai_opponent.get_move(game_state)
                    if move:
                        from_pos, to_pos = move
                        success = game_state.make_move(from_pos, to_pos)
                        if success:
                            sync_globals()
                            # Reset AI thinking state for next turn
                            game_state.ai_thinking = False
                            if hasattr(game_state, 'ai_think_start_time'):
                                delattr(game_state, 'ai_think_start_time')
                    else:
                        # If no move found, reset thinking state
                        game_state.ai_thinking = False
                        if hasattr(game_state, 'ai_think_start_time'):
                            delattr(game_state, 'ai_think_start_time')
        
        # Handle online moves (WebSocket handles messages asynchronously)
        if current_mode == GAME_MODE_ONLINE and online_client:
            online_client.process_messages()
            # Sync game state periodically
            if online_client.connected and online_client.room_code:
                online_client.update_game_state()
        
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_mode == GAME_MODE_ONLINE and online_client:
                        online_client.disconnect()
                    in_menu = True
                    menu.reset()
                    current_mode = None
                    ai_opponent = None
                    online_client = None
                if event.key == pygame.K_RETURN and game_over:
                    reset_game()
                if event.unicode and menu.entering_room_code:
                    if event.unicode.isalnum() and len(menu.room_code) < 6:
                        menu.room_code += event.unicode.upper()
                    elif event.key == pygame.K_BACKSPACE:
                        menu.room_code = menu.room_code[:-1]
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                x_coord = event.pos[0] // 100
                y_coord = event.pos[1] // 100
                click_coords = (x_coord, y_coord)
                
                # Skip if it's AI's turn
                if current_mode == GAME_MODE_AI and turn_step >= 2:
                    continue
                
                # Skip if it's online opponent's turn
                if current_mode == GAME_MODE_ONLINE and online_client and not online_client.is_my_turn():
                    continue
                
                if turn_step <= 1:
                    if click_coords == (8, 8) or click_coords == (9, 8):
                        game_state.winner = 'black'
                        game_state.game_over = True
                        sync_globals()
                    if click_coords in white_locations:
                        game_state.selection = white_locations.index(click_coords)
                        game_state.selected_piece = white_pieces[game_state.selection]
                        sync_globals()
                        if turn_step == 0:
                            game_state.turn_step = 1
                            sync_globals()
                    if click_coords in valid_moves and selection != 100:
                        from_pos = white_locations[selection]
                        success = game_state.make_move(from_pos, click_coords)
                        if success:
                            sync_globals()
                            if current_mode == GAME_MODE_ONLINE and online_client:
                                online_client.send_move(from_pos, click_coords)
                        # Handle castling
                    elif selection != 100 and selected_piece == 'king':
                        for q in range(len(castling_moves)):
                            if click_coords == castling_moves[q][0]:
                                from_pos = white_locations[selection]
                                success = game_state.make_move(from_pos, click_coords)
                                if success:
                                    sync_globals()
                                    if current_mode == GAME_MODE_ONLINE and online_client:
                                        online_client.send_move(from_pos, click_coords)
                if turn_step > 1:
                    if click_coords == (8, 8) or click_coords == (9, 8):
                        game_state.winner = 'white'
                        game_state.game_over = True
                        sync_globals()
                    if click_coords in black_locations:
                        game_state.selection = black_locations.index(click_coords)
                        game_state.selected_piece = black_pieces[game_state.selection]
                        sync_globals()
                        if turn_step == 2:
                            game_state.turn_step = 3
                            sync_globals()
                    if click_coords in valid_moves and selection != 100:
                        from_pos = black_locations[selection]
                        success = game_state.make_move(from_pos, click_coords)
                        if success:
                            sync_globals()
                            if current_mode == GAME_MODE_ONLINE and online_client:
                                online_client.send_move(from_pos, click_coords)
                    elif selection != 100 and selected_piece == 'king':
                        for q in range(len(castling_moves)):
                            if click_coords == castling_moves[q][0]:
                                from_pos = black_locations[selection]
                                success = game_state.make_move(from_pos, click_coords)
                                if success:
                                    sync_globals()
                                    if current_mode == GAME_MODE_ONLINE and online_client:
                                        online_client.send_move(from_pos, click_coords)

        if winner != '':
            game_over = True
            draw_game_over()

    pygame.display.flip()
pygame.quit()
