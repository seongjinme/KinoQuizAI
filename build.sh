#!/bin/bash

echo "Start building KinoQuizAI..."
python3.9 -m pip install -r requirements.txt

echo "Start migrations..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear

echo "Building complete."
