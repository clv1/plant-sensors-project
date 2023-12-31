"""Contains functions that collate and clean data extracted into a pandas dataframe."""

from datetime import datetime
import logging
from multiprocessing import Pool
import pandas as pd
from extract import extract_main

COLUMNS = ['plant_id', 'name', 'scientific_name', 'last_watered', 'recording_taken',
           'soil_moisture', 'temperature', 'email', 'botanist_first_name',
           'botanist_last_name', 'phone_number', 'image_url', 'longitude',
           'latitude', 'town', 'country', 'country_abbreviation', 'continent']

MIN_TEMP = 0
MAX_TEMP = 30
MIN_MOISTURE = 0
MAX_MOISTURE = 100


def make_plant_dataframe(plant_data: list[dict]) -> list[list[str]]:
    """Gets plant data and collates it into a dataframe"""

    if not isinstance(plant_data, list):
        raise TypeError('Plant data must be a list of dictionaries')

    data = []

    for plant in plant_data:
        if plant.get("error"):
            continue

        # gets botanist details
        first_name, last_name, email, phone_number = get_botanist(plant)

        image_url = get_image(plant)

        # gets location details
        longitude, latitude, town, country, country_abbreviation, continent = get_location(
            plant)

        if None in (first_name, last_name, email, phone_number, longitude, latitude, town, country, country_abbreviation, continent):
            continue

        scientific_name = get_scientific_name(plant)

        last_watered = get_last_watered(plant)
        recording_taken = get_recording_taken(plant)

        data.append([plant.get("plant_id"), plant.get(
            "name"), scientific_name, last_watered, recording_taken, plant.get("soil_moisture"),
            plant.get("temperature"), email, first_name, last_name, phone_number,
            image_url, longitude, latitude, town, country, country_abbreviation, continent])

    return make_dataframe(data)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans invalid data from the dataframe"""
    # Removes extreme temperature values from the dataframe
    remove_bad_temp = (pd.to_numeric(df.temperature) <= MIN_TEMP) | (
        pd.to_numeric(df.temperature) >= MAX_TEMP)

    df = df.drop(df[remove_bad_temp].index)

    # Removes invalid soil_moisture values from the dataframe
    remove_bad_moisture = (pd.to_numeric(df.soil_moisture) <= MIN_MOISTURE) | (
        pd.to_numeric(df.soil_moisture) >= MAX_MOISTURE)

    df = df.drop(df[remove_bad_moisture].index)

    return df


def get_recording_taken(response: dict) -> datetime:
    """Converts recording_taken time to a datetime object"""
    recording_taken = response.get("recording_taken")
    return datetime.strptime(recording_taken,
                             '%Y-%m-%d %H:%M:%S')


def get_last_watered(response: dict) -> datetime:
    """Converts last_watered time to a datetime object"""
    last_watered = response.get("last_watered")
    return datetime.strptime(last_watered,
                             '%a, %d %b %Y %H:%M:%S %Z')


def get_image(response: dict) -> str | None:
    """Gets the image url for the plant if there is one"""
    if response.get("images"):
        return response.get("images").get("original_url")


def get_scientific_name(response: dict) -> str | None:
    """Gets the scientific name for the plant if there is one"""
    if response.get("scientific_name"):
        return response.get("scientific_name")[0]


def get_location(response: dict) -> tuple[str]:
    """Gets all aspects of the location"""
    location = response.get("origin_location")

    longitude = location[0]
    latitude = location[1]
    town = location[2]
    country_abbreviation = location[3]
    country = location[4].split("/")[1]
    continent = location[4].split("/")[0]
    return longitude, latitude, town, country, country_abbreviation, continent


def get_botanist(response: dict) -> tuple[str]:
    """Gets all details of the botanist"""
    botanist = response.get("botanist")

    email = botanist.get("email")
    first_name = botanist.get("name").split()[0]
    last_name = botanist.get("name").split()[1]
    phone_number = botanist.get("phone")
    return first_name, last_name, email, phone_number


def make_dataframe(plants: list[list]) -> pd.DataFrame:
    """Makes an empty dataframe with correct heading names"""
    return pd.DataFrame(plants, columns=COLUMNS)


def transform_main(plant_data: list[list[dict]]) -> pd.DataFrame:
    """Takes data segments and parallel processes them to create a single dataframe."""
    with Pool(processes=4) as pool:
        logging.info("Transforming started.")
        data_segments = pool.map(make_plant_dataframe, plant_data)
        df = pd.DataFrame(columns=COLUMNS)

        logging.info("Cleaning Started")
        clean_data_segments = pool.map(clean_data, data_segments)
        for dataframe_segment in clean_data_segments:
            df = df._append(dataframe_segment, ignore_index=True)

    logging.info("Dataframe created and cleaned.")
    return df


if __name__ == "__main__":
    plant_data = extract_main()
    dataframe = transform_main(plant_data)
    print(dataframe)
