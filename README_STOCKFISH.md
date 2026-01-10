# Installing Stockfish Chess Engine

## Automatic Installation (Windows)

Run this command to automatically download and install Stockfish:

```bash
python install_stockfish.py
```

## Manual Installation

### Windows
1. Download Stockfish from: https://stockfishchess.org/download/
2. Extract the ZIP file
3. Place `stockfish.exe` in your project folder or add it to your PATH

### Linux
```bash
sudo apt-get install stockfish
# or
sudo yum install stockfish
```

### macOS
```bash
brew install stockfish
```

## Verification

After installation, the game will automatically detect Stockfish when you select "Stockfish AI" from the menu. If Stockfish is not found, the game will fall back to Minimax AI.

## Stockfish Configuration

The game configures Stockfish with:
- Maximum skill level (20/20)
- 512 MB hash memory
- 4 threads
- Depth 20 search
- 2 second thinking time per move

This provides professional-level chess play!
