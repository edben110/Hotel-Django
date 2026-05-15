release: python manage.py migrate --noinput
web: gunicorn Hotel.wsgi:application --bind 0.0.0.0:$PORT --workers 1
