release: python manage.py migrate --noinput
web: python manage.py migrate --noinput && gunicorn Hotel.wsgi:application --bind 0.0.0.0:$PORT --workers 1
