#!/bin/sh
uv run manage.py migrate
# python manage.py shell < startup.py
uv run manage.py runserver 0.0.0.0:8000
