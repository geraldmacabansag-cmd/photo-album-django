# 📷 PhotoAlbum — Django Photo Album Management System

A production-ready Django application for managing photo albums with Role-Based Access Control (RBAC), Cloudinary media storage, and deployment on Render with PostgreSQL.

---

## 🔗 Deliverables

| Item | Link |
|------|------|
| **Live App** | *(add your Render URL here after deployment)* |
| **GitHub Repo** | *(add your GitHub repo URL here)* |

---

## ✨ Features

- **Full CRUD** for Albums and Photos via Class-Based Views
- **Role-Based Access Control** — two distinct roles enforced at the view layer:
  - **Standard User**: create albums, upload & manage their own photos
  - **Album Admin (Staff/Superuser)**: full access to every album and photo; Django admin panel
- **Cloudinary Integration** — all images stored and served via Cloudinary CDN; local media disabled in production
- **PostgreSQL** on Render (SQLite fallback for local dev)
- **Pagination** (12 albums per page), **search** by album name/description
- **Secure** — `DEBUG=False`, HTTPS enforced, CSRF protection, `WhiteNoise` for static files
- **Dark-mode UI** — responsive, no framework dependencies

---

## 🏗 Architecture

```
photo_album/              ← Django project
│
├── photo_album/          ← Core settings / URL router / WSGI
│   ├── settings.py       ← All config; reads from env vars
│   ├── urls.py
│   └── wsgi.py
│
├── albums/               ← Main application
│   ├── models.py         ← Album, Photo (CloudinaryField)
│   ├── views.py          ← Class-Based Views (ListView, DetailView, CreateView, …)
│   ├── mixins.py         ← RBAC enforcement (AlbumOwnerOrAdminMixin, PhotoOwnerOrAdminMixin)
│   ├── forms.py          ← AlbumForm, PhotoForm, RegisterForm
│   ├── urls.py
│   └── admin.py
│
├── templates/
│   ├── base.html         ← Nav, messages, shared CSS
│   ├── registration/     ← Login, Register
│   └── albums/           ← All album & photo templates
│
├── requirements.txt
├── build.sh              ← Render deploy script
└── .env.example
```

---

## 🔑 Role-Based Access Control

| Action | Anonymous | Standard User | Album Admin (Staff) |
|--------|-----------|--------------|---------------------|
| View login / register | ✅ | ✅ | ✅ |
| View own albums | ❌ | ✅ | ✅ |
| View **all** albums | ❌ | ❌ | ✅ |
| Create album | ❌ | ✅ | ✅ |
| Edit / Delete **own** album | ❌ | ✅ | ✅ |
| Edit / Delete **any** album | ❌ | ❌ | ✅ |
| Upload photo to own album | ❌ | ✅ | ✅ |
| Edit / Delete **own** photo | ❌ | ✅ | ✅ |
| Edit / Delete **any** photo | ❌ | ❌ | ✅ |
| Django admin panel | ❌ | ❌ | ✅ |

RBAC is implemented in `albums/mixins.py` using `LoginRequiredMixin` + ownership checks. Violation raises `PermissionDenied` (→ HTTP 403).

---

## 🛠 Class-Based Views

| View | CBV Base | Purpose |
|------|----------|---------|
| `AlbumListView` | `ListView` | Paginated list; staff see all, users see own |
| `AlbumCreateView` | `CreateView` | New album; auto-assigns `owner` |
| `AlbumDetailView` | `DetailView` | Album + photo grid |
| `AlbumUpdateView` | `UpdateView` | Edit album (owner/admin only) |
| `AlbumDeleteView` | `DeleteView` | Delete album + Cloudinary cleanup |
| `PhotoCreateView` | `CreateView` | Upload photo to an album |
| `PhotoUpdateView` | `UpdateView` | Edit photo metadata or replace image |
| `PhotoDeleteView` | `DeleteView` | Delete photo + Cloudinary cleanup |
| `RegisterView` | `FormView` | User registration |

---

## 🌩 Cloudinary Integration

- `CloudinaryField` on `Photo.image` (stores `public_id` + metadata in DB, not a file path)
- `STORAGES['default']` set to `cloudinary_storage.storage.MediaCloudinaryStorage` — all `ImageField` / `FileField` uploads route to Cloudinary automatically
- On delete, `cloudinary.uploader.destroy(photo.image.public_id)` removes the asset from Cloudinary's CDN to prevent orphaned files

---

## 🚀 Local Development

### 1. Clone & install

```bash
git clone <your-repo-url>
cd photo_album
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — fill in your Cloudinary credentials
```

Minimum `.env` for local dev:

```
SECRET_KEY=any-long-random-string
DEBUG=True
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 3. Run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`

---

## ☁️ Deploying to Render

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-url>
git push -u origin main
```

### Step 2 — Create a PostgreSQL database on Render

1. Render Dashboard → **New** → **PostgreSQL**
2. Give it a name, choose the free plan, click **Create Database**
3. Copy the **Internal Database URL**

### Step 3 — Create a Web Service on Render

1. Render Dashboard → **New** → **Web Service**
2. Connect your GitHub repo
3. Configure:

| Setting | Value |
|---------|-------|
| **Environment** | Python 3 |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn photo_album.wsgi:application` |

### Step 4 — Set Environment Variables on Render

In the web service **Environment** tab, add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | A long random string (generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DEBUG` | `False` |
| `DATABASE_URL` | Internal Database URL from Step 2 |
| `CLOUDINARY_CLOUD_NAME` | From [Cloudinary Console](https://cloudinary.com/console) |
| `CLOUDINARY_API_KEY` | From Cloudinary Console |
| `CLOUDINARY_API_SECRET` | From Cloudinary Console |
| `DJANGO_SUPERUSER_USERNAME` | `admin` (or your choice) |
| `DJANGO_SUPERUSER_EMAIL` | `admin@yourdomain.com` |
| `DJANGO_SUPERUSER_PASSWORD` | A strong password |

### Step 5 — Deploy

Click **Deploy**. Render will run `build.sh` (install, collectstatic, migrate, create superuser) then start Gunicorn.

> ⚠️ Keep your Render instance active during the grading period. Free-tier instances spin down after 15 minutes of inactivity; visit the URL to wake it up.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `Django 5.0` | Web framework |
| `cloudinary` + `django-cloudinary-storage` | Cloudinary SDK + Django storage backend |
| `dj-database-url` | Parse `DATABASE_URL` env var |
| `psycopg2-binary` | PostgreSQL adapter |
| `gunicorn` | Production WSGI server |
| `whitenoise` | Serve static files efficiently |
| `python-dotenv` | Load `.env` in development |
| `Pillow` | Image processing |

---

## 🔒 Security Checklist

- [x] `SECRET_KEY` from environment variable
- [x] `DEBUG=False` in production
- [x] `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` in production
- [x] No credentials in source code
- [x] `.env` in `.gitignore`
- [x] RBAC enforced at view layer (403 on violations)
- [x] CSRF tokens on all forms
- [x] Cloudinary credentials in env vars only

---

## 📄 License

MIT
