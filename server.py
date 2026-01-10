# Online multiplayer server for chess game
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import string
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chess-game-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Room management
rooms = {}  # room_code -> {players: [], game_state: {}, created_at: datetime}

def generate_room_code():
    """Generate a unique 6-character room code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in rooms:
            return code

@app.route('/')
def index():
    """Serve the web interface"""
    return render_template('index.html', server_url=request.host_url.rstrip('/'))

@app.route('/play/<room_code>')
def play_room(room_code):
    """Serve the game interface for a specific room"""
    return render_template('index.html', room_code=room_code)

@app.route('/api/create_room', methods=['POST'])
def create_room():
    """Create a new game room"""
    room_code = generate_room_code()
    rooms[room_code] = {
        'players': [],
        'game_state': None,
        'created_at': datetime.now(),
        'player_colors': {}  # socket_id -> 'white' or 'black'
    }
    return jsonify({'room_code': room_code, 'invite_link': f'/play/{room_code}'})

@app.route('/api/room/<room_code>', methods=['GET'])
def get_room_info(room_code):
    """Get information about a room"""
    if room_code in rooms:
        room = rooms[room_code]
        return jsonify({
            'exists': True,
            'player_count': len(room['players']),
            'full': len(room['players']) >= 2
        })
    return jsonify({'exists': False})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")
    # Remove player from all rooms
    for room_code, room in rooms.items():
        if request.sid in room['players']:
            room['players'].remove(request.sid)
            if request.sid in room['player_colors']:
                del room['player_colors'][request.sid]
            leave_room(room_code)
            # Notify other player
            for player_id in room['players']:
                emit('opponent_disconnected', {'message': 'Opponent disconnected'}, room=player_id)
            # Clean up empty rooms older than 1 hour
            if len(room['players']) == 0 and (datetime.now() - room['created_at']) > timedelta(hours=1):
                del rooms[room_code]

@socketio.on('join_room')
def handle_join_room(data):
    """Handle player joining a room"""
    room_code = data.get('room_code')
    if not room_code:
        emit('error', {'message': 'Room code required'})
        return
    
    if room_code not in rooms:
        emit('error', {'message': 'Room does not exist'})
        return
    
    room = rooms[room_code]
    
    if len(room['players']) >= 2:
        emit('error', {'message': 'Room is full'})
        return
    
    # Add player to room
    if request.sid not in room['players']:
        room['players'].append(request.sid)
        join_room(room_code)
        
        # Assign color
        if len(room['players']) == 1:
            room['player_colors'][request.sid] = 'white'
            emit('joined_room', {
                'room_code': room_code,
                'color': 'white',
                'status': 'waiting'
            })
        else:
            room['player_colors'][request.sid] = 'black'
            emit('joined_room', {
                'room_code': room_code,
                'color': 'black',
                'status': 'ready'
            })
            # Notify first player that game can start
            for player_id in room['players']:
                if player_id != request.sid:
                    emit('opponent_joined', {
                        'message': 'Opponent joined. Game starting!',
                        'color': 'white'
                    }, room=player_id)
                    emit('game_start', {'message': 'Game starting!'}, room=player_id)
            emit('game_start', {'message': 'Game starting!'})

@socketio.on('create_room')
def handle_create_room():
    """Handle room creation via WebSocket"""
    room_code = generate_room_code()
    rooms[room_code] = {
        'players': [request.sid],
        'game_state': None,
        'created_at': datetime.now(),
        'player_colors': {request.sid: 'white'}
    }
    join_room(room_code)
    emit('room_created', {
        'room_code': room_code,
        'invite_link': f'/play/{room_code}',
        'color': 'white'
    })

@socketio.on('make_move')
def handle_move(data):
    """Handle a move from a player"""
    room_code = data.get('room_code')
    from_pos = tuple(data.get('from_pos'))
    to_pos = tuple(data.get('to_pos'))
    
    if room_code not in rooms:
        emit('error', {'message': 'Room does not exist'})
        return
    
    room = rooms[room_code]
    
    if request.sid not in room['players']:
        emit('error', {'message': 'Not in this room'})
        return
    
    # Update game state if provided
    if 'game_state' in data:
        room['game_state'] = data['game_state']
    
    # Broadcast move and game state to other player
    for player_id in room['players']:
        if player_id != request.sid:
            emit('opponent_move', {
                'from_pos': from_pos,
                'to_pos': to_pos,
                'game_state': room.get('game_state')
            }, room=player_id)

@socketio.on('update_game_state')
def handle_update_state(data):
    """Handle game state update"""
    room_code = data.get('room_code')
    game_state = data.get('game_state')
    
    if room_code not in rooms:
        return
    
    rooms[room_code]['game_state'] = game_state
    
    # Broadcast to other player
    room = rooms[room_code]
    for player_id in room['players']:
        if player_id != request.sid:
            emit('game_state_update', {
                'game_state': game_state
            }, room=player_id)

@socketio.on('forfeit')
def handle_forfeit(data):
    """Handle player forfeit"""
    room_code = data.get('room_code')
    
    if room_code not in rooms:
        return
    
    room = rooms[room_code]
    player_color = room['player_colors'].get(request.sid, 'unknown')
    winner = 'black' if player_color == 'white' else 'white'
    
    # Notify other player
    for player_id in room['players']:
        if player_id != request.sid:
            emit('opponent_forfeited', {
                'winner': winner,
                'message': f'{player_color.capitalize()} forfeited. {winner.capitalize()} wins!'
            }, room=player_id)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("Starting Chess Game Server...")
    print(f"Server running on http://0.0.0.0:{port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
