"""Small example of connecting to an MSSQL database."""
from os import environ
from dotenv import load_dotenv
import pandas as pd
import pyodbc


from extract import extract_main
from transform import transform_main


def get_connection():
    """Connects to the database"""
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={environ["DB_HOST"]};DATABASE={environ["DB_NAME"]};UID={environ["DB_USER"]};PWD={environ["DB_PASSWORD"]}'
    
    # Establish a connection to the database
    try:
        connection = pyodbc.connect(conn_str)
        print("Connected to the database successfully!")
        return connection
    except pyodbc.Error as e:
        print("Error in connection: ", e)


def bulk_insert(connection, insert_query, insert_data):
    """Execute the insert query using executemany"""
    cursor = connection.cursor()
    try:
        cursor.executemany(insert_query, insert_data)
        connection.commit() 
        print('Bulk insert was successful.')
        
    except pyodbc.Error as e:
        print('Error during bulk insert:', e)
    
    cursor.close()



def upload_botanists(connection, dataframe):
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



def upload_origin_locations(connection, dataframe):
    """Uploads the botanist data to the botanist table"""
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



def upload_plants(connection, dataframe):
    """Uploads the botanist data to the botanist table"""
    origin_location_ids_query = """
                                SELECT 
                                    origin_location_id, longitude, latitude
                                FROM 
                                    s_alpha.origin_location
                                ;
                                """
    cursor = connection.cursor()
    location_query_data = cursor.execute(origin_location_ids_query).fetchall()

    # location_query_data = [(1, -19.32556, -41.25528), (2, 33.95015, -118.03917), (3, 7.65649, 4.92235), (4, -19.32556, -41.25528), (5, 13.70167, -89.10944), (6, 22.88783, 84.13864), (7, 43.86682, -79.2663), (8, 5.27247, -3.59625), (9, 50.9803, 11.32903), (10, 43.50891, 16.43915), (11, 20.88953, -156.47432), (12, 32.5007, -94.74049), (13, 49.68369, 8.61839), (14, 29.65163, -82.32483), (15, 36.08497, 9.37082), (16, -7.51611, 109.05389), (17, 51.30001, 13.10984), (18, -21.44236, 27.46153), (19, 41.15612, 1.10687), (20, -29.2975, -51.50361), (21, 48.35693, 10.98461), (22, 52.53048, 13.29371), (23, 43.82634, 144.09638), (24, 11.8659, 34.3869), (25, 36.06386, 4.62744), (26, 51.67822, 33.9162), (27, 43.91452, -69.96533), (28, 34.75856, 136.13108), (29, 30.75545, 20.22625), (30, 23.29549, 113.82465), (31, 52.47774, 10.5511), (32, 28.92694, 78.23456), (33, 41.15612, 1.10687), (34, -32.45242, -71.23106), (35, 30.21121, 74.4818), (36, -6.8, 39.25), (37, 36.24624, 139.07204), (38, 44.92801, 4.8951), (39, 22.4711, 88.1453), (40, 41.57439, 24.71204), (41, 20.22816, -103.5687), (42, 33.95015, -118.03917), (43, -13.7804, 34.4587), (44, 14.14989, 121.3152), (45, 17.94979, -94.91386)]

    insert_query = """
                    INSERT INTO s_alpha.plant 
                        (name, scientific_name, origin_location_id, image_url) 
                    VALUES 
                        (?, ?, ?, ?)
                    """

    plant_tuples = []
    for index, row in dataframe[["name", "longitude", "latitude", "scientific_name", "image_url"]].iterrows():
        for location in location_query_data:
            if float(row["longitude"]) == float(location[1]) and float(row["latitude"]) == float(location[2]):
                plant_tuples.append((row['name'], row["scientific_name"], location[0], row["image_url"]))
                break

    bulk_insert(connection, insert_query,  plant_tuples)


def upload_recording_events(connection, dataframe):
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
    for index, row in dataframe[["name", "botanist_first_name", "botanist_last_name", "soil_moisture", "temperature", "recording_taken", "last_watered"]].iterrows():
        for plant in plant_query_data:
            if row["name"] == plant[1]:
                plant_id = plant[0]
                break

        for botanist in botanist_query_data:
            if row["botanist_first_name"] == botanist[1] and row["botanist_last_name"] == botanist[2]:
                botanist_id = botanist[0]
                break

        recording_tuples.append((plant_id, botanist_id, row["soil_moisture"], row["temperature"], row["recording_taken"], row["last_watered"]))
    
    bulk_insert(connection, insert_query, recording_tuples)
    


def load_main(df):
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

