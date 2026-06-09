import uuid


def test_register_login_and_protected_create(client):
    username = f"jwtuser_{uuid.uuid4().hex[:8]}"
    password = "secret123"

    register_response = client.post('/register', json={'username': username, 'password': password})
    assert register_response.status_code == 201

    login_response = client.post('/login', json={'username': username, 'password': password})
    data = login_response.get_json()
    assert login_response.status_code == 200
    assert 'token' in data

    protected_response = client.post('/create', json={
        'publisher': 'AuthPub',
        'name': 'AuthBook',
        'date': '2025-01-01',
        'cost': 25.5
    })
    assert protected_response.status_code == 401

    authorized_response = client.post('/create', json={
        'publisher': 'AuthPub',
        'name': 'AuthBook',
        'date': '2025-01-01',
        'cost': 25.5
    }, headers={'Authorization': f"Bearer {data['token']}"})
    assert authorized_response.status_code == 201
