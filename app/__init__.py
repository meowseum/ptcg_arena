from flask import Flask
from flask_login import LoginManager
from config import config
from app.models import db, User

login_manager = LoginManager()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.tournament import tournament_bp
    from app.analytics import analytics_bp
    from app.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(tournament_bp, url_prefix='/tournament')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Register error handlers
    from flask import render_template, redirect, url_for

    @app.errorhandler(401)
    def unauthorized(e):
        """Handle unauthorized access"""
        return redirect(url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden(e):
        """Handle forbidden access"""
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        """Handle page not found"""
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        """Handle internal server error"""
        return render_template('errors/500.html'), 500

    # Create tables
    with app.app_context():
        db.create_all()

    return app
