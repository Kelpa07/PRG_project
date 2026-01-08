# Deployment Guide for Smart Eats Django Application

## ⚠️ Important Note About Netlify

**Netlify is NOT recommended for Django applications** because:
- Netlify is designed for static sites and serverless functions
- Django requires a persistent Python server (WSGI/ASGI)
- Netlify doesn't support long-running processes needed for Django

## ✅ Recommended Deployment Platforms

### Option 1: Render (Recommended - Free Tier Available)
1. Sign up at https://render.com
2. Connect your GitHub repository
3. Create a new Web Service
4. Use the `render.yaml` file included in this project
5. Set environment variables in Render dashboard:
   - `SECRET_KEY`: Generate a secure key
   - `DEBUG`: Set to `False`
   - `ALLOWED_HOSTS`: Your Render URL (e.g., `smart-eats.onrender.com`)

### Option 2: Railway (Easy Setup)
1. Sign up at https://railway.app
2. Connect your GitHub repository
3. Railway will auto-detect Django
4. Set environment variables:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app.railway.app`

### Option 3: Heroku (Paid)
1. Sign up at https://heroku.com
2. Install Heroku CLI
3. Run: `heroku create your-app-name`
4. Deploy: `git push heroku main`
5. Set environment variables via Heroku dashboard

## 📋 Pre-Deployment Checklist

- [ ] Update `SECRET_KEY` in environment variables (never commit it!)
- [ ] Set `DEBUG=False` in production
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Run `python manage.py collectstatic`
- [ ] Run `python manage.py migrate`
- [ ] Test locally with `DEBUG=False`

## 🚀 Local Testing Before Deployment

```bash
# Activate virtual environment
cd Gproject
.\Gproject\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source Gproject/venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Test with production settings
set DEBUG=False  # Windows
export DEBUG=False  # Linux/Mac
python manage.py runserver
```

## 🔧 Environment Variables

Create a `.env` file (DO NOT commit this) or set in your hosting platform:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

## 📝 If You Must Use Netlify

If you absolutely need to use Netlify, you would need to:
1. Convert Django to a serverless architecture (very complex)
2. Use Netlify Functions (limited support)
3. Consider using a headless CMS approach

**Better alternative**: Deploy Django backend on Render/Railway and use Netlify for a separate frontend if needed.

## 🐛 Troubleshooting

### Static files not loading?
- Run `python manage.py collectstatic --noinput`
- Check `STATIC_ROOT` is set correctly
- Verify WhiteNoise middleware is in `MIDDLEWARE`

### Database errors?
- Run `python manage.py migrate`
- Check database connection settings

### 500 errors?
- Check `DEBUG=True` temporarily to see error details
- Review server logs
- Verify all environment variables are set
