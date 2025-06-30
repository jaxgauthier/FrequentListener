# 🎵 Audio Frequency Game

A Flask-based web application that challenges users to guess songs from reconstructed audio using Discrete Fourier Transform (DFT) processing.

## 🚀 Features

- **Audio Processing**: DFT-based frequency reconstruction with multiple difficulty levels
- **User Authentication**: Secure login/signup system with session management
- **Admin Panel**: Song management and Spotify integration
- **Statistics Tracking**: User performance and global song analytics
- **Real-time Gameplay**: Progressive difficulty reveal system

## 🏗️ Project Structure

```
DFT/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration management
│   ├── models/                  # Database models
│   │   ├── user.py             # User and AdminUser models
│   │   ├── song.py             # Song model
│   │   └── stats.py            # Statistics models
│   ├── routes/                  # Route handlers
│   │   ├── main.py             # Main game routes
│   │   ├── auth.py             # Authentication routes
│   │   ├── admin.py            # Admin panel routes
│   │   └── api.py              # API endpoints
│   ├── services/                # Business logic
│   │   ├── audio_service.py    # Audio processing
│   │   ├── spotify_service.py  # Spotify integration
│   │   └── stats_service.py    # Statistics management
│   └── utils/                   # Utility functions
├── templates/                   # HTML templates
├── static/                      # Static files (CSS, JS, images)
├── data/                        # Database files
├── audio/                       # Audio processing and storage
│   ├── uploads/                # Temporary uploads
│   └── OutputWAVS/             # Processed frequency files
├── scripts/                     # Management scripts
├── tests/                       # Test files
├── docs/                        # Documentation
├── deployment/                  # Deployment configurations
└── requirements/                # Dependency management
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip
- Git

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DFT
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

5. **Initialize database**
   ```bash
   python scripts/init_db.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secure-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Spotify API Configuration
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret

# Database Configuration
DATABASE_URL=sqlite:///data/game.db

# Server Configuration
HOST=127.0.0.1
PORT=5001
```

### Spotify API Setup
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Copy Client ID and Client Secret to your `.env` file

## 🎮 Usage

### For Players
1. Visit the main page to play the game
2. Listen to reconstructed audio at different frequency levels
3. Guess the original song title or artist
4. Track your progress by creating an account

### For Admins
1. Login at `/admin/login`
2. Search and add songs from Spotify
3. Process songs through the DFT pipeline
4. Set active songs for gameplay
5. View user statistics and analytics

## 🚀 Deployment

### Railway Deployment
1. **Prepare for deployment**
   ```bash
   python scripts/prepare_deployment.py
   ```

2. **Deploy to Railway**
   - Connect your GitHub repository to Railway
   - Set environment variables in Railway dashboard
   - Deploy automatically on push

### Other Platforms
The application is configured for deployment on:
- **Heroku**: Uses `Procfile` and `runtime.txt`
- **Render**: Uses `render.yaml`
- **DigitalOcean App Platform**: Uses `do-app.yaml`

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_audio_service.py

# Run with coverage
python -m pytest --cov=app tests/
```

## 📊 Database Management

### Initialize Database
```bash
python scripts/init_db.py
```

### Create Admin User
```bash
python scripts/create_admin.py --username admin --password securepass --email admin@example.com
```

### Backup Database
```bash
python scripts/backup_db.py
```

### Reset All Data
```bash
python scripts/reset_data.py
```

## 🔧 Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes following the established structure
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

### Database Migrations
```bash
# Create migration
python scripts/create_migration.py --message "Add new table"

# Apply migrations
python scripts/apply_migrations.py
```

## 📝 API Documentation

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/signup` - User registration
- `GET /auth/logout` - User logout

### Game Endpoints
- `GET /` - Main game page
- `POST /submit_guess` - Submit song guess
- `GET /current_stats` - Get current song statistics
- `GET /play_frequency/<song>/<freq>` - Serve audio file

### Admin Endpoints
- `GET /admin` - Admin dashboard
- `POST /admin/process_spotify_song` - Process Spotify song
- `DELETE /admin/delete/<song_id>` - Delete song
- `POST /admin/set_active/<song_id>` - Set active song

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the [documentation](docs/)
- Review the [FAQ](docs/FAQ.md)

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.
