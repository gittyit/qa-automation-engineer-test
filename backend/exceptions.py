'''  Exceptions classes:

- IndexPageException - Index page exception.
- ResultPageException - Result page exception.
- ConnectionException - Exception during establishing a connection to the DB.
- CreateTablesException - Exception during a deletion of the tables.
- CreateTablesException - Exception during a creation of the tables.
- PopulateTablesException - Exception during a population of the tables.
'''


class ResultPageException(Exception):
    pass


class IndexPageException(Exception):
    pass


class ConnectionException(Exception):
    pass


class DeleteTablesException(IndexPageException):
    pass


class CreateTablesException(IndexPageException):
    pass


class PopulateTablesException(IndexPageException):
    pass


class RetrieveDataException(ResultPageException):
    pass
