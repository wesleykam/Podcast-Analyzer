#!/usr/bin/env bash
set -e

# Point Selenium at your cached Chrome
export CHROME_BIN=/opt/render/project/.render/chrome/opt/google/chrome/google-chrome
export PATH="$PATH:/opt/render/project/.render/chrome/opt/google/chrome"

# (Optional) cache chromedriver downloads across restarts
# export WDM_LOCAL=1

# Helpful for debugging in logs (optional)
"$CHROME_BIN" --version || true

# Start the app
exec gunicorn 'app:create_app()' --bind 0.0.0.0:$PORT