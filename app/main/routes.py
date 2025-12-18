"""
Main routes - home page and general pages
"""
from flask import render_template
from app.main import main_bp

@main_bp.route('/')
def index():
    """Home page with tournament highlights and top players"""
    # TODO: Fetch live and upcoming tournaments from database
    # TODO: Fetch top players by ELO
    return render_template('index.html',
                          live=[],
                          upcoming=[],
                          top_players=[])
