# 🏆 HighScore - Open Source Leaderboard API

An open-source, fast, and easy-to-use leaderboard API for your games. Store scores, retrieve leaderboards, and track player statistics with a simple REST API.

## 🌐 Live Demo

**Try it now:** [https://api-leaderboard.qulyubis.biz.id](https://api-leaderboard.qulyubis.biz.id)

- **API Documentation**: [https://api-leaderboard.qulyubis.biz.id/docs](https://api-leaderboard.qulyubis.biz.id/docs)
- **Interactive Docs**: [https://api-leaderboard.qulyubis.biz.id/redoc](https://api-leaderboard.qulyubis.biz.id/redoc)

## ✨ Features

- 🎮 **Multi-game support** - Manage leaderboards for multiple games
- 🔑 **API Key Authentication** - Secure your games with unique API keys
- 🏆 **Flexible Leaderboards** - Get global, time-based, or player-specific leaderboards
- 📊 **Player Statistics** - Track individual player performance
- ⚡ **Fast & Scalable** - Built with FastAPI and async support
- 🐳 **Docker Ready** - Easy deployment with Docker
- 📖 **Auto-generated API Docs** - Swagger UI and ReDoc included

## 🔒 Security Features

**Enterprise-grade security built-in:**

- 🛡️ **Rate Limiting** - Prevent API abuse with configurable per-endpoint limits
- 🔐 **Security Headers** - HSTS, CSP, X-Frame-Options, and more
- ✅ **Input Validation** - Advanced sanitization prevents SQL injection and XSS
- 📝 **Request Logging** - Monitor all API requests with timestamps and client IPs
- 📏 **Size Limits** - Prevent DoS attacks with request body size limits (1MB default)
- 🚫 **IP Blocking** - Block malicious IPs at middleware level
- 🔑 **Bcrypt API Keys** - Keys hashed before storage, never stored in plain text
- 🛑 **Error Handling** - Secure error messages that don't leak sensitive info

**See [SECURITY.md](SECURITY.md) for complete security documentation.**

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/highscore.git
cd highscore

# Run with Docker Compose
docker-compose up -d

# API will be available at http://localhost:8000
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/highscore.git
cd highscore

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
```

## 📖 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 API Usage Examples

### 1. Create a Game and Get API Key

```bash
POST /api/v1/games
Content-Type: application/json

{
  "name": "My Awesome Game",
  "description": "An amazing game"
}

Response:
{
  "id": 1,
  "name": "My Awesome Game",
  "description": "An amazing game",
  "api_key": "game_abc123def456...",
  "created_at": "2025-11-08T20:21:28"
}
```

**⚠️ Save your API key! It's only shown once.**

### 2. Submit a Score

```bash
POST /api/v1/scores
Content-Type: application/json
X-API-Key: game_abc123def456...

{
  "player_name": "ProGamer123",
  "score": 9500,
  "game_metadata": {
    "level": 10,
    "time_played": 350
  }
}

Response:
{
  "id": 1,
  "game_id": 1,
  "player_name": "ProGamer123",
  "score": 9500,
  "game_metadata": {"level": 10, "time_played": 350},
  "created_at": "2025-11-08T20:21:28"
}
```

### 3. Get Leaderboard

```bash
GET /api/v1/leaderboard?limit=10
X-API-Key: game_abc123def456...

Response:
{
  "game_id": 1,
  "game_name": "My Awesome Game",
  "entries": [
    {
      "rank": 1,
      "player_name": "ProGamer123",
      "score": 9500,
      "created_at": "2025-11-08T20:21:28"
    },
    {
      "rank": 2,
      "player_name": "Player456",
      "score": 8200,
      "created_at": "2025-11-08T19:15:10"
    }
  ],
  "total_entries": 2
}
```

### 4. Get Player Statistics

```bash
GET /api/v1/players/ProGamer123/stats
X-API-Key: game_abc123def456...

Response:
{
  "player_name": "ProGamer123",
  "game_id": 1,
  "total_scores": 5,
  "best_score": 9500,
  "average_score": 7850.5,
  "worst_score": 6200,
  "rank": 1,
  "first_played": "2025-11-01T10:30:00",
  "last_played": "2025-11-08T20:21:28"
}
```

### 5. Get Time-Based Leaderboard

```bash
# Get today's leaderboard
GET /api/v1/leaderboard?period=today&limit=10
X-API-Key: game_abc123def456...

# Get this week's leaderboard
GET /api/v1/leaderboard?period=week&limit=10
X-API-Key: game_abc123def456...

# Get this month's leaderboard
GET /api/v1/leaderboard?period=month&limit=10
X-API-Key: game_abc123def456...
```

## 🔧 Configuration

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite:///./highscore.db
# For PostgreSQL: postgresql://user:password@localhost/highscore

# API Settings
API_TITLE=HighScore API
API_VERSION=1.0.0
CORS_ORIGINS=*

# Security
SECRET_KEY=your-secret-key-here-change-in-production
```

## 🗄️ Database

The API uses SQLAlchemy ORM and supports:
- **SQLite** (default, perfect for development and small deployments)
- **PostgreSQL** (recommended for production)
- **MySQL** (also supported)

### Database Schema

**Games Table**
- `id`: Primary key
- `name`: Game name
- `description`: Game description
- `api_key`: Unique API key (hashed)
- `created_at`: Timestamp

**Scores Table**
- `id`: Primary key
- `game_id`: Foreign key to games
- `player_name`: Player identifier
- `score`: Integer score value
- `game_metadata`: JSON field for additional data
- `created_at`: Timestamp

## 🛠️ Technology Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **SQLite/PostgreSQL** - Database
- **Docker** - Containerization

## 📊 Advanced Features

### Custom Sorting

By default, leaderboards are sorted by highest score. You can customize this behavior.

### Metadata Support

Store additional information with each score:
```json
{
  "player_name": "Player1",
  "score": 1000,
  "game_metadata": {
    "level": 5,
    "kills": 23,
    "deaths": 2,
    "accuracy": 0.89,
    "weapon": "rifle"
  }
}
```

## 🔒 Security

- API keys are hashed before storage
- Rate limiting recommended for production
- CORS configuration included
- Environment-based configuration

## 🚢 Deployment

### Docker Deployment

```bash
docker build -t highscore-api .
docker run -p 8000:8000 highscore-api
```

### Production Considerations

1. Use PostgreSQL instead of SQLite
2. Set strong `SECRET_KEY` in environment
3. Enable HTTPS
4. Configure rate limiting
5. Set up monitoring and logging
6. Use a reverse proxy (nginx)

## 📝 License

MIT License - Feel free to use in your projects!

## ☕ Support

If you find this project helpful and want to support its development, consider buying me a coffee!

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/qulyubi)

Your support helps maintain and improve this project for the game development community!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ for game developers
