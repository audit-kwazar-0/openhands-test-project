#!/usr/bin/env bash
# Run inside OpenHands sandbox: /workspace/project/openhands-test-project
set -euo pipefail

cd "$(dirname "$0")/.."
echo "Python: $(python3 --version)"

rm -rf .venv
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
# Use prebuilt wheels only — avoids libyaml compile segfaults
.venv/bin/pip install --only-binary=:all: -r requirements.txt || \
  .venv/bin/pip install -r requirements.txt

chmod +x labctl
./labctl init
echo "Verify imports:"
.venv/bin/python -c "import yaml; import lab_sentinel; print('yaml', yaml.__version__, 'lab_sentinel', lab_sentinel.__version__)"
.venv/bin/pytest -q
echo "OK: .venv ready — always use .venv/bin/python and .venv/bin/pytest"
