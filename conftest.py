"""
conftest.py — project root

Ensures the project root is on sys.path so tests can import app.* directly.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))