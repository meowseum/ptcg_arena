# Changelog

All notable changes to PTCG Arena will be documented in this file.

## [Unreleased]

### Phase 2: Core Implementation (In Progress)
- Tournament routes and templates
- Analytics routes and templates
- Admin panel implementation

## [0.1.0] - 2025-12-19

### Added - Foundation Release

#### Project Structure
- Created complete webapp folder structure with organized modules
- Set up Flask application factory pattern
- Configured development, production, and testing environments
- Added comprehensive .gitignore for Python projects

#### Database Models
- User model with Discord profile integration
- Player model with ELO statistics (elo, peak_elo, games_played, wins, losses)
- Tournament model with mode support (normal/BO3) and status tracking
- TournamentPlayer model for tournament participation
- Match model with result tracking and game scores
- Deck model with hierarchical structure and nature tags
- Season model for organizing tournaments
- ELOHistory model for tracking rating changes over time

#### Authentication & Authorization
- Discord OAuth integration via Authlib
- User registration and login flow
- Role-based access control system (Viewer/Player/Organizer/Admin)
- Custom decorators: @admin_required, @organizer_required, @player_required
- Session management with secure cookies

#### Swiss Tournament System (Ported from Swiss/main.py)
- PairingEngine class with comprehensive pairing logic
- Recursive backtracking algorithm for rematch-free pairings
- Bye assignment system (prefers players with zero previous byes)
- OMW (Opponent Match Win %) calculation with 25% floor
- OOWP (Opponent's Opponent Win %) calculation
- Score group handling and adjacency-based pairing
- Support for both Normal and BO3 tournament modes
- Minimal rematch fallback strategy when perfect pairing impossible

#### ELO Rating System (Ported from PTCG_Stat/elo_calculator.py)
- ELOCalculator class with player and deck ELO tracking
- Experience-based K-factors (40/24/16 for new/established/veteran)
- Expected score calculation using standard ELO formula
- Match-by-match ELO change tracking
- Peak ELO tracking for players
- Double loss penalty handling (-8 points)
- Deck ELO calculation with fixed K-factor (24)
- Radar chart attributes: Skill, Consistency, Experience, Clutch, Top Cut
- Tournament-wide ELO recalculation system

#### Frontend Design
- Gaming/esports themed CSS with electric blue (#00D9FF) and neon accents
- Dark theme with purple (#9D4EDD) and pink (#FF006E) highlights
- Card-based layout system with hover animations
- Gradient text effects for headings
- Glow effects on buttons and interactive elements
- Animated background with radial gradients
- Responsive grid system (2-column and 3-column)
- Tournament status badges (live/upcoming/completed) with animations
- Navigation bar with role-based menu items
- Mobile-responsive design (media queries for <768px)

#### Templates
- base.html: Base template with navigation and flash messages
- index.html: Landing page with hero section, tournament listings, and top players
- Component-ready structure for future pages

#### Configuration
- Environment variable management with python-dotenv
- Multiple configuration classes (Development/Production/Testing)
- Database URL configuration for SQLite and PostgreSQL
- Discord OAuth settings
- Session security settings

#### Documentation
- README.md: Comprehensive project overview
- DEPLOYMENT_GUIDE.md: Step-by-step PythonAnywhere deployment (300+ lines)
- PROJECT_STATUS.md: Current progress and roadmap
- QUICK_START.md: 10-minute setup guide for local development
- CHANGELOG.md: This file
- Inline code documentation with docstrings

#### Testing
- Test structure with pytest configuration
- test_elo_calculator.py: Unit tests for ELO logic
  - K-factor threshold tests
  - Expected score calculation tests
  - ELO change symmetry tests
  - Parameter validation tests
- test_pairing.py: Test stubs for Swiss pairing algorithm

#### Dependencies
- Flask 3.0.0 - Web framework
- Flask-SQLAlchemy 3.1.1 - ORM
- Flask-Login 0.6.3 - User session management
- Flask-WTF 1.2.1 - Form handling
- psycopg2-binary 2.9.9 - PostgreSQL adapter
- python-dotenv 1.0.0 - Environment variables
- requests 2.31.0 - HTTP library
- Authlib 1.3.0 - OAuth integration
- gunicorn 21.2.0 - WSGI server
- pytest 7.4.3 - Testing framework
- pytest-flask 1.3.0 - Flask testing utilities

#### Developer Tools
- .env.example template with all required variables
- requirements.txt for dependency management
- run.py entry point for local development
- Comprehensive error handling structure

### Code Statistics
- Total Lines of Code: ~2000+
- Models: 450+ lines (9 models)
- Swiss Pairing: 300+ lines
- ELO Calculator: 350+ lines
- CSS Theme: 400+ lines
- Documentation: 1000+ lines

### Original Codebases Referenced
- Swiss v10.0 - Tournament pairing system
- PTCG_Stat Season 3 - ELO analytics system

**Note**: Original folders (Swiss/ and PTCG_Stat/) remain unmodified and serve as reference only.

---

## Future Versions

### [0.2.0] - Planned
- Tournament CRUD routes
- Live tournament management interface
- Match result recording system
- Real-time standings display

### [0.3.0] - Planned
- Analytics dashboard
- Player profile pages
- Leaderboard with filters
- Season statistics

### [0.4.0] - Planned
- Admin panel
- User role management
- Deck database management
- Data import/export tools

### [1.0.0] - Planned (MVP)
- Full tournament management
- Complete analytics system
- Admin tools
- Production deployment
- Mobile responsive
- Comprehensive testing

---

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- MAJOR version: Incompatible API changes
- MINOR version: New functionality (backwards compatible)
- PATCH version: Bug fixes (backwards compatible)

## Contributing

See [README.md](README.md) for contribution guidelines.

---

**Legend**:
- `Added`: New features
- `Changed`: Changes in existing functionality
- `Deprecated`: Soon-to-be removed features
- `Removed`: Now removed features
- `Fixed`: Bug fixes
- `Security`: Vulnerability fixes
