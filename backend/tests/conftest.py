"""Pytest configuration and shared fixtures."""
import os

# Use SQLite for tests — no real PostgreSQL needed
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("GOOGLE_API_KEY", "test-key-not-used-in-unit-tests")
