#!/usr/bin/env python
"""
Development helper script for AI Teaching Assistant Backend.
Usage: python scripts/dev.py <command>
"""
import subprocess
import sys
import os
from pathlib import Path

# Ensure we're in the backend directory
BACKEND_DIR = Path(__file__).parent.parent
os.chdir(BACKEND_DIR)


def run_command(cmd: list, check: bool = True):
    """Run a command and handle errors."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check)
    return result.returncode


def cmd_run():
    """Run the development server."""
    run_command([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"])


def cmd_test():
    """Run tests with pytest."""
    run_command([sys.executable, "-m", "pytest", "-v"])


def cmd_test_cov():
    """Run tests with coverage report."""
    run_command([sys.executable, "-m", "pytest", "--cov=.", "--cov-report=html", "--cov-report=term"])


def cmd_format():
    """Format code with black and isort."""
    run_command([sys.executable, "-m", "black", "."])
    run_command([sys.executable, "-m", "isort", "."])


def cmd_lint():
    """Run linting with ruff."""
    run_command([sys.executable, "-m", "ruff", "check", "."], check=False)


def cmd_typecheck():
    """Run type checking with mypy."""
    run_command([sys.executable, "-m", "mypy", "."], check=False)


def cmd_check():
    """Run all checks (lint, typecheck, test)."""
    print("=== Running Linting ===")
    cmd_lint()
    print("\n=== Running Type Check ===")
    cmd_typecheck()
    print("\n=== Running Tests ===")
    cmd_test()


def cmd_install():
    """Install dependencies."""
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def cmd_install_dev():
    """Install development dependencies."""
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    run_command([sys.executable, "-m", "pip", "install", "black", "isort", "mypy", "ruff", "pytest-cov"])


def cmd_clean():
    """Clean up cache and build files."""
    import shutil
    patterns = ["__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "htmlcov", ".coverage"]
    for pattern in patterns:
        for path in BACKEND_DIR.rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed: {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed: {path}")


def cmd_help():
    """Show available commands."""
    print("AI Teaching Assistant Backend - Development Commands\n")
    print("Available commands:")
    print("  run         - Run the development server")
    print("  test        - Run tests")
    print("  test-cov    - Run tests with coverage")
    print("  format      - Format code (black + isort)")
    print("  lint        - Run linting (ruff)")
    print("  typecheck   - Run type checking (mypy)")
    print("  check       - Run all checks")
    print("  install     - Install dependencies")
    print("  install-dev - Install dev dependencies")
    print("  clean       - Clean cache files")
    print("  help        - Show this help")


COMMANDS = {
    "run": cmd_run,
    "test": cmd_test,
    "test-cov": cmd_test_cov,
    "format": cmd_format,
    "lint": cmd_lint,
    "typecheck": cmd_typecheck,
    "check": cmd_check,
    "install": cmd_install,
    "install-dev": cmd_install_dev,
    "clean": cmd_clean,
    "help": cmd_help,
}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        cmd_help()
        sys.exit(0)
    
    command = sys.argv[1]
    if command in COMMANDS:
        COMMANDS[command]()
    else:
        print(f"Unknown command: {command}")
        cmd_help()
        sys.exit(1)

