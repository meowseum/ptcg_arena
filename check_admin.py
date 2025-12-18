"""
Quick script to check and set admin status
Run this in PythonAnywhere console to verify/fix admin access
"""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check current user
    user = User.query.filter_by(email='jeffpccy@gmail.com').first()

    if user:
        print(f"✓ Found user: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Current role: {user.role}")
        print(f"  is_admin(): {user.is_admin()}")
        print(f"  is_organizer(): {user.is_organizer()}")

        if user.role != 'admin':
            print(f"\n⚠ User is not admin! Setting to admin...")
            user.role = 'admin'
            db.session.commit()
            print(f"✓ User promoted to admin!")
        else:
            print(f"\n✓ User is already admin!")
    else:
        print("✗ User not found!")

    # List all users
    print("\n=== All Users ===")
    for u in User.query.all():
        print(f"  {u.id}: {u.username} ({u.email}) - Role: {u.role}")
