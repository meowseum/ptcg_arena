# PTCG Arena - Unified Tournament Platform

A comprehensive web platform merging Swiss tournament management and PTCG ELO analytics into a single community-driven application.

## Features

### Tournament Management (from Swiss)
- ✅ Swiss pairing algorithm with rematch prevention
- ✅ Real-time standings with OMW/OOWP tiebreakers
- ✅ Timer system for rounds
- ✅ Match result recording
- ✅ Bye handling for odd player counts
- ✅ BO3 and Normal tournament modes

### Analytics (from PTCG_Stat)
- ✅ ELO rating system for players
- ✅ Deck ELO tracking
- ✅ Radar chart attributes (Skill, Consistency, Experience, Clutch, Top Cut)
- ✅ Season management
- ✅ Match history and statistics
- ✅ Dashboard with meta analysis

### Community Features (New)
- ✅ Discord OAuth authentication
- ✅ Role-based access control (Viewer/Player/Organizer/Admin)
- ✅ Player profiles with tournament history
- ✅ Public tournament listings
- ✅ Gaming/esports themed UI

## Tech Stack

- **Backend**: Flask (Python 3.8+)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: Discord OAuth via Authlib
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Hosting**: PythonAnywhere (recommended) / Railway / Render

## Quick Start

### 1. Clone and Install

```bash
cd webapp
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
# Edit .env with your Discord OAuth credentials
```

### 3. Initialize Database

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

### 4. Run

```bash
python run.py
```

Visit http://localhost:5000

## Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions for PythonAnywhere and other hosting platforms.

## Project Structure

```
webapp/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models.py             # SQLAlchemy models
│   ├── auth.py               # Discord OAuth
│   ├── decorators.py         # Role-based access control
│   ├── main.py               # Main blueprint
│   ├── tournament/           # Tournament module (Swiss)
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── pairing.py        # Swiss pairing algorithm
│   ├── analytics/            # Analytics module (PTCG_Stat)
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── elo_calculator.py # ELO calculations
│   ├── admin/                # Admin panel
│   ├── templates/            # Jinja2 templates
│   └── static/               # CSS, JS, images
│       ├── css/
│       │   └── main.css      # Gaming/esports theme
│       └── js/
├── tests/                    # Test suite
├── config.py                 # Configuration
├── requirements.txt          # Python dependencies
├── run.py                    # Entry point
└── DEPLOYMENT_GUIDE.md       # Deployment instructions
```

## Original Codebases

This project is a merger of two existing systems:

- **Swiss** ([Swiss/](../Swiss/)) - Tournament pairing system v10.0
- **PTCG_Stat** ([PTCG_Stat/](../PTCG_Stat/)) - ELO analytics system

**Important**: The original folders are **NOT modified** and serve as reference only. All new code is in [webapp/](.)

## Testing

Run tests to verify ported functions match original behavior:

```bash
pytest tests/ -v
```

## Database Schema

### Key Models

- **User** - Discord authenticated users with roles
- **Player** - Tournament players with ELO stats
- **Tournament** - Tournament instances
- **TournamentPlayer** - Player participation in specific tournaments
- **Match** - Match records with results
- **ELOHistory** - Track ELO changes over time
- **Deck** - Hierarchical deck database
- **Season** - Tournament seasons

## User Roles

| Role | Permissions |
|------|-------------|
| **Viewer** | View public tournaments, leaderboard |
| **Player** | + Register for tournaments, view own profile |
| **Organizer** | + Create/manage tournaments, access admin panel |
| **Admin** | Full access including deck database, user management |

## Configuration

Edit `.env` for local development:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DISCORD_CLIENT_ID=your-discord-client-id
DISCORD_CLIENT_SECRET=your-discord-client-secret
DISCORD_REDIRECT_URI=http://localhost:5000/auth/callback
DATABASE_URL=sqlite:///dev_ptcg.db
```

## Contributing

This is a consolidation project. Future contributions should:

1. Not modify original Swiss or PTCG_Stat folders
2. Follow existing code style
3. Include tests for new features
4. Update documentation

## License

See original projects for licensing information.

## Acknowledgments

- **Swiss v10.0** - Tournament pairing system
- **PTCG_Stat** - ELO analytics system
- Community feedback and testing

---

## Development Status

### Phase 1: Foundation ✅
- [x] Project structure
- [x] Database models
- [x] Discord OAuth
- [x] Role-based access
- [x] Gaming/esports UI theme

### Phase 2: Core Modules (In Progress)
- [x] Swiss pairing algorithm ported
- [x] ELO calculator ported
- [ ] Tournament routes and templates
- [ ] Analytics routes and templates
- [ ] Admin panel

### Phase 3: Integration (Upcoming)
- [ ] Tournament → ELO auto-calculation
- [ ] Season management
- [ ] Historical data import

### Phase 4: Polish (Upcoming)
- [ ] Mobile responsive adjustments
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Production deployment

---

For support and questions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).
