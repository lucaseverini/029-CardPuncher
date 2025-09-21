#!/usr/bin/env python3

# 029 Puncher
# git.py (8-24-2025)
# By Luca Severini (lucaseverini@mac.com)

import os
import re
import argparse
import sys
import subprocess
from typing import Dict, Any, Optional

def _git(*args: str, cwd: Optional[str] = None) -> str:
    return subprocess.check_output(["git", *args], cwd = cwd, stderr = subprocess.STDOUT).decode().strip()

# Check for updates in the given Git repo directory and optionally update it.
# Returns a dict with keys: inside_repo, branch, upstream, ahead, behind, dirty, updated, msg, commits.
# ------------------------------------------------------------------------------
def git_check_update(*, repo_dir: Optional[str] = None, do_update: bool = False) -> Dict[str, Any]:
    try:
        inside = _git("rev-parse", "--is-inside-work-tree", cwd = repo_dir) == "true"
    except subprocess.CalledProcessError as e:
        return {
            "inside_repo": False,
            "updated": False,
            "msg": e.output.decode().strip() if hasattr(e, "output") else str(e)
        }

    if not inside:
        return {"inside_repo": False, "updated": False, "msg": "Not a git repo"}

    def safe_git(args):
        try:
            return _git(*args, cwd = repo_dir)
        except subprocess.CalledProcessError:
            return ""

    branch = safe_git(["rev-parse", "--abbrev-ref", "HEAD"]) or "(detached)"
    upstream = safe_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])

    # fetch
    try:
        _git("fetch", "--all", "--prune", cwd = repo_dir)
    except subprocess.CalledProcessError as e:
        return {
            "inside_repo": True,
            "branch": branch,
            "upstream": upstream or None,
            "updated": False,
            "msg": e.output.decode().strip()
        }

    # ahead/behind versus upstream
    ahead = behind = None
    if upstream:
        try:
            lr = _git("rev-list", "--left-right", "--count", "HEAD...@{u}", cwd = repo_dir)
            left, right = lr.split()
            ahead, behind = int(left), int(right)
        except Exception:
            pass

    # dirty state
    dirty = True
    try:
        subprocess.check_call(
            ["git", "diff-index", "--quiet", "HEAD", "--"],
            cwd = repo_dir,
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL
        )
        dirty = False
    except subprocess.CalledProcessError:
        dirty = True

    commits: List[Dict[str, str]] = []
    if upstream and behind and behind > 0:
        try:
            raw = _git(
                "log",
                "--pretty = format:%H%x1f%an%x1f%ad%x1f%B%x1e",
                "--date = iso-strict",
                "HEAD..@{u}",
                cwd = repo_dir
            )
            for entry in raw.split("\x1e"):
                if not entry.strip():
                    continue
                parts = entry.strip().split("\x1f", 3)
                if len(parts) == 4:
                    message = re.sub(r"\n{2,}", "\n", parts[3]).strip()
                    commits.append(
                        {
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "subject": message
                        }
                    )
        except subprocess.CalledProcessError:
            commits = []

    updated = False
    msg = "OK"
    if do_update and upstream:
        if behind and behind > 0:
            try:
                _git("merge", "--ff-only", "@{u}", cwd = repo_dir)
                updated = True
                msg = "Fast-forwarded"
            except subprocess.CalledProcessError:
                try:
                    _git("pull", "--rebase", "--autostash", cwd = repo_dir)
                    updated = True
                    msg = "Pulled with rebase/autostash"
                except subprocess.CalledProcessError as e:
                    msg = f"Update failed: {e.output.decode().strip()}"
        else:
            msg = "Up to date"

    return {
        "inside_repo": True,
        "branch": branch,
        "upstream": upstream or None,
        "ahead": ahead,
        "behind": behind,
        "dirty": dirty,
        "updated": updated,
        "msg": msg,
        "commits": commits,
    }

def get_git_tag():
    version = None
    try:
        git_output = subprocess.check_output(["git", "describe", "--tags", "--always"], stderr = subprocess.DEVNULL)
        tag = git_output.strip().decode()
        
    except Exception:
        tag = "[error getting git tag]"
        
    return tag

def get_git_count():
    count = None
    try:
        git_output = subprocess.check_output(["git", "rev-list", "--all", "--count"], stderr = subprocess.DEVNULL)
        count = git_output.strip().decode()
        
    except Exception:
        count = "[error getting git count]"
        
    return count

def get_git_date():
    date = None
    try:
        git_output = subprocess.check_output(["git", "log", "-1", "--format=%cd", "--date=format:%d-%b-%Y %H:%M"], stderr = subprocess.DEVNULL)
        date = git_output.strip().decode()

    except subprocess.CalledProcessError:
        date = "[error getting git date]"

    return date
    
def get_git_version():
    count = get_git_count()
    date = get_git_date()
    return f"1.0 (build {count} - {date})"
    
