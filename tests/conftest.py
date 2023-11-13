from flask import Flask
import pytest
import os

from backend import create_app

# pytest_plugins = "pytest-asyncio"


@pytest.fixture
def app():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    app = create_app({
        'TESTING': True,
    })

    yield app


@pytest.fixture()
def client(app: Flask):
    return app.test_client()


@pytest.fixture()
def runner(app: Flask):
    return app.test_cli_runner()
