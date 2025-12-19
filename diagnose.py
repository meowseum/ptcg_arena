"""
Diagnostic script to check PythonAnywhere deployment
Run this in PythonAnywhere Bash console to verify everything is set up correctly
"""
import os
import sys

print("=== PTCG Arena Deployment Diagnostics ===\n")

# 1. Check Python version
print(f"1. Python version: {sys.version}\n")

# 2. Check current directory
print(f"2. Current directory: {os.getcwd()}\n")

# 3. Check if app directory exists
app_path = "/home/jeffpccy/ptcg_arena/app"
print(f"3. App directory exists: {os.path.exists(app_path)}")
if os.path.exists(app_path):
    print(f"   Contents: {os.listdir(app_path)}\n")

# 4. Check templates directory
templates_path = "/home/jeffpccy/ptcg_arena/app/templates"
print(f"4. Templates directory exists: {os.path.exists(templates_path)}")
if os.path.exists(templates_path):
    print(f"   Contents: {os.listdir(templates_path)}")

    # Check admin templates
    admin_path = f"{templates_path}/admin"
    if os.path.exists(admin_path):
        print(f"   Admin templates: {os.listdir(admin_path)}")

    # Check tournament templates
    tournament_path = f"{templates_path}/tournament"
    if os.path.exists(tournament_path):
        print(f"   Tournament templates: {os.listdir(tournament_path)}")
    print()

# 5. Try importing the app
print("5. Testing app import...")
try:
    sys.path.insert(0, '/home/jeffpccy/ptcg_arena')
    from app import create_app, db
    from app.models import User

    print("   ✓ App imports successfully")

    # 6. Create app and check admin user
    print("\n6. Checking admin user...")
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email='jeffpccy@gmail.com').first()
        if user:
            print(f"   ✓ User found: {user.username}")
            print(f"   ✓ Role: {user.role}")
            print(f"   ✓ is_admin(): {user.is_admin()}")
            print(f"   ✓ is_organizer(): {user.is_organizer()}")
        else:
            print("   ✗ User not found!")

    # 7. Check routes
    print("\n7. Registered routes:")
    with app.app_context():
        routes = []
        for rule in app.url_map.iter_rules():
            if 'admin' in rule.rule or 'tournament' in rule.rule:
                routes.append(f"   {rule.rule} -> {rule.endpoint}")
        for route in sorted(routes):
            print(route)

    print("\n✓ Diagnostics complete!")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
