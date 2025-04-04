#!/usr/bin/env bash
# exit on error
set -o errexit

python3 pip install -r requirements.txt
python3 manage.py collectstatic --no-input