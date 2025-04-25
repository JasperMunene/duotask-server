import os, sys

# make sure the project root (where app.py lives) is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import create_app, db as _db

TEST_DATABASE_URI = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test session."""
    # override config for testing
    os.environ["CONNECTION_STRING"] = TEST_DATABASE_URI
    os.environ["FLASK_ENV"] = "testing"

    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URI,
        "WTF_CSRF_ENABLED": False,
    })

    # create tables
    with app.app_context():
        _db.create_all()
        # if you use migrations:
        # upgrade()

    yield app

    # teardown
    with app.app_context():
        _db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def db(app):
    """An initialized database for each test."""
    return _db


