# 🎵 Frequent Listener - Audio Frequency Guessing Game

A Flask-based web game where players listen to reconstructed audio with different frequency levels and try to guess the original song.

## 🚀 Railway Deployment

### Prerequisites
- Railway account (free tier available)
- GitHub repository with your code
- Spotify Developer credentials (optional, for song search)

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Ensure these files are in your repository**:
   - `app.py` (main Flask application)
   - `requirements.txt` (Python dependencies)
   - `Procfile` (Railway deployment configuration)
   - `runtime.txt` (Python version)
   - `.gitignore` (exclude unnecessary files)

### Step 2: Deploy to Railway

1. **Go to [Railway.app](https://railway.app)** and sign in with GitHub
2. **Click "New Project"** → "Deploy from GitHub repo"
3. **Select your repository** and click "Deploy"
4. **Wait for deployment** (usually 2-3 minutes)

### Step 3: Configure Environment Variables

In your Railway project dashboard, go to **Variables** tab and add:

```
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-admin-password
```

### Step 4: Set Up Admin Access

1. **Create your admin account** by visiting your deployed URL
2. **Sign up** with the username/password you set in environment variables
3. **Access admin panel** at `your-url.com/admin`

### Step 5: Initialize Database

1. **Visit your deployed URL** - the database will be created automatically
2. **Log in as admin** and go to the admin panel
3. **Add songs** using the Spotify search feature or upload audio files

## 🔐 Admin Access Control

The admin panel is protected by:
- **Session-based authentication** - only logged-in users can access `/admin`
- **Environment variables** - set your admin credentials securely
- **Database isolation** - each deployment has its own database

## 🎮 How to Play

1. **Visit the game URL** (public access)
2. **Listen to reconstructed audio** starting with hardest difficulty (100 frequencies)
3. **Click the + button** to reveal easier versions
4. **Guess the song** using the search form
5. **Score starts at 7** and decreases by 1 for each difficulty level revealed
6. **Sign in** to track your progress and see stats

## 🛠️ Admin Features

- **Spotify Integration**: Search and add songs from Spotify
- **Audio Processing**: Automatic DFT processing with multiple frequency levels
- **Song Management**: Set active songs, delete songs, view all songs
- **User Management**: View user accounts and stats
- **Statistics**: Track global and individual performance

## 📁 Project Structure

```
DFT/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Railway deployment config
├── runtime.txt           # Python version
├── .gitignore           # Git ignore rules
├── templates/           # HTML templates
│   ├── user.html        # Main game interface
│   ├── admin.html       # Admin panel
│   ├── login.html       # Login page
│   └── signup.html      # Signup page
├── static/              # CSS, JS, and static files
├── OutputWAVS/          # Processed audio files
└── uploads/             # Temporary uploads
```

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `SPOTIFY_CLIENT_ID` | Spotify API client ID | No (uses sample data) |
| `SPOTIFY_CLIENT_SECRET` | Spotify API client secret | No (uses sample data) |
| `ADMIN_USERNAME` | Your admin username | Yes |
| `ADMIN_PASSWORD` | Your admin password | Yes |

## 🌐 Public Access

Once deployed:
- **Main game**: `https://your-app-name.railway.app/`
- **Admin panel**: `https://your-app-name.railway.app/admin` (login required)
- **User signup**: `https://your-app-name.railway.app/signup`

## 📊 Features

- **Multi-frequency audio reconstruction** (100 to 7500 frequencies)
- **Real-time Spotify search** for song suggestions
- **User authentication** with session management
- **Progress tracking** with all-time statistics
- **Admin controls** for song management
- **Responsive design** for mobile and desktop

## 🚨 Important Notes

1. **Database**: Railway uses ephemeral storage - data may reset on redeployment
2. **Audio files**: Large audio files are stored temporarily - consider external storage for production
3. **Admin access**: Keep your admin credentials secure
4. **Rate limiting**: Consider implementing rate limiting for public access

## 🆘 Troubleshooting

- **Deployment fails**: Check `requirements.txt` and `Procfile`
- **Database errors**: Visit the app URL to initialize the database
- **Admin access issues**: Verify environment variables are set correctly
- **Audio not playing**: Check if audio files exist in `OutputWAVS/`

## 📞 Support

For deployment issues, check Railway's documentation or contact their support.