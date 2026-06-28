# SocialHub – Mini Social Media App
A full-featured social media platform built with Django + HTML/CSS/JS.

## Features
- ✅ User registration & login
- ✅ User profiles with avatar, bio, website
- ✅ Create / delete posts (with optional image)
- ✅ Comments (inline AJAX on feed, full view on post detail)
- ✅ Like / unlike posts (real-time, no page reload)
- ✅ Follow / unfollow users (real-time)
- ✅ Home feed (posts from followed users)
- ✅ Search users and posts
- ✅ Followers / Following lists


---

## Project Structure

```
socialmedia/
├── manage.py
├── requirements.txt
├── db.sqlite3              ← created automatically
├── media/                  ← uploaded images stored here
├── socialmedia/            ← Django project config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── social/                 ← Main app
    ├── __init__.py
    ├── admin.py
    ├── forms.py
    ├── models.py
    ├── urls.py
    ├── views.py
    ├── migrations/
    │   └── __init__.py
    ├── templates/social/
    │   ├── base.html
    │   ├── login.html
    │   ├── register.html
    │   ├── feed.html
    │   ├── profile.html
    │   ├── edit_profile.html
    │   ├── post_detail.html
    │   ├── search.html
    │   ├── followers.html
    │   └── partials/
    │       └── post_card.html
    └── static/social/
        ├── css/main.css
        └── js/main.js
```

---

## Setup Instructions

### Step 1 – Install Python
Make sure Python 3.10+ is installed.
```bash
python --version
```

### Step 2 – Create a virtual environment
```bash
cd socialmedia
python -m venv venv
```

### Step 3 – Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 – Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5 – Create an admin superuser (optional)
```bash
python manage.py createsuperuser
```

### Step 6 – Start the development server
```bash
python manage.py runserver
```

### Step 7 – Open in browser
- App: http://127.0.0.1:8000/

