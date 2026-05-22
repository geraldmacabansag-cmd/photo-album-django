#!/usr/bin/env bash
# Render build script — runs on every deploy
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Auto-create superuser from env vars (safe to re-run — exits 0 if already exists)
python manage.py createsuperuser --noinput || true
