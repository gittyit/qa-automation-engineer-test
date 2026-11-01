import os
import asyncpg

from asyncpg.connection import Connection

import exceptions as Exc


class dbManager():

    def __init__(self):
        # Get connection parameters from evironment vars
        self.pw = os.environ.get('POSTGRES_PASSWORD') or ""
        self.host = os.environ.get('POSTGRES_HOST') or ""
        self.port = os.environ.get('POSTGRES_PORT') or ""

    async def get_connection(self) -> Connection:
        ''' Gets a new DB connection with parameters from environment vars.

        In case of errors, raises ConnectionException.

        Returns:
        - asyncpg.connection object.

        '''
        try:
            

            # Raise an error if any of the vars are not populated
            if not (self.pw and self.host and self.port):
                raise Exc.ConnectionException(
                    "Provide host, port and password via environment vars:" +
                    f"\nPOSTGRES_PASSWORD={self.pw}\nPOSTGRES_HOST={self.host}\nPOSTGRES_PORT={self.port}")

            # Establish a connection to a DB named "postgres"
            cn = await asyncpg.connect(f'postgresql://postgres:{self.pw}@{self.host}:{self.port}/postgres')
        except Exc.ConnectionException as ex:
            raise ex
        except BaseException as ex:
            raise Exc.ConnectionException("Can't connect to the DB") from ex
        return cn


    async def retrieve_data(self, i: int, d: list):
        """Retrieves data from the DB tables.

        In case of errors, raises RetrieveDataException.

        Args:
            i (int): table number
            d (list): list, where data will be appended
        """
        try:
            cn = await self.get_connection()

            rows = await cn.fetch(f'SELECT * FROM data_{i};')
            for rec in rows:
                d.append({"id": rec['id'],
                        "name": rec['name']})

        # Close the connection
            await cn.close()

        except BaseException as ex:
            raise Exc.RetrieveDataException(
                f"Can't retrieve data from the tables") from ex

    async def get_all_data(self, i: int, d: list):
        """Retrieves data from the DB tables.

        In case of errors, raises RetrieveDataException.

        Args:
            i (int): table number
            d (list): list, where data will be appended
        """
        try:
            cn = await self.get_connection()

            rows = await cn.fetch(f'SELECT * FROM data_{i};')
            for rec in rows:
                d.append({"id": rec['id'],
                        "name": rec['name']})

        # Close the connection
            await cn.close()

        except BaseException as ex:
            raise Exc.RetrieveDataException(
                f"Can't retrieve data from the tables") from ex


    async def delete_tables(self, conn: Connection):
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


    async def create_and_populate_tables(self):
        ''' Create and populate tables method.

        - Creates 3 data tables in DB.
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
            cn = await self.get_connection()

            # Delete data tables
            await self.delete_tables(cn)

            # Create data tables
            await self.create_tables(cn)

            # Populate it with data
            await self.populate_tables(cn)

            # Close the connection
            await cn.close()

        except BaseException as ex:
            raise ex

    async def create_tables(self, conn: Connection):
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


    async def populate_tables(self, conn: Connection):
        """ Populates asynchronously 3 tables from ranges.

        Args:
            conn (Connection): Existing DB connection
        """
        # Populating the table data_1: IDs 1-10, 31-40;
        await self.populate_table(conn, 'data_1', range(1, 11), range(31, 41))

        # Populating the table data_2: IDs 11-20, 41-50;
        await self.populate_table(conn, 'data_2', range(11, 21), range(41, 51))

        # Populating the table data_3: IDs 21-30, 51-60;
        await self.populate_table(conn, 'data_3', range(21, 31), range(51, 61))


    async def populate_table(self, conn: Connection, tab: str, sequence1=None, sequence2=None):
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
