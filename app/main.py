from flask import Blueprint, render_template
from flask_login import current_user
from app.models import Tournament, Player
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page with tournament highlights"""
    upcoming_tournaments = Tournament.query.filter_by(status='upcoming').order_by(Tournament.date).limit(3).all()
    live_tournaments = Tournament.query.filter_by(status='live').all()
    top_players = Player.query.order_by(desc(Player.elo)).limit(5).all()

    return render_template('index.html',
                         upcoming=upcoming_tournaments,
                         live=live_tournaments,
                         top_players=top_players)

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')
