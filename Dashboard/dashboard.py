"""Dashboard script."""
# Currently contains only DB-related functionality

from os import environ
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import pyodbc


LAST_24_LIMIT = (datetime.now() - timedelta(hours=24)
                 ).strftime("%Y-%m-%d %H:%M:%S")


def get_db_connection():
    """Connects to the database."""
    load_dotenv()
    conn_str = f"""DRIVER={{ODBC Driver 17 for SQL Server}};
                SERVER={environ['DB_HOST']};
                DATABASE={environ['DB_NAME']};
                UID={environ['DB_USER']};
                PWD={environ['DB_PASSWORD']};"""

    # Establish a connection to the database
    try:
        conn = pyodbc.connect(conn_str)
        print("Successfully connected to the database!")
        return conn
    except pyodbc.Error as e:
        print("Error connecting to database: ", e)

    return


def load_all_data(conn: pyodbc.Connection) -> pd.DataFrame:
    """Loads all recording event data as a dataframe."""
    query = "SELECT * FROM s_alpha.recording_event;"
    data = pd.read_sql(query, conn)
    return data


def load_last_24_data(conn: pyodbc.Connection) -> pd.DataFrame:
    """Loads recordings data taken in the last 24 hours as a dataframe."""
    query = """SELECT * FROM s_alpha.recording_event
            WHERE recording_taken > ?;"""
    data = pd.read_sql(query, conn, params=(LAST_24_LIMIT,))
    return data


if __name__ == "__main__":
    connection = get_db_connection()
    # print(load_all_data(connection))
    print(load_last_24_data(connection))
