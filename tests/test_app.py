import pytest
import backend.app as app

def test_me():
    # app.run()
    assert True

def test_run_request(client):
    response = client.get("/")
    # breakpoint()
    assert b"<p>Tables are created and populated!</p>" in response.data