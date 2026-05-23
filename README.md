# 📦 MomentBox

A photo album management web app built with Django, Cloudinary, and PostgreSQL — deployed on Render.

---

## 🔗 Links

| | |
|---|---|
| **Live App** | *(https://momentbox-omuh.onrender.com/)* |
| **GitHub Repo** | *(https://github.com/geraldmacabansag-cmd/photo-album-django.git)* |

---

FEATURES

- Create and manage photo albums
- Upload photos stored on Cloudinary
- Role-based access — users manage their own albums; admins manage everything
- Search and paginate albums
- Secure production setup (HTTPS, environment variables, no hardcoded secrets)

---

TECH STACK

| Layer | Technology |
|---|---|
| Framework | Django 5.0 |
| Database | PostgreSQL (Render) |
| Media Storage | Cloudinary |
| Server | Gunicorn + WhiteNoise |
| Deployment | Render |

---

Running Locally

1. Clone and install**
```bash
git clone <your-repo-url>
cd photo_album
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Set up environment**
```bash
cp .env.example .env
# Fill in your Cloudinary credentials in .env
```

3. Run**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000`

---

Deploying to Render

1. Push code to GitHub
2. Create a **PostgreSQL** database on Render — copy the Internal Database URL
3. Create a **Web Service** on Render connected to your repo:
   - Build command: `./build.sh`
   - Start command: `gunicorn photo_album.wsgi:application`
4. Add these environment variables:

| Variable | Value |
|---|---|
| `SECRET_KEY` | Any long random string |
| `DEBUG` | `False` |
| `DATABASE_URL` | Internal Database URL from step 2 |
| `CLOUDINARY_CLOUD_NAME` | From Cloudinary dashboard |
| `CLOUDINARY_API_KEY` | From Cloudinary dashboard |
| `CLOUDINARY_API_SECRET` | From Cloudinary dashboard |
| `DJANGO_SUPERUSER_USERNAME` | Your admin username |
| `DJANGO_SUPERUSER_EMAIL` | Your admin email |
| `DJANGO_SUPERUSER_PASSWORD` | Your admin password |

5. Click **Deploy** — build runs automatically

---

## 👤 User Roles

| | Standard User | Admin (Staff) |
|---|---|---|
| View & manage own albums | ✅ | ✅ |
| View & manage all albums | ❌ | ✅ |
| Access Django admin panel | ❌ | ✅ |

---
