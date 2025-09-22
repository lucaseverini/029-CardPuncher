#!/usr/bin/env python3

# 029 Puncher
# git.py (9-21-2025)
# By Luca Severini (lucaseverini@mac.com)

import os
import sys
import subprocess

def upload_to_arduino():
    print("Uploading to Arduino…")

if __name__ == "__main__":
    try:
        upload_to_arduino()
           
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\nProgram Interrupted.")
        sys.exit(1)
