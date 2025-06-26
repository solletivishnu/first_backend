#!/usr/bin/env bash

# Function to handle dpkg interruption
fix_dpkg() {
  echo "Running 'sudo dpkg --configure -a' to fix any interrupted dpkg processes"
  sudo dpkg --configure -a
}

# Run the fix_dpkg function before proceeding
fix_dpkg

# Update the package list
echo "Updating package list..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required system dependencies
echo "Installing required packages..."
sudo apt-get install -y wkhtmltopdf python3-pip nginx virtualenv python3-venv python3-setuptools python3-wheel

# Ensure pip and setuptools are updated **only in virtual environment**
echo "Upgrading pip and setuptools in virtual environment..."

# Create a virtual environment if not already created
if [ ! -d "myenv" ]; then
  sudo python3 -m venv myenv
fi

# Activate virtual environment
source myenv/bin/activate

sudo chmod -R 777 myenv

# Upgrade pip and setuptools inside the virtual environment
pip install --upgrade pip setuptools wheel pandas

echo "All dependencies installed successfully."
