"""
Install Git Hooks for Victoria College Repository
Enables automatic pre-commit database snapshotting and seed synchronization.
"""

import os
import sys
import shutil
import stat
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GIT_DIR = os.path.join(BASE_DIR, '.git')
HOOKS_DIR = os.path.join(GIT_DIR, 'hooks')
SRC_HOOK = os.path.join(BASE_DIR, '.githooks', 'pre-commit')
DEST_HOOK = os.path.join(HOOKS_DIR, 'pre-commit')

def install():
    if not os.path.exists(GIT_DIR):
        print("[WARNING] Not a git repository (.git folder not found).")
        return False

    os.makedirs(HOOKS_DIR, exist_ok=True)
    if not os.path.exists(SRC_HOOK):
        print(f"[ERROR] Source hook not found: {SRC_HOOK}")
        return False

    shutil.copyfile(SRC_HOOK, DEST_HOOK)
    
    # Make executable on Unix/Mac/WSL
    try:
        st = os.stat(DEST_HOOK)
        os.chmod(DEST_HOOK, st.st_mode | stat.S_IEXEC)
    except Exception:
        pass

    # Also configure core.hooksPath if desired
    try:
        subprocess.run(['git', 'config', 'core.hooksPath', '.githooks'], cwd=BASE_DIR, check=False)
    except Exception:
        pass

    print("[SUCCESS] Git pre-commit hook installed successfully.")
    print("Database changes in data/victoria.db will now automatically snapshot before commit.")
    return True

if __name__ == '__main__':
    install()
