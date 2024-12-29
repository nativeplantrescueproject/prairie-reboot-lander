#!/usr/bin/env bash

set -e

. /venv/bin/activate

while ! flask
do
  echo "Retry..."
  sleep 3
done

exec gunicorn --bind 127.0.0.1:5000 --forwarded-allow-ips='*' --log-level=debug --workers=2 wsgi:app