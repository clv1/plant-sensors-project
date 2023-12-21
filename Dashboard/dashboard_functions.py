"""Script that contains the functions for the dashboard"""

from os import environ
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import altair as alt
import pyodbc


LAST_24_LIMIT = (datetime.now() - timedelta(hours=24)
                 ).strftime("%Y-%m-%d %H:%M:%S")


def get_db_connection():
    """Connects to the database."""
    load_dotenv()
    conn_str = f"""DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={environ['DB_HOST']};DATABASE={environ['DB_NAME']};UID={environ['DB_USER']};PWD={environ['DB_PASSWORD']};"""

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
    query = """SELECT s_alpha.recording_event.*, s_alpha.plant.*, s_alpha.botanist.*,
                s_alpha.origin_location.*
                FROM s_alpha.recording_event
                JOIN s_alpha.plant
                ON s_alpha.plant.plant_id = s_alpha.recording_event.plant_id
                JOIN s_alpha.botanist
                ON s_alpha.botanist.botanist_id = s_alpha.recording_event.botanist_id J
                OIN s_alpha.origin_location
                ON s_alpha.origin_location.origin_location_id = s_alpha.plant.origin_location_id;"""
    data = pd.read_sql(query, conn)
    return data


def load_last_24_data(conn: pyodbc.Connection) -> pd.DataFrame:
    """Loads recordings data taken in the last 24 hours as a dataframe."""
    query = """SELECT s_alpha.recording_event.*, s_alpha.plant.*, s_alpha.botanist.*,
                s_alpha.origin_location.* FROM s_alpha.recording_event
                JOIN s_alpha.plant
                ON s_alpha.plant.plant_id = s_alpha.recording_event.plant_id
                JOIN s_alpha.botanist
                ON s_alpha.botanist.botanist_id = s_alpha.recording_event.botanist_id
                JOIN s_alpha.origin_location
                ON s_alpha.origin_location.origin_location_id = s_alpha.plant.origin_location_id
                WHERE recording_taken > ?;"""
    data = pd.read_sql(query, conn, params=(LAST_24_LIMIT,))
    return data


def get_unique_plant_ids(plants_data: pd.DataFrame) -> pd.DataFrame:

    plants_sorted_by_id = plants_data.sort_values(
        by='plant_id', ascending=True)
    unique_sorted_by_id = plants_sorted_by_id.drop_duplicates(
        subset='plant_id')

    return unique_sorted_by_id


def make_temperature_against_recording_graph(plants_data: pd.DataFrame, filter: list) -> alt.Chart:

    plants_data = plants_data[(plants_data['plant_id'].isin(filter))]

    temperature_per_reading_graph = alt.Chart(plants_data).mark_line().encode(
        x='recording_taken:T',
        y=alt.Y('temperature:Q', title='Temperature (°C)'),
        color='name:N'
    )

    return temperature_per_reading_graph


def make_moisture_against_recording_graph(plants_data: pd.DataFrame, filter: list) -> alt.Chart:

    plants_data = plants_data[(plants_data['plant_id'].isin(filter))]

    moisture_graph = alt.Chart(plants_data).mark_line().encode(
        x='recording_taken:T',
        y=alt.Y('soil_moisture:Q', title='Moisture as a %'),
        color='name:N'
    )

    return moisture_graph


if __name__ == "__main__":

    load_dotenv()

    connection = get_db_connection()

    data_1 = load_all_data(connection)

    data_2 = load_last_24_data(connection)

    print(data_2)
