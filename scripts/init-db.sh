#!/bin/bash
set -euo pipefail

DEV_DB="${POSTGRES_DB:-helpcenter_devdb}"
TEST_DB="${POSTGRES_DB_TEST:-helpcenter_testdb}"

create_db_if_missing() {
  local db="$1"
  echo "Ensuring database: $db"
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
    -tc "SELECT 1 FROM pg_database WHERE datname = '$db'" | grep -q 1 || \
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
      -c "CREATE DATABASE $db OWNER $POSTGRES_USER;"
}

create_db_if_missing "$DEV_DB"
create_db_if_missing "$TEST_DB"