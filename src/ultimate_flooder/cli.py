#!/usr/bin/env python3
"""
Command line interface for IP-HUNTER
"""

import sys
import os

def main():
    """Main CLI entry point"""
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)

    # Import and run main
    from main import main as app_main
    app_main()

if __name__ == "__main__":
    main()