"""
Admin routes - to be implemented
"""
from flask import render_template
from flask_login import login_required
from app.admin import admin_bp
from app.decorators import admin_required

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # TODO: Implement admin dashboard
    return "<h1>Admin Dashboard - Coming Soon</h1>"
