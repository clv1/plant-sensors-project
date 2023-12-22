"""Contains functions that upload clean data to all tables in the database."""
import logging
from os import environ
import logging
from dotenv import load_dotenv
import pandas as pd
import pyodbc


from extract import extract_main
from transform import transform_main


def get_connection() -> pyodbc.Connection | None:
    """Connects to the database"""
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={environ["DB_HOST"]};DATABASE={environ["DB_NAME"]};UID={environ["DB_USER"]};PWD={environ["DB_PASSWORD"]}'

    # Establish a connection to the database
    try:
        connection = pyodbc.connect(conn_str)
        print("Connected to the database successfully!")
        logging.info("Database connection acquired.")
        return connection
    except pyodbc.Error as e:
        print("Error in connection: ", e)
        logging.info("Error in connection.")


def bulk_insert(connection: pyodbc.Connection, insert_query: str, insert_data: list[tuple]) -> None:
    """Execute the insert query using executemany"""
    cursor = connection.cursor()
    try:
        cursor.executemany(insert_query, insert_data)
        connection.commit()
        print('Bulk insert was successful.')

    except pyodbc.Error as e:
        print('Error during bulk insert:', e)

    cursor.close()


def upload_botanists(connection: pyodbc.Connection, dataframe: pd.DataFrame) -> None:
    """Uploads the botanist data to the botanist table"""
    insert_query = """
                    INSERT INTO s_alpha.botanist 
                        (first_name, last_name, email, phone_number) 
                    VALUES 
                        (?, ?, ?, ?)
                    """

    # get data from the database to check against input for duplicates
    botanist_query = """
                    SELECT 
                        first_name, last_name
                    FROM
                        s_alpha.botanist
                    ;
                    """
    cursor = connection.cursor()
    botanist_query_data = cursor.execute(botanist_query).fetchall()

    # build input data
    botanist_data = dataframe[["botanist_first_name",
                               "botanist_last_name", "email", "phone_number"]]
    botanist_tuples = list(botanist_data.itertuples(index=False, name=None))
    # Remove duplicates
    insert_data = list(set([i for i in botanist_tuples]))
    for botanist in insert_data:
        for query_botanist in botanist_query_data:
            if botanist[0] == query_botanist[0] and botanist[1] == query_botanist[1]:
                insert_data.pop(insert_data.index(botanist))
                break

    if len(insert_data) > 0:
        bulk_insert(connection, insert_query, insert_data)


def upload_origin_locations(connection: pyodbc.Connection, dataframe: pd.DataFrame) -> None:
    """Uploads the location data to the origin location table"""
    insert_query = """
                    INSERT INTO s_alpha.origin_location 
                        (longitude, latitude, town, country, country_abbreviation, continent) 
                    VALUES 
                        (?, ?, ?, ?, ?, ?)
                    """

    # get data from the database to check against input for duplicates
    location_query = """
                    SELECT 
                        longitude, latitude
                    FROM
                        s_alpha.origin_location
                    ;
                    """
    cursor = connection.cursor()
    location_query_data = cursor.execute(location_query).fetchall()

    # build input data
    location_data = dataframe[["longitude",
                               "latitude", "town", "country", "country_abbreviation", "continent"]]
    location_tuples = list(location_data.itertuples(index=False, name=None))

    # Remove duplicates
    insert_data = list(set([i for i in location_tuples]))

    for location in insert_data:
        for query_location in location_query_data:
            if float(location[0]) == float(query_location[0]) and float(
                    location[1]) == float(query_location[1]):
                insert_data.pop(insert_data.index(location))
                break

    if len(insert_data) > 0:
        bulk_insert(connection, insert_query, insert_data)


