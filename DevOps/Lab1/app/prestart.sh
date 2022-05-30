#! /usr/bin/env sh

set -e

# Let the DB start
sleep 10;
# Run migrations
flask db upgrade