# Deployment Guide for Chess Game Online Server

## Important Note
Vercel does **not** support WebSockets, which are required for real-time multiplayer. Use one of these alternatives:

## Option 1: Railway (Recommended - Easiest)

1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub repository
4. Railway will automatically detect the Python project
5. Add environment variables if needed (none required for basic setup)
6. The server will deploy automatically
7. Your server URL will be something like: `https://your-app.railway.app`

Update `constants.py`:
```python
SERVER_URL = 'https://your-app.railway.app'
WS_URL = 'wss://your-app.railway.app'
```

## Option 2: Render

1. Go to [render.com](https://render.com) and sign up
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Environment**: Python 3
5. Click "Create Web Service"
6. Your server URL will be: `https://your-app.onrender.com`

Update `constants.py`:
```python
SERVER_URL = 'https://your-app.onrender.com'
WS_URL = 'wss://your-app.onrender.com'
```

## Option 3: Heroku (Legacy)

1. Install Heroku CLI
2. Run:
```bash
heroku create your-app-name
git push heroku main
```
3. Your server URL: `https://your-app-name.herokuapp.com`

## Option 4: Self-Hosted (VPS/Dedicated Server)

1. Set up a VPS (DigitalOcean, AWS EC2, etc.)
2. Install Python and dependencies
3. Run: `python server.py`
4. Use nginx as reverse proxy for WebSocket support
5. Set up SSL with Let's Encrypt

## Testing Your Deployment

1. Start the server: `python server.py`
2. Open browser to your server URL
3. Create a room and test the connection
4. Share the room code with a friend to test multiplayer

## Troubleshooting

- **WebSocket connection fails**: Make sure your hosting platform supports WebSockets
- **Port issues**: Some platforms use the `PORT` environment variable
- **CORS errors**: The server already has CORS enabled for all origins

## Free Tier Limits

- **Railway**: $5 free credit monthly
- **Render**: Free tier with sleep after inactivity
- **Heroku**: No longer has free tier
