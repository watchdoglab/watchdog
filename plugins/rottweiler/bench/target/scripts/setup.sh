#!/usr/bin/env bash
set -e
curl -fsSL https://downloads.acme-tools.example/bin/migrate-linux-amd64 -o /usr/local/bin/migrate
chmod +x /usr/local/bin/migrate
migrate --version
