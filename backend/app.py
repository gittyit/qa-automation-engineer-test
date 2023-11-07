import asyncpg
import asyncio
import os
# import logging as Log

from flask import Flask as Fl, url_for
from flask import render_template as Render
from flask import jsonify

app = Fl(__name__)


@app.route('/result')
async def result():
    ''' Result page method:
    - Queries all data from tables and sort it by ID.
    - Creates a JSON response with retrieved data.
    - If no data is found returns an error page with error details
    - In case of success returns data in JSON format
    '''
    # Get a new connection to the DB
    msg, Ex, cn = await get_connection()
    # In case of errors --> Display error page
    if not cn:
        return Render("error.html", error_msg=msg, ex_msg=Ex)

    try:
        # Retrieve all data from 3 tables with timeout 2 seconds
        d = await asyncio.wait_for(retrieve_data(cn), timeout=2)
    except BaseException as Ex:
        msg, ex_str = add_msg("Can't retrieve data from DB tables", Ex)
        return Render("error.html", error_msg=msg, ex_msg=ex_str)
    return jsonify(d)


@app.route('/')
async def run():
    ''' Index page method:
    - Asyncronicaly creates 3 data tables in DB.
    - Populates the tables with data:
        - Table data_1: IDs 1-10, 31-40;
        - Table data_2: IDs 11-20, 41-50;
        - Table data_3: IDs 21-30, 51-60; 
    - In case of error returns an error page with error details
    - In case of success returns success message
    '''
    # Log.basicConfig(level=Log.ERROR)
    # Log.info('Run method started')
    # url = url_for('run')
    # Get a new connection to the DB
    msg, ex_str, cn = await get_connection()
    # In case of errors --> Display error page
    if not cn:
        return Render("error.html", error_msg=msg, ex_msg=ex_str)

    try:
        # If tables exist --> delete it
        await cn.execute('''
            DROP TABLE IF EXISTS data_1, data_2, data_3;
        ''')
    except BaseException as Ex:
        msg, ex_str = add_msg("Can't delete DB tables", Ex)
        return Render("error.html", error_msg=msg, ex_msg=ex_str)

    try:
        # Create data tables
        await cn.execute('''
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
    except BaseException as Ex:
        msg, ex_str = add_msg("Can't create DB tables", Ex)
        return Render("error.html", error_msg=msg, ex_msg=ex_str)

    await populate_tables(cn)

    # Close the connection
    await cn.close()

    message = 'Tables are created and populated!'
    return f"<p>{message}</p>"


async def get_connection():
    try:
        # Establish a connection to a DB named "postgres"
        pw = os.environ.get('POSTGRES_PASSWORD')
        host = os.environ.get('POSTGRES_HOST')
        port = os.environ.get('POSTGRES_PORT')
        if not (pw and host and port):
            raise Exception("Provide environment vars to connect to the DB")
        cn = await asyncpg.connect(f'postgresql://postgres:{pw}@{host}:{port}/postgres')
    except BaseException as Ex:
        msg, ex_str = add_msg("Can't connect to the DB", Ex)
        return msg, ex_str, ''
    return '', '', cn


async def retrieve_data(connection):
    d = []
    async with connection.transaction():
        async for rec in connection.cursor('''
            SELECT * FROM data_1
            UNION ALL
            SELECT * FROM data_2
            UNION ALL
            SELECT * FROM data_3
            ORDER BY id;
        '''):
            d.append({"id": rec['id'],
                      "name": rec['name']})
    return d


def add_msg(text, exception=''):
    msg = f"{text}: {exception}"
    print(msg)
    return text, str(exception)


async def populate_tables(connection):
    # Populating the table data_1: IDs 1-10, 31-40;
    await populate_table(connection, 'data_1', range(1, 11), range(31, 41))

    # Populating the table data_2: IDs 11-20, 41-50;
    await populate_table(connection, 'data_2', range(11, 21), range(41, 51))

    # Populating the table data_3: IDs 21-30, 51-60;
    await populate_table(connection, 'data_3', range(21, 31), range(51, 61))


async def populate_table(connection, tablename, sequence1: None, sequence2: None):
    try:
        # If sequence1 is defined --> Populate the table with it
        if sequence1:
            for id in sequence1:
                await connection.execute(f"INSERT INTO {tablename} (id, name) VALUES({id}, 'Test {id}');")

        # If sequence2 is defined --> Populate the table with it
        if sequence2:
            for id in sequence2:
                await connection.execute(f"INSERT INTO {tablename} (id, name) VALUES({id}, 'Test {id}');")
    except BaseException as Ex:
        msg, ex_str = add_msg(f"Can't insert data into table {tablename}", Ex)
        return Render("error.html", error_msg=msg, ex_msg=ex_str)
