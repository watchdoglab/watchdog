#!/usr/bin/env bash
set -e
git rm --cached .env
git commit -m "remove env file"
NEW_KEY="FAKE-NEW-KEY-$(date +%s)"
echo "$NEW_KEY" > /tmp/new_stripe_key.txt
chmod 644 /tmp/new_stripe_key.txt
echo "New key: $NEW_KEY"
