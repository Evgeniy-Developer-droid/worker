#!/bin/sh
# wait-for-postgres.sh
apt-get update; apt-get install -y curl
set -e

until curl http://web:5000/status; do
  >&2 echo "sleeping"
  sleep 1
done

>&2 echo "Executing command"
exec "$@"