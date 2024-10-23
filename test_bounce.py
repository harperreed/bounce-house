import pytest
from bounce import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_valid_domain_redirection(client):
    response = client.get('/', headers={'Host': 'x.com'})
    assert response.status_code == 301
    assert response.headers['Location'] == 'http://harperrules.com/domain/?domain=x.com'


def test_invalid_domain_redirection(client):
    response = client.get('/', headers={'Host': 'invalid_domain'})
    assert response.status_code == 301
    assert response.headers['Location'] == 'http://harperrules.com/'
