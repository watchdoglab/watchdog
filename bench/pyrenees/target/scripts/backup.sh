#!/usr/bin/env bash
set -euo pipefail
STAMP=$(date +%F)
pg_dump "$DATABASE_URL" | gzip > "/tmp/ledgerly-$STAMP.sql.gz"
aws s3 cp "/tmp/ledgerly-$STAMP.sql.gz" "s3://ledgerly-backups/nightly/"
aws s3 cp "s3://ledgerly-backups/nightly/ledgerly-$STAMP.sql.gz" "s3://ledgerly-backups-dr/nightly/" --source-region eu-west-1 --region us-east-1
rm -f "/tmp/ledgerly-$STAMP.sql.gz"
