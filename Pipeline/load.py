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


# def upload_botanists(conn, df: pd.Dataframe):
    # query = sql.text(
    #     "INSERT INTO s_alpha.botanist (first_name, last_name, email, phone_number) VALUES (:first_name, :last_name, :email, :phone_number)")

    # for botanist in df
    # conn.execute(query, {"first_name": first_name, "last_name": last_name,
    #              "email": email, "phone_number": phone_number})


if __name__ == "__main__":
    plant_data = extract_main()
    dataframe = transform_main(plant_data)

    load_dotenv()
    botanist_data = dataframe[["botanist_first_name",
                      "botanist_last_name", "email", "phone_number"]]

    conn = get_connection()
    cursor = conn.cursor()

    botanist_tuples = list(botanist_data.itertuples(index=False, name=None))

    # Define your insert query
    insert_query = 'INSERT INTO YourTableName (Column1, Column2, Column3) VALUES (?, ?, ?)'

    # Define the data you want to insert
    data_to_insert = [
        ('value1_row1', 'value2_row1', 'value3_row1'),
        ('value1_row2', 'value2_row2', 'value3_row2'),
        # Add as many rows as you need
    ]

    # Execute the insert query using executemany
    try:
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()  # Don't forget to commit to save changes
        print('Bulk insert was successful.')
    except pyodbc.Error as e:
        print('Error during bulk insert:', e)

    # Clean up
    cursor.close()
    conn.close()
