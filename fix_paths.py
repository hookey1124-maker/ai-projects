"""Fix hardcoded Administrator paths -> local machine paths.
Run after every git pull to ensure paths resolve correctly.
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# Path mapping: (old_pattern, new_pattern)
# IMPORTANT: keep old patterns capitalized exactly as they appear in old files
OLD_DESKTOP = r"C:\Users\Administrator\Desktop"
NEW_ROOT = r"c:\Users\Hardy\ai-projects"

PATH_MAP = [
    # AI project root -> ai-projects (the main shift)
    (OLD_DESKTOP + r"\AI项目", NEW_ROOT),
    # Individual projects that were directly on Desktop
    (OLD_DESKTOP + r"\三部周报v1", NEW_ROOT + r"\三部周报v1"),
    (OLD_DESKTOP + r"\新品复盘", NEW_ROOT + r"\新品复盘"),
]

# Files/dirs to skip
SKIP_DIRS = {'.git', '.claude', 'node_modules', '__pycache__', '.venv', 'browser_profile'}
SKIP_EXTENSIONS = {'.xlsx', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.zip', '.exe', '.dll', '.bin'}
SKIP_NAMES = {'.gitignore', '.gitattributes', 'fix_paths.py'}  # protect self


def build_variants(old, new):
    """Generate all slash variants for a path pair."""
    pairs = []
    # Backslash (raw Python string)
    pairs.append((old, new))
    # Forward slash
    pairs.append((old.replace('\\', '/'), new.replace('\\', '/')))
    # Double-backslash (JSON/string-escaped)
    pairs.append((old.replace('\\', '\\\\'), new.replace('\\', '\\\\')))
    return pairs


def fix_file(filepath):
    """Fix paths in a single file. Returns True if modified."""
    try:
        # Skip binary files
        if filepath.suffix.lower() in SKIP_EXTENSIONS:
            return False
        if filepath.name in SKIP_NAMES:
            return False

        content = filepath.read_text(encoding='utf-8', errors='replace')
        original = content

        for old, new in PATH_MAP:
            for old_var, new_var in build_variants(old, new):
                if old_var in content:
                    content = content.replace(old_var, new_var)

        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
        return False

    except Exception as e:
        print(f"  WARN Failed: {filepath.relative_to(REPO_ROOT)} -- {e}")
        return False


def main():
    print("[fix_paths] Scanning for hardcoded Administrator paths...")
    modified = 0
    files_changed = []

    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip excluded dirs (but NOT .workbuddy or other dot-dirs with content)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in files:
            fpath = Path(root) / fname
            if fix_file(fpath):
                modified += 1
                files_changed.append(str(fpath.relative_to(REPO_ROOT)))

    if modified:
        print(f"\n[fix_paths] Fixed {modified} file(s):")
        for f in files_changed:
            print(f"   -> {f}")
    else:
        print("[fix_paths] No Administrator paths found -- all clean.")

    return modified


if __name__ == '__main__':
    sys.exit(0 if main() >= 0 else 1)
