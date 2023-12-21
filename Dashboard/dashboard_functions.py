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


def load_all_data(conn: pyodbc.Connection) -> pd.DataFrame:
    """Loads all recording event data as a dataframe."""
    query = """SELECT s_alpha.recording_event.*, s_alpha.plant.name, s_alpha.plant.image_url,
                s_alpha.botanist.first_name, s_alpha.botanist.last_name,
                s_alpha.origin_location.country
                FROM s_alpha.recording_event
                JOIN s_alpha.plant
                ON s_alpha.plant.plant_id = s_alpha.recording_event.plant_id
                JOIN s_alpha.botanist
                ON s_alpha.botanist.botanist_id = s_alpha.recording_event.botanist_id
                JOIN s_alpha.origin_location
                ON s_alpha.origin_location.origin_location_id = s_alpha.plant.origin_location_id;"""
    data = pd.read_sql(query, conn)
    return data


def load_last_24_data(conn: pyodbc.Connection) -> pd.DataFrame:
    """Loads recordings data taken in the last 24 hours as a dataframe."""
    query = """SELECT s_alpha.recording_event.*, s_alpha.plant.name, s_alpha.plant.image_url,
                s_alpha.botanist.first_name, s_alpha.botanist.last_name,
                s_alpha.origin_location.country
                FROM s_alpha.recording_event
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
    """Returns a dataframe of all the unique plant_id's in ascedning order"""

    plants_sorted_by_plant_id = plants_data.sort_values(
        by='plant_id', ascending=True)
    unique_sorted_by_plant_id = plants_sorted_by_plant_id.drop_duplicates(
        subset='plant_id')

    return unique_sorted_by_plant_id


def get_botanists_and_plants(plants_data: pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe of all the botanists and the plants they work on"""

    plants_data['botanist_name'] = plants_data['first_name'] + \
        ' ' + plants_data['last_name']

    botanists_and_plants = plants_data.drop_duplicates(
        subset=['botanist_name', 'plant_id'])

    botanists_and_plants = botanists_and_plants.groupby(
        'botanist_name')['plant_id'].agg(list).reset_index()
    botanists_and_plants.columns = ['botanist', 'plants_worked_with']

    return botanists_and_plants


def make_temperature_graph(plants_data: pd.DataFrame, selected: list) -> alt.Chart:
    """Makes a line chart that plots the temperature against the recording for each plant"""

    plants_data = plants_data[(plants_data['plant_id'].isin(selected))]

    temperature_per_reading_graph = alt.Chart(plants_data).mark_line().encode(
        x='recording_taken:T',
        y=alt.Y('temperature:Q', title='Temperature (°C)'),
        color='name:N'
    )

    return temperature_per_reading_graph


def make_moisture_graph(plants_data: pd.DataFrame, selected: list) -> alt.Chart:
    """Makes a line chart that plots the moisture against the recording for each plant"""

    plants_data = plants_data[(plants_data['plant_id'].isin(selected))]

    moisture_graph = alt.Chart(plants_data).mark_line().encode(
        x='recording_taken:T',
        y=alt.Y('soil_moisture:Q', title='Moisture as a %'),
        color='name:N'
    )

    return moisture_graph


def make_country_pie_chart(plants_data: pd.DataFrame) -> alt.Chart:
    """Makes a pie chart that shows all the different countries
    the LMNH plants come from and how many of them come from their"""

    unique_plants = plants_data.drop_duplicates(subset='plant_id')
    country_counts = unique_plants['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    plant_country_chart = alt.Chart(country_counts).mark_arc().encode(
        color='country:N',
        theta='count:Q'
    )

    return plant_country_chart


def make_watered_per_day_chart(plants_data: pd.DataFrame) -> alt.Chart:
    """Makes a bar chart that shows how many plants are being watered each day"""

    plants_data['date'] = plants_data['last_watered'].dt.date
    chart = alt.Chart(plants_data).mark_bar().encode(
        x=alt.X('date:O', title='date'),
        y=alt.Y('count():Q', title='Number of plants watered')
    )

    return chart


def make_watered_per_hour_chart(plants_data: pd.DataFrame) -> alt.Chart:
    """Makes a bar chart that shows how many plants are being watered each day"""

    plants_data['Hour'] = plants_data['last_watered'].dt.hour
    chart = alt.Chart(plants_data).mark_bar().encode(
        x=alt.X('Hour:O', title='Hour'),
        y=alt.Y('count():Q', title='Number of plants watered')
    )

    return chart


if __name__ == "__main__":

    connection = get_db_connection()

    data_1 = load_all_data(connection)

    data_2 = load_last_24_data(connection)

    print(data_1)
