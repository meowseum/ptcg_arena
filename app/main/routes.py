"""
Main routes - home page and general pages
"""
from flask import render_template, jsonify
from flask_login import current_user
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

@main_bp.route('/debug/user')
def debug_user():
    """Debug route to check current user session"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role,
            'is_admin': current_user.is_admin(),
            'is_organizer': current_user.is_organizer(),
            'is_player': current_user.is_player()
        })
    else:
        return jsonify({
            'authenticated': False,
            'message': 'Not logged in'
        })
