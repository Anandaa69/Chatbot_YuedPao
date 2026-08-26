"""
Tests for Flask Webhook Endpoints (/callback and /health)
"""
import pytest
from app.main import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'healthy'
    assert 'Chatbot YuedPao' in json_data['service']


def test_mock_webhook_callback(client):
    mock_payload = {
        "events": [
            {
                "type": "message",
                "replyToken": "dummy_reply_token",
                "message": {
                    "type": "text",
                    "id": "12345",
                    "text": "อยากได้เสื้อยืดผ้านุ่มๆ ไม่เกิน 300"
                }
            }
        ]
    }
    response = client.post('/callback', json=mock_payload)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert len(json_data['mock_results']) == 1
    assert json_data['mock_results'][0]['intent'] == 'product_search'
