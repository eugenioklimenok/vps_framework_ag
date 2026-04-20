"""
Project configuration and policy constants.
"""

from pathlib import Path

# Required directory structure for a valid project scaffold
REQUIRED_PROJECT_DIRS = [
    "app",
    "config",
    "deploy",
    "docs",
    "operate",
    "tests",
]

# Required files for a valid project scaffold
REQUIRED_PROJECT_FILES = [
    ".env.example",
    ".gitignore",
    "README.md",
    "compose.yaml",
    "project.yaml",
]
