import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_root_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'status' in data
    assert data['status'] == 'running'

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_get_items(client):
    response = client.get('/api/items')
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'count' in data
    assert data['count'] == 3

def test_get_item_exists(client):
    response = client.get('/api/items/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == 1
    assert 'name' in data

def test_get_item_not_found(client):
    response = client.get('/api/items/999')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_create_item(client):
    response = client.post('/api/items',
        json={'name': 'Test Item', 'description': 'Test description'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Test Item'
    assert 'created_at' in data

def test_create_item_missing_name(client):
    response = client.post('/api/items', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
