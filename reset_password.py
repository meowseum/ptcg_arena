"""
Quick script to reset admin password
Run this in PythonAnywhere console if you can't log in
"""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='jeffpccy@gmail.com').first()

    if user:
        print(f"✓ Found user: {user.username}")

        # Set new password (change 'newpassword123' to your desired password)
        new_password = 'admin123456'
        user.set_password(new_password)
        db.session.commit()

        print(f"\n✓ Password reset successfully!")
        print(f"  Email: {user.email}")
        print(f"  New password: {new_password}")
        print(f"\n✓ You can now log in at: https://jeffpccy.pythonanywhere.com/auth/login")
    else:
        print("✗ User not found!")
