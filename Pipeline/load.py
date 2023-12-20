"""Small example of connecting to an MSSQL database."""
from os import environ
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
        return connection
    except pyodbc.Error as e:
        print("Error in connection: ", e)


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

    botanist_data = dataframe[["botanist_first_name",
                      "botanist_last_name", "email", "phone_number"]]
    botanist_tuples = list(botanist_data.itertuples(index=False, name=None))
    # Remove duplicates
    insert_data = list(set([i for i in botanist_tuples]))

    bulk_insert(connection, insert_query, insert_data)



def upload_origin_locations(connection: pyodbc.Connection, dataframe: pd.DataFrame) -> None:
    """Uploads the location data to the origin location table"""
    insert_query = """
                    INSERT INTO s_alpha.origin_location 
                        (longitude, latitude, town, country, country_abbreviation, continent) 
                    VALUES 
                        (?, ?, ?, ?, ?, ?)
                    """

    location_data = dataframe[["longitude",
                      "latitude", "town", "country", "country_abbreviation", "continent"]]
    location_tuples = list(location_data.itertuples(index=False, name=None))

    # Remove duplicates
    insert_data = list(set([i for i in location_tuples]))

    bulk_insert(connection, insert_query, insert_data)



def upload_plants(connection: pyodbc.Connection, dataframe: pd.DataFrame) -> None:
    """Uploads the plant data to the plant table"""
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

    plant_tuples = []
    for index, row in dataframe[["name", "longitude",
                                  "latitude", "scientific_name", "image_url"]].iterrows():
        for location in location_query_data:
            if float(row["longitude"]) == float(location[1]) and float(
                row["latitude"]) == float(location[2]):
                plant_tuples.append(
                    (row['name'], row["scientific_name"], location[0], row["image_url"]))
                break

    bulk_insert(connection, insert_query,  plant_tuples)


def upload_recording_events(connection: pyodbc.Connection, dataframe: pd.DataFrame) -> None:
    """Uploads the recording event data to the recording event table"""   
    botanist_query =  """
                    SELECT 
                        botanist_id, first_name, last_name
                    FROM 
                        s_alpha.botanist
                    ;
                    """
    cursor = connection.cursor()
    botanist_query_data = cursor.execute(botanist_query).fetchall()

    plant_query =  """
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

    recording_tuples = []
    for index, row in dataframe[["name", "botanist_first_name", "botanist_last_name", "soil_moisture",
                                  "temperature", "recording_taken", "last_watered"]].iterrows():
        for plant in plant_query_data:
            if row["name"] == plant[1]:
                plant_id = plant[0]
                break

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

    conn = get_connection()

    upload_botanists(conn, df)
    upload_origin_locations(conn, df)
    upload_plants(conn, df)
    upload_recording_events(conn, df)

    conn.close()


if __name__ == "__main__":
    plant_data = extract_main()
    df = transform_main(plant_data)
    load_main(df)
