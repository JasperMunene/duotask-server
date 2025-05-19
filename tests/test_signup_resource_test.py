from models.user import User
import datetime
def test_missing_fields(client):
    response = client.post('/auth/signup', json={})
    assert response.status_code == 400
    assert b"Name cannot be blank!" in response.data

def test_invalid_email(client, mock_validate_email):
    mock_validate_email.return_value = False
    response = client.post('/auth/signup', json={
        'name': 'John',
        'email': 'invalid-email',
        'password': 'Password123!'
    })
    assert response.status_code == 400

def test_password_rules(client):
    # Add password rules in your app, this assumes validation exists
    response = client.post('/auth/signup', json={
        'name': 'John',
        'email': 'john@example.com',
        'password': '123'  # too weak
    })
    assert response.status_code == 400
    
def test_successful_signup(client ,mock_send, mock_otp ):
    response = client.post('/auth/signup', json={
        'name': 'Jane',
        'email': 'jane@example.com',
        'password': 'StrongPass123!'
    })

    data = response.get_json()
    user = User.query.filter_by(email='jane@example.com').first()

    assert response.status_code == 201
    assert 'user_id' in data
    assert user is not None
    assert user.password != 'StrongPass123!'  # Ensure hashing
    assert user.otp_code == '123456'
    assert user.otp_expires_at > datetime.datetime.utcnow()
    assert user.is_verified is False
    mock_send.assert_called_once()

def test_duplicate_email(client):
    user = User(
        name="Test",
        email="test@example.com",
        password="hashedpass"
    )
    _db.session.add(user)
    _db.session.commit()

    response = client.post('/auth/signup', json={
        'name': 'New User',
        'email': 'test@example.com',
        'password': 'Password123!'
    })
    assert response.status_code == 409
    assert b"User with that email already exists" in response.data

def test_email_failure_handled(client, mock_send ):
    response = client.post('/auth/signup', json={
        'name': 'Fail Email',
        'email': 'fail@example.com',
        'password': 'Password123!'
    })

    assert response.status_code == 500
    assert b"Registration failed" in response.data
    
def test_db_error_handled(client, mock_logger):
    response = client.post('/auth/signup', json={
        'name': 'DB Fail',
        'email': 'dberror@example.com',
        'password': 'Password123!'
    })

    assert response.status_code == 500
    assert b"Registration failed" in response.data
    mock_logger.assert_called_once()
