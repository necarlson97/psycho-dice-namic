#!/bin/bash

# Psycho-Dice-Namic Development Script
# Watches for changes and re-runs simulations

# Activate virtual environment
source env/bin/activate

# Install dependencies if needed
if [ ! -f env/.deps_installed ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch env/.deps_installed
fi

# Function to run simulations
run_simulations() {
    echo "Running simulations..."
    python src/run_simulations.py
}

# Run initial simulations
run_simulations

# Watch for changes and re-run
echo "Watching for changes..."
watchmedo shell-command \
    --patterns="*.py" \
    --recursive \
    --command='python src/run_simulations.py' \
    src/

