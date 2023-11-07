import pytest
# from backend import create_app

def test_run_request(client):
    response = client.get("/")
    assert b"<p>Tables are created and populated!</p>" in response.data