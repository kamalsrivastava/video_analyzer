import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def test_upload(client):
    # Test for uploading a file (you need a valid file for this)
    data = {
        'file': (open('test_video.mp4', 'rb'), 'test_video.mp4')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert 'transcribed_text' in response.json

def test_analyze(client):
    # Test the analyze endpoint
    response = client.post('/analyze', json={"text": "Hello world!"})
    assert response.status_code == 200
    assert 'summary' in response.json
    assert 'sentiment' in response.json
