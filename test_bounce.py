import pytest
from bounce import app, domain_counter_stat, rate_limit_store
import time


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_valid_domain_redirection(client):
    response = client.get('/', headers={'Host': 'example.com'})
    assert response.status_code == 301
    assert response.headers['Location'] == (
        'http://harperrules.com/domain/?domain=example.com'
    )


def test_invalid_domain_redirection(client):
    response = client.get('/', headers={'Host': 'invalid_domain'})
    assert response.status_code == 301
    assert response.headers['Location'] == 'http://harperrules.com/'


def test_missing_host_header(client):
    response = client.get('/')
    assert response.status_code == 301
    assert response.headers['Location'] == 'http://harperrules.com/'


def test_prometheus_counter_increment(client):
    initial_count = domain_counter_stat.labels('example.com')._value.get()
    client.get('/', headers={'Host': 'example.com'})
    new_count = domain_counter_stat.labels('example.com')._value.get()
    assert new_count == initial_count + 1


def test_rate_limiting(client):
    client_ip = '127.0.0.1'
    rate_limit_store[client_ip] = [time.time()] * 100  # Simulate 100 requests in the rate limit period
    response = client.get('/', headers={'Host': 'example.com'}, environ_base={'REMOTE_ADDR': client_ip})
    assert response.status_code == 429
    assert b"Rate limit exceeded" in response.data
