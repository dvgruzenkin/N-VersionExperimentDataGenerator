"""Data base query execution module

Program for simulation several N-versions work of one module to test vote algorithms.
Experiment is carried out in Denis V. Gruzenkin PhD thesis writing.
"""

import sqlite3

__author__ = "Denis V. Gruzenkin"
__copyright__ = "Copyright 2021, Denis V. Gruzenkin"
__credits__ = ["Denis V. Gruzenkin"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Denis V. Gruzenkin"
__email__ = "gruzenkin.denis@good-look.su"
__status__ = "Production"


class DBConnectorMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DBConnector(metaclass=DBConnectorMeta):
    def __init__(self, db_name: str):
        self._db_name = db_name
        self._connection = sqlite3.connect(self._db_name)

    @property
    def db_name(self) -> str:
        return self._db_name

    @db_name.setter
    def db_name(self, new_name: str):
        self._db_name = new_name

    def connect_2_db(self):
        self._connection = sqlite3.connect(self._db_name)

    def execute_query(self, query_str, parameters=[], commit=False, return_query_set=True):
        """
        It executes query string with or without parameters and commit and return query set if it is necessary
        :param query_str: SQL-query string for execution
        :param parameters: list or tuples query parameters, by default is empty
        :param commit: Is needed commit query flag, by default is False
        :param return_query_set: Is needed return query set flag, by default is True
        :return: SQL query set or None
        """
        cursor = self._connection.cursor()
        many_parameters = len(parameters) > 0 and isinstance(parameters[0], (tuple, list))

        try:
            if many_parameters:
                cursor.executemany(query_str, parameters)
            else:
                cursor.execute(query_str, parameters)

            if commit:
                self._connection.commit()

            if return_query_set:
                if 'insert' in query_str.lower():
                    table_name = query_str.split()[2]
                    if self.table_exists(table_name):
                        cursor.execute(f'SELECT id FROM {table_name} WHERE rowid=last_insert_rowid();')
                return cursor.fetchall()

        except sqlite3.Error as e:
            print(f"SQLite error: {e.args[0]}")
            print("Query string:", query_str)
            print("Parameters:", parameters)
            raise
        finally:
            cursor.close()

    def table_exists(self, table_name: str) -> bool:
        check_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        return len(self.execute_query(check_query)) > 0

    def __str__(self):
        return f'{self._db_name} – {str(self._connection)}'