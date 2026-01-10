# Quick Stockfish Installation Guide

## Option 1: Automatic (Try First)
```bash
python install_stockfish.py
```

## Option 2: Manual Download (If Auto Fails)

### Windows:
1. Visit: https://stockfishchess.org/download/
2. Click "Download" for Windows
3. Extract the ZIP file
4. Find `stockfish.exe` inside
5. Copy `stockfish.exe` to your chess_game folder

### Alternative Direct Download:
- Go to: https://github.com/official-stockfish/Stockfish/releases
- Download the latest `stockfish-windows-x86-64-avx2.zip`
- Extract and copy `stockfish.exe` to your project folder

## Option 3: Use Python Stockfish Package
```bash
pip install stockfish
```
Then the game will try to use it automatically.

## Verify Installation
After placing `stockfish.exe` in your project folder, run the game and select "Stockfish AI". If it works, you'll see "Stockfish engine initialized successfully!" in the console.

## Note
If Stockfish is not found, the game will automatically use the improved Minimax AI instead, which is now much smarter!
