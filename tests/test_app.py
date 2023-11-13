""" Test for app
"""
import os
import pytest

from backend import app


def test_me():
    ''' Selfcheck for the testing environment
    - Always True
    '''
    assert True


@pytest.mark.asyncio
async def test_db_connection():
    ''' Establishes a new async DB connection:
    - Populates evironment variables with connection parameters
    - Launches get_connection method (async)
    - Checks that there is no error messages or exceptions
    - Checks that the connection object is from asyncpg.connection.Connection class
    '''
    # Set connection parameters
    os.environ['POSTGRES_HOST'] = "localhost"
    os.environ['POSTGRES_PORT'] = "5440"
    os.environ['POSTGRES_PASSWORD'] = "Examplepass14"

    try:
        cn = await app.get_connection()
    except BaseException as ex:
        pytest.fail(str(ex))

    assert isinstance(cn, app.asyncpg.connection.Connection)


# def test_run_request(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b"<p>Tables are created and populated!</p>" in response.data
