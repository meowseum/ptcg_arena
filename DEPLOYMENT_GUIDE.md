# PTCG Arena Deployment Guide

## Prerequisites

- Python 3.8+ installed
- PythonAnywhere account (free tier works for testing)
- (Optional) Google Cloud account for OAuth

---

## Part 1: Google OAuth Setup (Optional)

**Note**: Google OAuth is optional! Users can register with email/password. Skip this part if you don't want OAuth.

### Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name it "PTCG Arena"
4. Click "Create"

### Step 2: Enable Google+ API

1. In the left sidebar, go to **"APIs & Services"** → **"Library"**
2. Search for "Google+ API"
3. Click it and press **"Enable"**

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** (unless you have Google Workspace)
3. Click **"Create"**
4. Fill in:
   - App name: **PTCG Arena**
   - User support email: Your email
   - Developer contact: Your email
5. Click **"Save and Continue"**
6. Skip "Scopes" (click "Save and Continue")
7. Add test users (your email) if needed
8. Click **"Save and Continue"**

### Step 4: Create OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Application type: **Web application**
4. Name: **PTCG Arena Web**
5. Add **Authorized redirect URIs**:
   - **Local testing**: `http://localhost:5000/auth/google/callback`
   - **Production**: `https://yourusername.pythonanywhere.com/auth/google/callback`
6. Click **"Create"**
7. Copy your **Client ID** and **Client Secret**

---

## Part 2: Local Development Setup

### Step 1: Install Dependencies

```bash
cd webapp
pip install -r requirements.txt
```

### Step 2: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env`:
   ```
   SECRET_KEY=your-random-secret-key-here

   # Optional - for Google OAuth
   GOOGLE_CLIENT_ID=your-client-id-from-google
   GOOGLE_CLIENT_SECRET=your-client-secret-from-google
   GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

   # Admin email (set this to your email)
   INITIAL_ADMIN_EMAIL=your@email.com
   ```

**Generate SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 3: Initialize Database

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### Step 4: Run Locally

```bash
python run.py
```

Visit http://localhost:5000

### Step 5: Create Admin Account

1. Register an account via the web interface
2. Then in Python console:

```python
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    user = User.query.filter_by(email='your@email.com').first()
    user.role = 'admin'
    db.session.commit()
exit()
```

---

## Part 3: PythonAnywhere Deployment

### Step 1: Sign Up

1. Go to https://www.pythonanywhere.com
2. Create a free "Beginner" account (or paid account for production)
3. Verify your email

### Step 2: Upload Code

#### Option A: Using Git (Recommended)

1. Push your `webapp` folder to GitHub (private repository recommended)
2. In PythonAnywhere, open a Bash console
3. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/yourrepo.git
   cd yourrepo/webapp
   ```

#### Option B: Using Upload

1. Compress your `webapp` folder to a ZIP file
2. In PythonAnywhere, go to "Files"
3. Upload the ZIP
4. Open a Bash console and extract:
   ```bash
   unzip webapp.zip
   cd webapp
   ```

### Step 3: Create Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.10 ptcg_env
pip install -r requirements.txt
```

### Step 4: Set Up Database

#### For Testing (SQLite)

```bash
python
>>> from app import create_app, db
>>> app = create_app('development')
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

#### For Production (PostgreSQL)

1. In PythonAnywhere, go to "Databases" tab
2. Set a database password
3. Note your database details:
   - Host: `yourusername.mysql.pythonanywhere-services.com`
   - Database name: `yourusername$ptcg`
4. Update environment variables in WSGI file (see Step 6)

### Step 5: Configure Web App

1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Choose Python 3.10

### Step 6: Configure WSGI File

1. Click on the WSGI configuration file link
2. Replace contents with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/webapp'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-secret-key-here'

# Optional - Google OAuth
os.environ['GOOGLE_CLIENT_ID'] = 'your-client-id'
os.environ['GOOGLE_CLIENT_SECRET'] = 'your-client-secret'
os.environ['GOOGLE_REDIRECT_URI'] = 'https://yourusername.pythonanywhere.com/auth/google/callback'

# For PostgreSQL (if using)
# os.environ['DATABASE_URL'] = 'postgresql://user:pass@host/db'

# Import Flask app
from app import create_app
from app.auth import init_oauth

application = create_app('production')
init_oauth(application)
```

