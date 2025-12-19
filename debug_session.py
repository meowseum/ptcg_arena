"""
Debug script to check user session and role
Run this to see what Flask-Login is seeing
"""
from app import create_app, db
from app.models import User
from flask import session

app = create_app()

with app.app_context():
    # Check database
    user = User.query.filter_by(email='jeffpccy@gmail.com').first()

    if user:
        print("=== DATABASE CHECK ===")
        print(f"User ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role (raw): '{user.role}'")
        print(f"is_admin(): {user.is_admin()}")
        print(f"is_organizer(): {user.is_organizer()}")
        print(f"is_player(): {user.is_player()}")

        # Check for weird characters or whitespace
        print(f"\nRole debug:")
        print(f"  Length: {len(user.role)}")
        print(f"  Repr: {repr(user.role)}")
        print(f"  Bytes: {user.role.encode('utf-8')}")
        print(f"  Equals 'admin': {user.role == 'admin'}")

        # Fix if needed
        if user.role.strip() != 'admin':
            print(f"\n⚠ Role has whitespace or wrong value!")
            print(f"Fixing role to 'admin'...")
            user.role = 'admin'
            db.session.commit()
            print(f"✓ Fixed!")
    else:
        print("✗ User not found!")

    # Check all users
    print("\n=== ALL USERS ===")
    for u in User.query.all():
        print(f"{u.id}: {u.username} - role='{u.role}' (is_admin={u.is_admin()})")
