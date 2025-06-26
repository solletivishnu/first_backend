#!/usr/bin/env bash

# Ensure virtualenv is installed
if ! command -v virtualenv &> /dev/null; then
    echo "Installing virtualenv..."
    sudo apt-get update
    sudo apt-get install -y python3-venv
fi

# Remove existing virtual environment if it's broken
if [ -d "/home/ubuntu/env" ]; then
    echo "Removing existing virtual environment..."
    rm -rf /home/ubuntu/env
fi

# Create a new virtual environment
python3 -m venv /home/ubuntu/env

# Activate the virtual environment
source /home/ubuntu/env/bin/activate

# Upgrade pip & setuptools
pip install --upgrade pip setuptools wheel

pip install pandas

# Install dependencies
if [ -f "/home/ubuntu/TaraFirst/requirements.txt" ]; then
    pip install -r /home/ubuntu/TaraFirst/requirements.txt
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

echo "Python dependencies installed successfully!"
