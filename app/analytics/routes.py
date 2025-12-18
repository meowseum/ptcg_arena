"""
Analytics routes
"""
from flask import render_template, request
from app.analytics import analytics_bp
from app.models import Player, Deck, ELOHistory, Tournament
from sqlalchemy import func

@analytics_bp.route('/leaderboard')
def leaderboard():
    """Display player leaderboard"""
    # Filter parameters
    status_filter = request.args.get('status', 'all')  # all, official, provisional
    min_games = int(request.args.get('min_games', 0))

    # Build query
    query = Player.query

    if status_filter == 'official':
        query = query.filter(Player.games_played >= 10)
    elif status_filter == 'provisional':
        query = query.filter(Player.games_played < 10)

    if min_games > 0:
        query = query.filter(Player.games_played >= min_games)

    # Order by ELO
    players = query.order_by(Player.elo.desc()).limit(100).all()

    # Deck leaderboard
    decks = Deck.query.filter(Deck.games_played >= 5).order_by(Deck.elo.desc()).limit(20).all()

    return render_template('analytics/leaderboard.html',
                          players=players,
                          decks=decks,
                          status_filter=status_filter,
                          min_games=min_games)

@analytics_bp.route('/profile/<int:player_id>')
def profile(player_id):
    """Display player profile"""
    player = Player.query.get_or_404(player_id)

    # Get ELO history
    elo_history = ELOHistory.query.filter_by(player_id=player_id).order_by(ELOHistory.timestamp.desc()).limit(50).all()

    # Get recent tournaments
    from app.models import TournamentPlayer
    tournament_participations = TournamentPlayer.query.filter_by(player_id=player_id).order_by(TournamentPlayer.id.desc()).limit(10).all()

    # Get deck usage statistics
    deck_stats = (
        TournamentPlayer.query
        .filter_by(player_id=player_id)
        .filter(TournamentPlayer.deck_id.isnot(None))
        .join(Deck)
        .with_entities(
            Deck.name,
            func.count(TournamentPlayer.id).label('times_used'),
            func.sum(TournamentPlayer.wins).label('total_wins'),
            func.sum(TournamentPlayer.losses).label('total_losses')
        )
        .group_by(Deck.name)
        .all()
    )

    return render_template('analytics/profile.html',
                          player=player,
                          elo_history=elo_history,
                          tournament_participations=tournament_participations,
                          deck_stats=deck_stats)
