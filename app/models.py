from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User accounts for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # Authentication methods
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Null if OAuth only
    google_id = db.Column(db.String(100), unique=True, nullable=True)

    # Profile
    username = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(200))

    # Authorization
    role = db.Column(db.String(20), default='viewer')  # viewer, player, organizer, admin

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)

    # Relationships
    organized_tournaments = db.relationship('Tournament', backref='organizer', lazy=True)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_organizer(self):
        return self.role in ['organizer', 'admin']

    def is_player(self):
        return self.role in ['player', 'organizer', 'admin']

class Season(db.Model):
    """Tournament seasons"""
    __tablename__ = 'seasons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tournaments = db.relationship('Tournament', backref='season', lazy=True)

class Player(db.Model):
    """Players in tournaments (separate from user accounts)"""
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # ELO Stats
    elo = db.Column(db.Float, default=1500.0)
    peak_elo = db.Column(db.Float, default=1500.0)
    games_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    ties = db.Column(db.Integer, default=0)

    # Radar Attributes (0-100)
    skill = db.Column(db.Float, default=50.0)
    consistency = db.Column(db.Float, default=50.0)
    experience = db.Column(db.Float, default=0.0)
    clutch = db.Column(db.Float, default=50.0)
    top_cut = db.Column(db.Float, default=0.0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='player_profile')

    @property
    def win_rate(self):
        if self.games_played == 0:
            return 0.0
        return self.wins / self.games_played

    @property
    def adjusted_win_rate(self):
        """Bayesian adjusted win rate"""
        return (self.wins + 3) / (self.games_played + 6)

    @property
    def status(self):
        return "Official" if self.games_played >= 10 else "Provisional"

class Deck(db.Model):
    """Deck database with hierarchical structure"""
    __tablename__ = 'decks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=True)

    # Nature tags (comma-separated)
    natures = db.Column(db.String(200))  # "Meta Deck,Box Deck"

    # Stats
    elo = db.Column(db.Float, default=1500.0)
    games_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    parent = db.relationship('Deck', remote_side=[id], backref='variants')

    @property
    def win_rate(self):
        if self.games_played == 0:
            return 0.0
        return self.wins / self.games_played

    def get_nature_list(self):
        if not self.natures:
            return []
        return [n.strip() for n in self.natures.split(',')]

class Tournament(db.Model):
    """Tournament instances"""
    __tablename__ = 'tournaments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'), nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Tournament settings
    mode = db.Column(db.String(20), default='normal')  # normal or bo3
    draw_points = db.Column(db.Integer, default=0)  # 0 or 1

    # Status
    status = db.Column(db.String(20), default='upcoming')  # upcoming, live, completed
    current_round = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    participants = db.relationship('TournamentPlayer', backref='tournament', lazy=True, cascade='all, delete-orphan')
    matches = db.relationship('Match', backref='tournament', lazy=True, cascade='all, delete-orphan')

class TournamentPlayer(db.Model):
    """Player participation in a specific tournament"""
    __tablename__ = 'tournament_players'

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=True)

    # Tournament-specific stats
    points = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    ties = db.Column(db.Integer, default=0)
    byes = db.Column(db.Integer, default=0)

    # BO3 specific
    game_wins = db.Column(db.Integer, default=0)
    game_losses = db.Column(db.Integer, default=0)
    is_tardy = db.Column(db.Boolean, default=False)

    # Dropped from tournament
    dropped = db.Column(db.Boolean, default=False)
    dropped_round = db.Column(db.Integer, nullable=True)

    # Relationships
    player = db.relationship('Player', backref='tournament_participations')
    deck = db.relationship('Deck', backref='tournament_usages')

class Match(db.Model):
    """Match records"""
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)

    player1_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'), nullable=True)  # Null for bye

    # Result: 'player1', 'player2', 'draw', 'double_loss', 'bye'
    result = db.Column(db.String(20), nullable=True)

    # BO3 game scores
    p1_game_wins = db.Column(db.Integer, default=0)
    p2_game_wins = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    player1 = db.relationship('TournamentPlayer', foreign_keys=[player1_id], backref='matches_as_p1')
    player2 = db.relationship('TournamentPlayer', foreign_keys=[player2_id], backref='matches_as_p2')

class ELOHistory(db.Model):
    """Track ELO changes over time"""
    __tablename__ = 'elo_history'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=True)

    elo_before = db.Column(db.Float, nullable=False)
    elo_after = db.Column(db.Float, nullable=False)
    elo_change = db.Column(db.Float, nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    player = db.relationship('Player', backref='elo_history')
    match = db.relationship('Match', backref='elo_records')
    tournament = db.relationship('Tournament', backref='elo_changes')
