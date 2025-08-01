#!/usr/bin/env python3
"""
Simple runner script that sets up the correct Python path
"""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now import and run the main module
from main import main

if __name__ == "__main__":
    main()