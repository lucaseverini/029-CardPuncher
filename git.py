#!/usr/bin/env python3

# 029 Puncher
# git.py (8-24-2025)
# By Luca Severini (lucaseverini@mac.com)

import subprocess

def get_git_tag():
    version = None
    try:
        git_output = subprocess.check_output(["git", "describe", "--tags", "--always"], stderr = subprocess.DEVNULL)
        tag = git_output.strip().decode()
        
    except Exception:
        tag = "[error getting git tag]"
        
    # print(f"Git tag: {tag}")
    return tag

def get_git_count():
    count = None
    try:
        git_output = subprocess.check_output(["git", "rev-list", "--all", "--count"], stderr = subprocess.DEVNULL)
        count = git_output.strip().decode()
        
    except Exception:
        count = "[error getting git count]"
        
    # print(f"Git count: {count}")
    return count

def get_git_date():
    date = None
    try:
        git_output = subprocess.check_output(["git", "log", "-1", "--format=%cd", "--date=format:%d-%b-%Y %H:%M"], stderr = subprocess.DEVNULL)
        date = git_output.strip().decode()

    except subprocess.CalledProcessError:
        date = "[error getting git date]"

    # print(f"Git date: {date}")
    return date
    
def get_git_version():
    count = get_git_count()
    date = get_git_date()
    return f"1.0 (build {count} - {date})"
    
