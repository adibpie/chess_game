# Changelog - Chess Game Improvements

## Latest Updates

### 🎮 AI Improvements
- **Stockfish AI Enhanced**: 
  - Fixed coordinate conversion issues
  - Increased skill level to maximum (20)
  - Better time limits (1.5s) and depth (18)
  - Proper board state synchronization
  - Now properly captures pieces and makes smart moves

- **AI Thinking Animation**:
  - Added 2-second delay before AI moves
  - Status message: "Black is deciding the move..." appears during thinking
  - More engaging gameplay experience

### 🎨 Menu Redesign
- **Retro Pixelated Theme**:
  - Pixelated text rendering with customizable pixel size
  - 3D button effects (highlight/shadow)
  - Grid background pattern
  - Yellow border accents
  - Hover effects on buttons
  - Consistent retro aesthetic throughout all menus

### 🌐 Online Hosting
- **Deployment Support**:
  - Created deployment files for Railway, Render, and Heroku
  - Added `DEPLOYMENT.md` with step-by-step hosting guide
  - Server now supports PORT environment variable
  - Note: Vercel doesn't support WebSockets, use Railway or Render instead

### 🐛 Bug Fixes
- Fixed Stockfish coordinate conversion
- Improved board state synchronization
- Better error handling for AI moves
- Fixed AI thinking state management

## Files Changed
- `ai_engine.py` - Enhanced Stockfish AI
- `menu.py` - Complete retro pixelated redesign
- `additions.py` - Added AI thinking delay and status
- `server.py` - Added PORT environment variable support
- `DEPLOYMENT.md` - New deployment guide
- `Procfile`, `railway.json`, `render.yaml` - Deployment configs
