#!/usr/bin/env python3
"""
Launch script for DCM (Device Controller-Monitor) GUI
Run this script to start the pacemaker interface application
"""

import sys
import os

# Add DCM directory to path
sys.path.insert(0, os.path.dirname(__file__))

from gui.dcm_gui import main

if __name__ == "__main__":
    print("Starting DCM GUI Application...")
    print("Device Controller-Monitor for Pacemaker Management")
    print("-" * 50)
    main()

