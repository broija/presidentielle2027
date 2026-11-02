#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(realpath -s "${BASH_SOURCE[0]}")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

source .venv/bin/activate

PYTHONPATH=$SCRIPT_DIR

SCRIPT_PATH="$1"
shift

python3 "$SCRIPT_PATH" $*
