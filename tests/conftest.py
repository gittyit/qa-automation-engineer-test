import pytest
# from app import create_app
from backend import create_app

# backend.create_app

@pytest.fixture()
def test_run():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    
    yield app
    
@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()