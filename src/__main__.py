#!/usr/bin/env python3
"""
Main entry point for Ultimate Flooder when run as a module
"""

import sys
import os

# Add parent directory to path to import main.py from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main

if __name__ == "__main__":
    main()