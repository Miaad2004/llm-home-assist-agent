#!/bin/zsh
# run_app.zsh

VENV_PATH="$(dirname $0)/agent_venv"
VENV_PYTHON="$VENV_PATH/bin/python"

# Check if venv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
    echo "Installing requirements..."
    "$VENV_PYTHON" -m pip install --upgrade pip
    "$VENV_PYTHON" -m pip install -r "$(dirname $0)/requirements.txt"
else
    echo "Virtual environment already exists. Skipping setup."
fi

# Set PYTHONPATH and run the app
export PYTHONPATH="$(dirname $0)"
"$VENV_PYTHON" "$(dirname $0)/scripts/run_app.py"
