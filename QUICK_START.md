# PTCG Arena - Quick Start Guide

Get your local development environment running in 10 minutes!

---

## Prerequisites

- Python 3.8+ installed
- Code editor (VS Code, PyCharm, etc.)

---

## Step 1: Install Dependencies (2 min)

Open terminal in the `webapp` folder:

```bash
cd "c:\Users\Jeff\Desktop\Project_S\Gym Match\webapp"
pip install -r requirements.txt
```

Wait for installation to complete.

---

## Step 2: Configure Environment (1 min)

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` in your editor and set a secret key:
   ```
   SECRET_KEY=your-random-key-here
   ```

**Tip**: Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Note**: Google OAuth is optional! You can use email/password registration without setting up Google.

---

## Step 3: Initialize Database (2 min)

```bash
python
```

Then type:
```python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
exit()
```

You should see `dev_ptcg.db` file created.

---

## Step 4: Run the App (1 min)

```bash
python run.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

---

## Step 5: Register an Account! (1 min)

1. Open browser: http://localhost:5000
2. Click **"註冊"** (Register)
3. Fill in:
   - 使用者名稱 (Username)
   - 電子郵件 (Email)
   - 密碼 (Password - minimum 6 characters)
   - 確認密碼 (Confirm password)
4. Click **"註冊"** button
5. You'll be redirected to login page
6. Login with your email and password

---

## Step 6: Make Yourself Admin (1 min)

In Python console:

```bash
python
```

```python
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    # Replace with YOUR email address
    user = User.query.filter_by(email='your@email.com').first()
    user.role = 'admin'
    db.session.commit()
    print(f"✅ {user.username} is now an admin!")
exit()
```

Refresh the page - you should now see **"管理面板"** (Admin Panel) in navigation!

---

## (Optional) Step 7: Set Up Google OAuth

If you want to enable "Sign in with Google":

### Create Google OAuth App

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Go to **APIs & Services** → **Credentials**
4. Click **"Create Credentials"** → **"OAuth client ID"**
5. Application type: **Web application**
6. Name it: **"PTCG Arena Local"**
7. Add **Authorized redirect URI**: `http://localhost:5000/auth/google/callback`
8. Click **"Create"**
9. Copy your **Client ID** and **Client Secret**

### Configure in .env

Edit your `.env` file:
```
GOOGLE_CLIENT_ID=paste-your-client-id-here
GOOGLE_CLIENT_SECRET=paste-your-secret-here
```

Restart the app, and you'll see "使用 Google 登入" button!

---

## 🎉 Success!

You're now running PTCG Arena locally!

### What Works Now:
- ✅ Landing page
- ✅ Email/password registration
- ✅ Email/password login
- ✅ Google OAuth login (if configured)
- ✅ User roles

### What's Still Being Built:
- ⏳ Tournament creation & management
- ⏳ Player profiles & leaderboard
- ⏳ Admin panel features

---

## Next Steps

### Option 1: Explore the Code
- Check out [models.py](app/models.py) - database structure
- Look at [pairing.py](app/tournament/pairing.py) - Swiss algorithm
- See [elo_calculator.py](app/analytics/elo_calculator.py) - ELO logic

### Option 2: Continue Development
See [PROJECT_STATUS.md](PROJECT_STATUS.md) for what needs to be implemented next.

### Option 3: Deploy It
When ready, follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) to deploy to PythonAnywhere.

---

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Can't register - email already exists"
That email is already in database. Use a different email or login with existing account.

### "Database Error"
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.drop_all()
...     db.create_all()
```

### "Port 5000 Already in Use"
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or just change port in run.py
```

### "Google OAuth Not Working"
- Make sure you set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
- Verify redirect URI is exactly `http://localhost:5000/auth/google/callback` in Google Console
- Restart the app after changing `.env`

---

## Getting Help

1. Check [README.md](README.md) for project overview
2. See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed setup
3. Review [PROJECT_STATUS.md](PROJECT_STATUS.md) for current progress

---

Happy coding! 🚀
