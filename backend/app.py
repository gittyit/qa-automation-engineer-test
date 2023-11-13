'''  QA Automation Engineer Test:
- Index page --> Creates DB tables and populates it (async)
- Result page --> Retrieves the data from DB tables in JSON (async)
'''
import os
import asyncio
import asyncpg

from . import exceptions as Exc

from asyncpg.connection import Connection
from flask import Flask
from flask import render_template as Render
from flask import jsonify

app = Flask(__name__)


@app.route('/result')
async def result_page():
    ''' Result page method.

    - Queries all data from the tables concurrently and sort it by ID.
    - If no data is found, returns an error page with error details
    - In case of success, returns data in JSON format
    '''
    try:
        data = []
        # Create coroutines list with data queries from 3 tables
        coros = [retrieve_data(i, data) for i in range(1, 4)]
        # Run coroutines concurrently and get data within timeout of 2 seconds
        for co in asyncio.as_completed(coros, timeout=2):
            await co
        # Sort data by id
        d = sorted(data, key=lambda x: x['id'])
        # print(d)
    except BaseException as ex:
        return Render("error.html", error_msg=str(ex))
    return jsonify(d)


@app.route('/')
async def index_page():
    ''' Index page method.

    - Asyncronicaly creates 3 data tables in DB.
    - Populates the tables with a following data:
        - Table data_1: IDs 1-10, 31-40;
        - Table data_2: IDs 11-20, 41-50;
        - Table data_3: IDs 21-30, 51-60;
    - In case of:
        - errors, returns an error page with details
        - success, returns success message
    '''
    try:
        # Open a new connection to the DB
        cn = await get_connection()

        # Delete data tables
        await delete_tables(cn)

        # Create data tables
        await create_tables(cn)

        # Populate it with data
        await populate_tables(cn)
    except BaseException as ex:
        return Render("error.html", error_msg=str(ex))

    # Close the connection
    await cn.close()

    message = 'Tables are created and populated!'
    return f"<p>{message}</p>"


async def get_connection() -> (str, str, Connection):
    ''' Gets a new DB connection with parameters from environment vars.

    In case of errors, raises ConnectionException.

    Returns:
    - asyncpg.connection object.

    '''
    try:
        # Get connection parameters from evironment vars
        pw = os.environ.get('POSTGRES_PASSWORD')
        host = os.environ.get('POSTGRES_HOST')
        port = os.environ.get('POSTGRES_PORT')

        # Raise an error if any of the vars are not populated
        if not (pw and host and port):
            raise Exception("Provide environment vars to connect to the DB")

        # Establish a connection to a DB named "postgres"
        cn = await asyncpg.connect(f'postgresql://postgres:{pw}@{host}:{port}/postgres')
    except BaseException as ex:
        raise Exc.ConnectionException("Can't connect to the DB") from ex
    return cn


async def retrieve_data(i: int, d: list):
    """Retrieves data from the DB tables.

    In case of errors, raises RetrieveDataException.

    Args:
        i (int): table number
        d (list): list, where data will be appended
    """
    try:
        cn = await get_connection()

        rows = await cn.fetch(f'SELECT * FROM data_{i};')
        for rec in rows:
            d.append({"id": rec['id'],
                      "name": rec['name']})

    # Close the connection
        await cn.close()

    except BaseException as ex:
        raise Exc.RetrieveDataException(
            f"Can't retrieve data from the tables") from ex


async def delete_tables(conn: Connection):
    """ Deletes existing data tables from the DB.

    Args:
        conn (Connection): Existing DB connection
    """
    try:
        # If tables exist --> delete it
        await conn.execute('''
            DROP TABLE IF EXISTS data_1, data_2, data_3;
        ''')
    except BaseException as ex:
        raise Exc.DeleteTablesException(
            f"Can't delete tables in the DB") from ex


async def create_tables(conn: Connection):
    """ Populates asynchronously 3 tables from ranges.

    Args:
        conn (Connection): Existing DB connection
    """
    try:
        # Create 3 DB tables
        await conn.execute('''
                CREATE TABLE data_1 (
                    id INT PRIMARY KEY,
                    name VARCHAR(255)
                );
                CREATE TABLE data_2 (
                    id INT PRIMARY KEY,
                    name VARCHAR(255)
                );
                CREATE TABLE data_3 (
                    id INT PRIMARY KEY,
                    name VARCHAR(255)
                );
        ''')
    except BaseException as ex:
        raise Exc.CreateTablesException(
            f"Can't create tables in the DB") from ex


async def populate_tables(conn: Connection):
    """ Populates asynchronously 3 tables from ranges.

    Args:
        conn (Connection): Existing DB connection
    """
    # Populating the table data_1: IDs 1-10, 31-40;
    await populate_table(conn, 'data_1', range(1, 11), range(31, 41))

    # Populating the table data_2: IDs 11-20, 41-50;
    await populate_table(conn, 'data_2', range(11, 21), range(41, 51))

    # Populating the table data_3: IDs 21-30, 51-60;
    await populate_table(conn, 'data_3', range(21, 31), range(51, 61))


async def populate_table(conn: Connection, tab: str, sequence1=None, sequence2=None):
    """ Populate asynchronously DB table from arguments.

    Args:
        conn (Connection): Existing DB connection
        tab (str): Table name to populate
        sequence1 (sequence, optional): Range. Defaults to None.
        sequence2 (sequence, optional): Range. Defaults to None.

    Returns:
        Render: Rendered template with error page
    """
    try:
        # If sequence1 is defined --> Populate the table with it
        if sequence1:
            for id in sequence1:
                await conn.execute(f"INSERT INTO {tab} (id, name) VALUES({id}, 'Test {id}');")

        # If sequence2 is defined --> Populate the table with it
        if sequence2:
            for id in sequence2:
                await conn.execute(f"INSERT INTO {tab} (id, name) VALUES({id}, 'Test {id}');")
    except BaseException as ex:
        raise Exc.PopulateTablesException(
            f"Can't insert data into table {tab}") from ex
