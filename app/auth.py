from flask import Blueprint, redirect, url_for, session, request, current_app, render_template, flash
from flask_login import login_user, logout_user, current_user, login_required
from authlib.integrations.flask_client import OAuth
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from app.models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth with app context"""
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('使用者名稱', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('電子郵件', validators=[DataRequired(), Email()])
    password = PasswordField('密碼', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('確認密碼', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('註冊')

class LoginForm(FlaskForm):
    email = StringField('電子郵件', validators=[DataRequired(), Email()])
    password = PasswordField('密碼', validators=[DataRequired()])
    submit = SubmitField('登入')

# Google OAuth Routes
@auth_bp.route('/login/google')
def login_google():
    """Redirect to Google OAuth"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info:
            flash('無法從 Google 獲取使用者資訊', 'danger')
            return redirect(url_for('main.index'))

        google_id = user_info['sub']
        email = user_info['email']
        username = user_info.get('name', email.split('@')[0])
        avatar = user_info.get('picture')

        # Find or create user
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                # Link Google account to existing user
                existing_user.google_id = google_id
                if not existing_user.avatar:
                    existing_user.avatar = avatar
                existing_user.last_login = datetime.utcnow()
                user = existing_user
            else:
                # Create new user
                user = User(
                    email=email,
                    google_id=google_id,
                    username=username,
                    avatar=avatar,
                    role='viewer',
                    email_verified=True  # Google emails are verified
                )
                db.session.add(user)
        else:
            # Update existing user
            user.username = username
            user.avatar = avatar
            user.last_login = datetime.utcnow()

        db.session.commit()

        # Log in the user
        login_user(user)
        flash(f'歡迎回來，{user.username}！', 'success')

        return redirect(url_for('main.index'))

    except Exception as e:
        current_app.logger.error(f"Google OAuth error: {e}")
        flash('登入失敗，請稍後再試', 'danger')
        return redirect(url_for('main.index'))

# Email/Password Routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with email/password"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('此電子郵件已被註冊', 'danger')
            return render_template('auth/register.html', form=form)

        # Create new user
        user = User(
            email=form.email.data,
            username=form.username.data,
            role='viewer'
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('註冊成功！請登入', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with email/password"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()

            flash(f'歡迎回來，{user.username}！', 'success')

            # Redirect to next page or home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('電子郵件或密碼錯誤', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    logout_user()
    flash('您已成功登出', 'info')
    return redirect(url_for('main.index'))