def upload_plants(connection: pyodbc.Connection, dataframe: pd.DataFrame) -> None:
    """Uploads the plant data to the plant table"""
    # get database data to find origin_location_ids
    origin_location_ids_query = """
                                SELECT 
                                    origin_location_id, longitude, latitude
                                FROM 
                                    s_alpha.origin_location
                                ;
                                """
    cursor = connection.cursor()
    location_query_data = cursor.execute(origin_location_ids_query).fetchall()

    insert_query = """
                    INSERT INTO s_alpha.plant 
                        (name, scientific_name, origin_location_id, image_url) 
                    VALUES 
                        (?, ?, ?, ?)
                    """

    # get data from the database to check against input for duplicates
    plant_query = """
                    SELECT 
                        name
                    FROM
                        s_alpha.plant
                    ;
                    """
    cursor = connection.cursor()
    plant_query_data = cursor.execute(plant_query).fetchall()

    # build input data
    plant_tuples = []
    for index, row in dataframe[["name", "longitude",
                                 "latitude", "scientific_name", "image_url"]].iterrows():
        for location in location_query_data:
            # link origin_location_ids
            if float(row["longitude"]) == float(location[1]) and float(
                    row["latitude"]) == float(location[2]):
                plant_tuples.append(
                    (row['name'], row["scientific_name"], location[0], row["image_url"]))
                break

    # remove duplicates
    for plant in plant_tuples:
        for query_plant in plant_query_data:
            if plant[0] == query_plant[0]:
                plant_tuples.pop(plant_tuples.index(plant))
                break

    if len(plant_tuples) > 0:
        bulk_insert(connection, insert_query,  plant_tuples)


def upload_recording_events(connection: pyodbc.Connection, dataframe: pd.DataFrame) -> None:
    """Uploads the recording event data to the recording event table"""
    # get database data to link botanist_ids
    botanist_query = """
                    SELECT 
                        botanist_id, first_name, last_name
                    FROM 
                        s_alpha.botanist
                    ;
                    """
    cursor = connection.cursor()
    botanist_query_data = cursor.execute(botanist_query).fetchall()

    # get database data to link plant ids
    plant_query = """
                    SELECT 
                        plant_id, name
                    FROM 
                        s_alpha.plant
                    ;
                    """
    cursor = connection.cursor()
    plant_query_data = cursor.execute(plant_query).fetchall()

    insert_query = """
                    INSERT INTO s_alpha.recording_event 
                        (plant_id, botanist_id, soil_moisture, temperature, recording_taken, last_watered) 
                    VALUES 
                        (?, ?, ?, ?, ?, ?)
                    """

    # build input data
    recording_tuples = []
    for index, row in dataframe[["name", "botanist_first_name", "botanist_last_name",
                                 "soil_moisture", "temperature", "recording_taken",
                                 "last_watered"]].iterrows():
        # link plant_ids
        for plant in plant_query_data:
            if row["name"] == plant[1]:
                plant_id = plant[0]
                break

        # link botanist_ids
        for botanist in botanist_query_data:
            if row["botanist_first_name"] == botanist[1] and row[
                    "botanist_last_name"] == botanist[2]:
                botanist_id = botanist[0]
                break

        recording_tuples.append((plant_id, botanist_id, row["soil_moisture"],
                                 row["temperature"], row["recording_taken"], row["last_watered"]))

    bulk_insert(connection, insert_query, recording_tuples)


def load_main(df: pd.DataFrame) -> None:
    """loads all data from the dataframe into its respective tables"""
    load_dotenv()

    logging.info("Getting Database Connection.")

    conn = get_connection()
    logging.info("Connected to the Database.")

    upload_botanists(conn, df)
    logging.info("Botanist data uploaded.")

    upload_origin_locations(conn, df)
    logging.info("Location data uploaded.")

    upload_plants(conn, df)
    logging.info("Plants data uploaded.")

    upload_recording_events(conn, df)
    logging.info("Recording event data uploaded.")



    conn.close()


if __name__ == "__main__":
    plant_data = extract_main()
    df = transform_main(plant_data)
    load_main(df)
