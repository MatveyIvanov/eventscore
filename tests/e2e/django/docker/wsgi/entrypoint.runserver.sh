#!/bin/bash

# if any of the commands fails for any reason, the entire script fails
set -o errexit

# fail exit if one of pipe command fails
set -o pipefail

# exits if any of variables is not set
set -o nounset

echo "[MIGRATE]"
python manage.py makemigrations --no-input
python manage.py migrate --no-input

echo "[RUN SERVER]"
python manage.py runserver 0.0.0.0:8000
