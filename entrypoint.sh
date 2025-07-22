#!/bin/bash
set -e

PW_FILE="/app/.django-superuser-pw"

if [ ! -f "$PW_FILE" ]; then
    export DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 16)
    echo "$DJANGO_SUPERUSER_PASSWORD" > $PW_FILE
    echo ""
    echo "*********************************"
    echo "Superuser Django password generated: $(cat $PW_FILE)"
    echo "Saved in /app/.django-superuser-pw"
    echo "*********************************"
else
    export DJANGO_SUPERUSER_PASSWORD=$(cat $PW_FILE)
fi

poetry run python manage.py migrate --noinput

poetry run python manage.py createsuperuser \
    --noinput \
    --username $DJANGO_SUPERUSER_USERNAME \
    --email $DJANGO_SUPERUSER_EMAIL || true

poetry run python manage.py runserver 0.0.0.0:8000
