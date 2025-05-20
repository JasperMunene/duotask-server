import pytest

from models.user import User
from extensions import bcrypt
import resources.auth_resource as auth_res


def create_user(app, db, email, password, verified):
    """Helper to create a new user and return its id and email within app context."""
    with app.app_context():
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            name="Test User",
            email=email,
            password=hashed,
            auth_provider='email',
            is_verified=verified
        )
        db.session.add(user)
        db.session.commit()
        return user.id, user.email


def test_login_no_user(client):
    """If email not found, should return 401 and appropriate message."""
    resp = client.post(
        '/auth/login',
        json={'email': 'nouser@example.com', 'password': 'x'}
    )
    assert resp.status_code == 401
    assert resp.get_json()['message'] == 'No user with that email credentials'


def test_login_incorrect_password(app, client, db):
    """If password is wrong, should return 401 and error message."""
    # Create a verified user
    create_user(app, db, 'bob@example.com', 'correctpass', verified=True)
    resp = client.post(
        '/auth/login',
        json={'email': 'bob@example.com', 'password': 'wrongpass'}
    )
    assert resp.status_code == 401
    assert resp.get_json()['message'] == 'Incorrect password'


def test_login_not_verified(app, client, db, monkeypatch):
    """If account not verified, should return 403 and error message."""
    # Force password check to always pass
    monkeypatch.setattr(auth_res.bcrypt, 'check_password_hash', lambda stored, pwd: True)
    user_id, email = create_user(app, db, 'alice@example.com', 'pass123', verified=False)
    resp = client.post(
        '/auth/login',
        json={'email': email, 'password': 'pass123'}
    )
    assert resp.status_code == 403
    assert resp.get_json()['message'] == 'Account not verified'


def test_login_success(app, client, db, monkeypatch):
    """Happy path: verified user with correct credentials gets a token cookie and 200."""
    # Stub out both password check and JWT creation
    monkeypatch.setattr(auth_res.bcrypt, 'check_password_hash', lambda stored, pwd: True)
    monkeypatch.setattr(auth_res, 'create_access_token', lambda identity: 'fake-token')

    user_id, email = create_user(app, db, 'jane@example.com', 'pw123', verified=True)
    resp = client.post(
        '/auth/login',
        json={'email': email, 'password': 'pw123'}
    )
    assert resp.status_code == 200

    data = resp.get_json()
    assert data['message'] == 'Login successful'
    assert data['user']['email'] == email
    assert data['user']['id'] == user_id

    # Verify the cookie header contains our fake token
    cookie = resp.headers.get('Set-Cookie', '')
    assert 'access_token=fake-token' in cookie
