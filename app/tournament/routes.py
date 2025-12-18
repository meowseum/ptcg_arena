"""
Tournament routes - to be implemented
"""
from flask import render_template, redirect, url_for
from app.tournament import tournament_bp

@tournament_bp.route('/list')
def list():
    """List all tournaments"""
    # TODO: Implement tournament listing
    return "<h1>Tournament List - Coming Soon</h1>"

@tournament_bp.route('/<int:tournament_id>')
def view(tournament_id):
    """View tournament details"""
    # TODO: Implement tournament view
    return f"<h1>Tournament {tournament_id} - Coming Soon</h1>"
