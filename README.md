# Chess Game - Multi-Mode Edition

A feature-rich chess game written in Python with Pygame, supporting local PvP, AI opponents, and online multiplayer.

## Features

- **Local PvP**: Play against a friend on the same computer
- **AI Opponents**: 
  - Minimax AI with adjustable difficulty (depth 1-5)
  - Stockfish integration for strong play
- **Online Multiplayer**: 
  - Create or join rooms with 6-character codes
  - Shareable invite links
  - Real-time gameplay via WebSocket
- **Web Interface**: Play in your browser (hybrid desktop/web support)

## Installation

1. Install Python 3.8 or higher (Python 3.11-3.13 recommended for best compatibility)

2. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note for Python 3.14+ users**: The project uses `pygame-ce` (Community Edition) instead of `pygame` for better compatibility with newer Python versions. The API is identical, so no code changes are needed.

3. (Optional) For Stockfish AI, download Stockfish:
   - Windows: Download from [stockfishchess.org](https://stockfishchess.org/download/)
   - Linux: `sudo apt-get install stockfish` or `sudo yum install stockfish`
   - macOS: `brew install stockfish`

## Running the Game

### Desktop Version (Pygame)
```bash
python additions.py
```

### Web Server (for online multiplayer)
```bash
python server.py
```
Then open your browser to `http://localhost:5000`

## Game Modes

### Local PvP
- Select "Local PvP" from the main menu
- Two players take turns on the same computer
- White moves first

### Play vs AI
- Select "Play vs AI" from the main menu
- Choose between Minimax or Stockfish AI
- For Minimax, adjust difficulty with left/right arrow keys
- You play as White, AI plays as Black

### Online Multiplayer
- Select "Online Multiplayer" from the main menu
- **Create Room**: Generate a room code and share it with your friend
- **Join Room**: Enter a 6-character room code to join
- Both players can use the desktop app or web interface

## Controls

- **Mouse**: Click to select pieces and make moves
- **ESC**: Return to main menu
- **ENTER**: Restart game after game over
- **Arrow Keys**: Adjust AI difficulty (in AI selection menu)

## Room Codes

Room codes are 6-character alphanumeric codes (e.g., "ABC123"). Share these codes or the invite link to play with friends online.

## Deployment

To deploy the web server online:

1. Update `constants.py` with your server URL:
```python
SERVER_URL = 'https://your-domain.com'
WS_URL = 'wss://your-domain.com'
```

2. Deploy to platforms like:
   - Heroku
   - Railway
   - Render
   - DigitalOcean

3. Make sure WebSocket support is enabled on your hosting platform

## File Structure

- `additions.py` - Main game file with Pygame interface
- `constants.py` - Game constants and configuration
- `menu.py` - Menu system
- `game_logic.py` - Core game logic (framework-agnostic)
- `ai_engine.py` - AI implementations (Minimax and Stockfish)
- `server.py` - Online multiplayer server
- `online_client.py` - Desktop client for online play
- `web_app.py` - Web application entry point
- `templates/index.html` - Web interface
- `requirements.txt` - Python dependencies

## Troubleshooting

- **Stockfish not found**: Install Stockfish or the game will fall back to Minimax AI
- **Connection issues**: Make sure the server is running and the URL in `constants.py` is correct
- **Import errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`

## License

This project is open source and available for modification and distribution.
