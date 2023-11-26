#!/bin/bash

while ! nc -z db 5432;
    do sleep .5;
    echo "wait database";
done;
    echo "connected to the database";

python manage.py makemigrations users;
python manage.py makemigrations recipes;
python manage.py migrate;
python manage.py loaddata transformed_ingredients.json;
python manage.py custom_createsuperuser;
python manage.py collectstatic --noinput;
gunicorn -w 2 -b 0:8000 foodgram_backend.wsgi;
