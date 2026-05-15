release: python Reserv/manage.py migrate --noinput
web: gunicorn Reserv.wsgi:application --chdir Reserv --bind 0.0.0.0:$PORT --workers 1