### Step 7: Set Virtual Environment

1. In "Web" tab, find "Virtualenv" section
2. Enter: `/home/yourusername/.virtualenvs/ptcg_env`

### Step 8: Set Static Files

1. In "Web" tab, find "Static files" section
2. Add mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/webapp/static`

### Step 9: Reload Web App

1. Scroll to top of "Web" tab
2. Click the big green "Reload" button
3. Visit your site: `https://yourusername.pythonanywhere.com`

---

## Part 4: Initial Admin Setup

### Create First Admin User

1. Register an account on your deployed site
2. In a PythonAnywhere Bash console:

```bash
cd webapp
python
>>> from app import create_app, db
>>> from app.models import User
>>> app = create_app()
>>> with app.app_context():
...     user = User.query.filter_by(email='your@email.com').first()
...     user.role = 'admin'
...     db.session.commit()
>>> exit()
```

---

## Part 5: Testing Checklist

### Before Going Live

- [ ] Registration works (email/password)
- [ ] Login works (email/password)
- [ ] Google OAuth works (if configured)
- [ ] Admin can access admin panel
- [ ] Flash messages display correctly
- [ ] Logout works
- [ ] Mobile responsive design works

---

## Troubleshooting

### "Internal Server Error"

1. Check error logs:
   - PythonAnywhere: "Web" tab > "Log files" > "Error log"
2. Common issues:
   - Missing environment variables in WSGI file
   - Wrong virtualenv path
   - Database not initialized
   - Missing `SECRET_KEY`

### "Google OAuth Not Working"

1. Verify redirect URI matches exactly in Google Console
2. Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in WSGI file
3. Make sure Google+ API is enabled
4. Check OAuth consent screen is configured

### "Can't Register - Database Error"

1. Make sure you ran `db.create_all()`
2. Check database connection string
3. For SQLite, check file permissions

### "Static Files Not Loading"

1. Check static files mapping in "Web" tab
2. Verify path is correct: `/home/yourusername/webapp/static`
3. Clear browser cache
4. Check file permissions

### "Email Already Registered"

This is normal behavior - each email can only register once. Use a different email or login with existing account.

---

## Maintenance

### Updating Code

```bash
cd webapp
git pull  # If using Git
workon ptcg_env
pip install -r requirements.txt --upgrade
# Reload web app from "Web" tab
```

### Database Backup

```bash
cd webapp
# For SQLite
cp dev_ptcg.db dev_ptcg_backup.db

# For PostgreSQL
pg_dump database_name > backup.sql
```

### Monitoring

- Check error logs regularly in PythonAnywhere
- Monitor database size (free tier has limits)
- Watch for slow queries
- Monitor user registrations

---

## Scaling Beyond Free Tier

When you outgrow the free tier:

1. **Paid PythonAnywhere** ($5-12/month)
   - More CPU time
   - Always-on web app
   - PostgreSQL database
   - Custom domain

2. **Railway / Render** (Free tier available)
   - Better for larger communities
   - PostgreSQL included
   - Auto-deployments from Git
   - Easier scaling

3. **VPS** ($5+/month)
   - Full control
   - Requires more technical knowledge
   - Best for 100+ users

---

## User Roles Explained

| Role | Can Do |
|------|--------|
| **Viewer** | Browse tournaments, view leaderboard |
| **Player** | + Register for tournaments, view own profile |
| **Organizer** | + Create/manage tournaments, access admin panel |
| **Admin** | Full access including user management, deck database |

To promote users:
```python
user.role = 'player'  # or 'organizer' or 'admin'
db.session.commit()
```

---

## Security Best Practices

- ✅ Never commit `.env` file to Git
- ✅ Use strong `SECRET_KEY` (32+ characters)
- ✅ Keep Google Client Secret private
- ✅ Regularly update dependencies (`pip install --upgrade`)
- ✅ Use HTTPS in production (PythonAnywhere provides this)
- ✅ Set strong passwords for all admin accounts
- ✅ Monitor error logs for suspicious activity

---

## Success!

Your PTCG Arena should now be live! 🎉

### Next Steps:
1. Create your first tournament
2. Invite community members
3. Start tracking ELO ratings

For questions or issues, check:
- [README.md](README.md) - Project overview
- [QUICK_START.md](QUICK_START.md) - Local development guide
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Development roadmap
