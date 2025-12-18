"""
Admin routes
"""
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.decorators import admin_required
from app.models import db, User, Tournament, Player, Match

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    total_users = User.query.count()
    total_tournaments = Tournament.query.count() if hasattr(db.Model, 'Tournament') else 0
    total_players = Player.query.count() if hasattr(db.Model, 'Player') else 0
    total_matches = Match.query.count() if hasattr(db.Model, 'Match') else 0

    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all() if hasattr(User, 'created_at') else []

    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_tournaments=total_tournaments,
                          total_players=total_players,
                          total_matches=total_matches,
                          recent_users=recent_users)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users"""
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/user/<int:user_id>/promote/<role>')
@login_required
@admin_required
def promote_user(user_id, role):
    """Promote user to a specific role"""
    if role not in ['viewer', 'player', 'organizer', 'admin']:
        flash('Invalid role', 'error')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)
    user.role = role
    db.session.commit()
    flash(f'{user.username} promoted to {role}', 'success')
    return redirect(url_for('admin.users'))
