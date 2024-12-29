#!/usr/bin/env bash

set -e

. /venv/bin/activate

while ! flask
do
  echo "Retry..."
  sleep 3
done

exec gunicorn --bind 0.0.0.0:5000 --forwarded-allow-ips='*' wsgi:app