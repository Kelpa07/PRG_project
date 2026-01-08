# Smart Eats - Django Restaurant Management System

A Django-based web application for restaurant order management with customer and admin dashboards.

## Features

- 🍽️ Menu browsing and ordering
- 👤 User authentication (Customer & Admin)
- 📱 Responsive design (mobile-friendly)
- 🛒 Shopping cart functionality
- 📊 Admin dashboard for order management
- 💳 Payment integration support
- 📸 Image uploads for menu items and profiles

## Tech Stack

- **Backend**: Django 6.0.1
- **Database**: SQLite (development)
- **Static Files**: WhiteNoise
- **Server**: Gunicorn (production)

## Quick Start

### Prerequisites

- Python 3.13+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd PRG_project/Gproject
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Homepage: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Project Structure

```
Gproject/
├── Gproject/          # Django project settings
│   ├── settings.py   # Main settings file
│   ├── urls.py       # URL configuration
│   └── wsgi.py       # WSGI configuration
├── ourproject/        # Main application
│   ├── models.py     # Database models
│   ├── views.py      # View functions
│   ├── urls.py       # App URLs
│   ├── templates/    # HTML templates
│   └── static/       # Static files (CSS, JS, images)
├── manage.py         # Django management script
├── requirements.txt  # Python dependencies
└── db.sqlite3        # SQLite database (not in git)
```

## Deployment

### ⚠️ Important: Netlify Limitation

**Netlify does NOT support Django applications** because Django requires a persistent Python server. Netlify is designed for static sites.

### Recommended Platforms

1. **Render** (Free tier available) - See `render.yaml`
2. **Railway** (Easy setup)
3. **Heroku** (Paid)
4. **PythonAnywhere** (Free tier available)

See `DEPLOYMENT.md` for detailed deployment instructions.

### Environment Variables

Set these in your hosting platform:

```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

### Pre-Deployment Steps

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Test deployment settings
python manage.py check --deploy
```

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

## Configuration

### Admin Signup Code

The admin signup code is set in `settings.py`:
```python
ADMIN_SIGNUP_CODE = '2025'  # Change this in production!
```

### Session Settings

- Sessions expire after 30 days
- Users stay logged in unless they log out

## Security Notes

- ⚠️ Change `SECRET_KEY` before deploying to production
- ⚠️ Set `DEBUG=False` in production
- ⚠️ Update `ALLOWED_HOSTS` with your domain
- ⚠️ Use environment variables for sensitive data

## License

This project is for educational purposes.

## Support

For deployment issues, refer to `DEPLOYMENT.md`.
