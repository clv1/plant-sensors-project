"""Script that contains the functions for the dashboard"""

from os import environ
from dotenv import load_dotenv
import pyodbc
import pandas as pd


def get_db_connection():
    """Connects to the database"""
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={environ["DB_HOST"]};DATABASE={environ["DB_NAME"]};UID={environ["DB_USER"]};PWD={environ["DB_PASSWORD"]}'
    # Establish a connection to the database
    try:
        connection = pyodbc.connect(conn_str)
        print("Connected to the database successfully!")
        return connection
    except pyodbc.Error as e:
        print("Error in connection: ", e)


def load_data_from_database(connection):
    """Loads all the truck data from the database"""

    with connection.cursor() as curr:
        curr.execute("""USE plants;""")
        curr.execute("""
        SELECT * FROM s_alpha.botanist;""")
        data = curr.fetchall()
        columns = ['botanist_id']
        df = pd.DataFrame(data, columns=columns)
        return df

if __name__ == "__main__":

    load_dotenv()

    connection = get_db_connection()

    botanists = load_data_from_database(connection)

    print(botanists)
