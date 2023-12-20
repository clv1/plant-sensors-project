"""Small example of connecting to an MSSQL database."""
from os import environ
from dotenv import load_dotenv
from sqlalchemy import create_engine, sql
import pandas as pd
import pyodbc


from extract import extract_main
from transform import transform_main


def get_connection():
   # Set up your connection string
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={environ["DB_HOST"]};DATABASE={environ["DB_NAME"]};UID={environ["DB_USER"]};PWD={environ["DB_PASSWORD"]}'
    # Establish a connection to the database
    try:
        connection = pyodbc.connect(conn_str)
        print("Connected to the database successfully!")
        return connection
    except pyodbc.Error as e:
        print("Error in connection: ", e)


def upload_botanists(conn):
    """Uploads the botanist data to the botanist table"""
    cursor = conn.cursor()
    insert_query = 'INSERT INTO s_alpha.botanist (first_name, last_name, email, phone_number) VALUES (?, ?, ?, ?)'

    botanist_data = dataframe[["botanist_first_name",
                      "botanist_last_name", "email", "phone_number"]]
    botanist_tuples = list(botanist_data.itertuples(index=False, name=None))

    # Execute the insert query using executemany
    try:
        cursor.executemany(insert_query, botanist_tuples)
        conn.commit() 
        print('Bulk insert was successful.')
    except pyodbc.Error as e:
        print('Error during bulk insert:', e)

    cursor.close()



if __name__ == "__main__":
    plant_data = extract_main()
    dataframe = transform_main(plant_data)

    load_dotenv()
    

    conn = get_connection()





    conn.close()
