#!/usr/bin/env bash
set -e

# Resolve the directory where this bash script is actually located
SCRIPT_NAME=$(readlink $(which $0))
SCRIPT_DIR="$(cd $(dirname $SCRIPT_NAME) && pwd)"

# Activate the virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Pass all CLI arguments ($@) directly to the Python script
python "$SCRIPT_DIR/repent.py" "$@" -t "$SCRIPT_DIR/main.tex"

# Deactivate venv
deactivate
