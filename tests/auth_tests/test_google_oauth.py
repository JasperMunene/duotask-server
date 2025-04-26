import pytest
from flask import Flask, redirect
import resources.auth_resource as auth_res

class Dummy:
    pass

def make_oauth_stub(frontend_url='http://frontend'):
    stub = Dummy()
    stub.frontend_url = frontend_url
    stub.google = Dummy()
    # default metadata and methods; tests will override
    stub.google.server_metadata = {}
    return stub

@pytest.fixture
def app_context():
    # Provide a Flask request context for url_for and redirect
    app = Flask(__name__)
    with app.test_request_context():
        yield

# Tests for GoogleLogin.get()

def test_google_login_success(app_context, monkeypatch):
    oauth_stub = make_oauth_stub()
    # patch url_for to avoid BuildError
    monkeypatch.setattr(auth_res, 'url_for', lambda endpoint, _external=True: 'http://fake/authorize')
    # stub authorize_redirect to return a Flask redirect response
    oauth_stub.google.authorize_redirect = lambda redirect_uri: redirect(redirect_uri)

    gl = auth_res.GoogleLogin(oauth_stub)
    resp = gl.get()

    # Should be a redirect to our fake URL
    assert resp.status_code == 302
    assert resp.location == 'http://fake/authorize'


def test_google_login_failure(app_context, monkeypatch, caplog):
    oauth_stub = make_oauth_stub()
    monkeypatch.setattr(auth_res, 'url_for', lambda endpoint, _external=True: 'http://fake/authorize')
    # simulate authorize_redirect throwing
    def bad_auth(redirect_uri):
        raise Exception('fail')
    oauth_stub.google.authorize_redirect = bad_auth

    gl = auth_res.GoogleLogin(oauth_stub)
    resp, code = gl.get()

    assert code == 503
    assert resp['message'] == 'Google login unavailable'
    assert 'Google login initiation failed' in caplog.text

# Tests for GoogleAuthorize.get()

def test_authorize_access_token_failure(app_context, monkeypatch):
    oauth_stub = make_oauth_stub(frontend_url='http://front')
    # simulate authorize_access_token exception
    oauth_stub.google.authorize_access_token = lambda: (_ for _ in ()).throw(Exception('token error'))

    ga = auth_res.GoogleAuthorize(oauth_stub)
    resp = ga.get()

    assert isinstance(resp, type(redirect('')))
    assert 'error=Failed to authorize access token' in resp.location


def test_authorize_missing_userinfo_endpoint(app_context, monkeypatch):
    oauth_stub = make_oauth_stub()
    oauth_stub.google.authorize_access_token = lambda: 'tok'
    oauth_stub.google.server_metadata = {}  # missing endpoint

    ga = auth_res.GoogleAuthorize(oauth_stub)
    resp = ga.get()

    assert 'error=Server configuration error' in resp.location


def test_authorize_fetch_userinfo_failure(app_context):
    oauth_stub = make_oauth_stub()
    oauth_stub.google.authorize_access_token = lambda: 'tok'
    oauth_stub.google.server_metadata = {'userinfo_endpoint': 'https://fake'}
    # simulate HTTP get failure
    class FakeRes:
        def raise_for_status(self): raise Exception('fetch error')
    oauth_stub.google.get = lambda url: FakeRes()

    ga = auth_res.GoogleAuthorize(oauth_stub)
    resp = ga.get()

    assert 'error=Failed to fetch user information' in resp.location


def test_authorize_missing_email_field(app_context):
    oauth_stub = make_oauth_stub()
    oauth_stub.google.authorize_access_token = lambda: 'tok'
    oauth_stub.google.server_metadata = {'userinfo_endpoint': 'https://fake'}
    # valid status, but missing email
    class GoodRes:
        def raise_for_status(self): pass
        def json(self): return {}
    oauth_stub.google.get = lambda url: GoodRes()

    ga = auth_res.GoogleAuthorize(oauth_stub)
    resp = ga.get()

    assert 'error=Email not provided by Google' in resp.location


def test_authorize_success(app_context, monkeypatch):
    # simulate create user and JWT
    fake_user = Dummy()
    fake_user.id = 42

    oauth_stub = make_oauth_stub(frontend_url='http://front')
    oauth_stub.google.authorize_access_token = lambda: 'tok'
    oauth_stub.google.server_metadata = {'userinfo_endpoint': 'https://fake'}
    class GoodRes2:
        def raise_for_status(self): pass
        def json(self): return {'email': 'u@x.com', 'name': 'U', 'picture': 'pic'}
    oauth_stub.google.get = lambda url: GoodRes2()

    # patch user creation and token
    monkeypatch.setattr(auth_res.GoogleAuthorize, '_get_or_create_user', lambda self, info: fake_user)
    monkeypatch.setattr(auth_res, 'create_access_token', lambda identity: 'jwt')

    ga = auth_res.GoogleAuthorize(oauth_stub)
    resp = ga.get()

    # Should redirect to onboarding
    assert isinstance(resp, type(redirect('')))
    assert resp.location == 'http://front/onboarding'
    # Cookie should carry our fake JWT
    cookie = resp.headers.get('Set-Cookie', '')
    assert 'access_token=jwt' in cookie
