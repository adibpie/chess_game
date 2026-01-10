# Online multiplayer client for desktop Pygame version
import socketio
import threading
from constants import WS_URL
from game_logic import GameState

class OnlineClient:
    def __init__(self, game_state):
        self.game_state = game_state
        self.sio = socketio.Client()
        self.room_code = None
        self.player_color = None
        self.connected = False
        self.my_turn = False
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.sio.on('connect')
        def on_connect():
            print("Connected to server")
            self.connected = True
        
        @self.sio.on('disconnect')
        def on_disconnect():
            print("Disconnected from server")
            self.connected = False
        
        @self.sio.on('joined_room')
        def on_joined_room(data):
            self.room_code = data['room_code']
            self.player_color = data['color']
            self.my_turn = (data['color'] == 'white')
            print(f"Joined room {self.room_code} as {self.player_color}")
        
        @self.sio.on('opponent_joined')
        def on_opponent_joined(data):
            print("Opponent joined the room")
        
        @self.sio.on('game_start')
        def on_game_start(data):
            print("Game starting!")
            self.my_turn = (self.player_color == 'white')
        
        @self.sio.on('opponent_move')
        def on_opponent_move(data):
            from_pos = tuple(data['from_pos'])
            to_pos = tuple(data['to_pos'])
            print(f"Opponent moved: {from_pos} -> {to_pos}")
            # Apply opponent's move
            self.game_state.make_move(from_pos, to_pos)
            self.my_turn = True
        
        @self.sio.on('game_state_update')
        def on_game_state_update(data):
            game_state_data = data['game_state']
            self.game_state.load_board_state(game_state_data)
        
        @self.sio.on('opponent_forfeited')
        def on_opponent_forfeited(data):
            winner = data['winner']
            print(f"Opponent forfeited. {winner.capitalize()} wins!")
            self.game_state.winner = winner
            self.game_state.game_over = True
        
        @self.sio.on('opponent_disconnected')
        def on_opponent_disconnected(data):
            print("Opponent disconnected")
            self.game_state.game_over = True
        
        @self.sio.on('error')
        def on_error(data):
            print(f"Error: {data.get('message', 'Unknown error')}")
    
    def connect(self, url=None):
        """Connect to the server"""
        if url is None:
            url = WS_URL.replace('ws://', 'http://').replace('wss://', 'https://')
        try:
            self.sio.connect(url)
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.connected:
            self.sio.disconnect()
    
    def create_room(self):
        """Create a new room"""
        if not self.connected:
            return False
        
        self.sio.emit('create_room')
        # Response will come via 'room_created' event handler
        return True
    
    def join_room(self, room_code):
        """Join an existing room"""
        if not self.connected:
            return False
        
        self.sio.emit('join_room', {'room_code': room_code})
        return True
    
    def send_move(self, from_pos, to_pos):
        """Send a move to the server"""
        if not self.connected or not self.room_code:
            return
        
        self.sio.emit('make_move', {
            'room_code': self.room_code,
            'from_pos': list(from_pos),
            'to_pos': list(to_pos),
            'game_state': self.game_state.get_board_state()
        })
        self.my_turn = False
    
    def update_game_state(self):
        """Update game state on server"""
        if not self.connected or not self.room_code:
            return
        
        self.sio.emit('update_game_state', {
            'room_code': self.room_code,
            'game_state': self.game_state.get_board_state()
        })
    
    def forfeit(self):
        """Forfeit the game"""
        if not self.connected or not self.room_code:
            return
        
        self.sio.emit('forfeit', {'room_code': self.room_code})
    
    def is_my_turn(self):
        """Check if it's the player's turn"""
        return self.my_turn
    
    def process_messages(self):
        """Process incoming messages (call this in game loop)"""
        # SocketIO handles messages asynchronously via callbacks
        pass
