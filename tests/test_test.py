import pytest

from models.user import User
from extensions import bcrypt

# We need to patch out the external email sender
import resources.auth_resource as auth_res


def test_signup_success(client, db, monkeypatch):
    """
    Should create a new user, hash the password, send an OTP email,
    and return 201 with a user_id.
    """
    sent = {}

    # Replace the real email send with a dummy
    def fake_send(params):
        sent['called'] = True
        sent['params'] = params

    monkeypatch.setattr(auth_res.resend.Emails, 'send', fake_send)

    payload = {
        'name': 'Alice',
        'email': 'alice@example.com',
        'password': 'secret'
    }
    response = client.post('/auth/signup', json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'User created. Please verify your email.'
    assert 'user_id' in data

    # Verify the user was saved in DB
    user = User.query.filter_by(email=payload['email']).first()
    assert user is not None
    # Password must be hashed
    assert user.password != payload['password']
    assert bcrypt.check_password_hash(user.password, payload['password'])

    # OTP email should have been "sent"
    assert sent.get('called', False) is True
    assert sent['params']['to'] == [payload['email']]


def test_signup_conflict_existing_email(client, db):
    """
    If the email is already registered, should return 409 conflict.
    """
    # Pre-create a user with the same email
    hashed_pw = bcrypt.generate_password_hash('abc').decode('utf-8')
    existing = User(name='Bob', email='bob@example.com', password=hashed_pw)
    db.session.add(existing)
    db.session.commit()

    payload = {
        'name': 'Bob2',
        'email': 'bob@example.com',
        'password': 'newpass'
    }
    response = client.post('/auth/signup', json=payload)

    assert response.status_code == 409
    data = response.get_json()
    assert data['message'] == 'User with that email already exists'