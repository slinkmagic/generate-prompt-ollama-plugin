#!/usr/bin/env python3
"""Pre-commit hooks setup script"""

import subprocess
import sys

def install_pre_commit():
    """Install and setup pre-commit hooks"""
    try:
        # Install pre-commit
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pre-commit'], check=True)
        
        # Install the git hook scripts
        subprocess.run(['pre-commit', 'install'], check=True)
        
        # Run hooks on all files (optional)
        print("Installing pre-commit hooks...")
        subprocess.run(['pre-commit', 'run', '--all-files'], check=False)
        
        print("✅ Pre-commit hooks installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing pre-commit hooks: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_pre_commit()