
from multiprocessing import Pool
import pandas as pd
from datetime import datetime
from extract import extract_main

COLUMNS = ['plant_id', 'name', 'scientific_name', 'last_watered', 'recording_taken', 'soil_moisture', 'temperature', 'email',
           'botanist_first_name', 'botanist_last_name', 'phone_number', 'image_url', 'longitude', 'latitude', 'town', 'country', 'country_abbreviation', 'continent']


def get_plant_data(plant_data) -> list[list[str]]:
    """Gets plant data and collates it into a dataframe"""
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

        scientific_name = get_scientific_name(plant)

        last_watered = get_last_watered(plant)
        recording_taken = get_recording_taken(plant)

        data.append([plant.get("plant_id"), plant.get(
            "name"), scientific_name, last_watered, recording_taken, plant.get("soil_moisture"), plant.get("temperature"), email, first_name, last_name, phone_number, image_url, longitude, latitude, town, country, country_abbreviation, continent])

    return make_dataframe(data)


def clean_data(df: pd.DataFrame) -> None:
    # remove_bad_temp = (pd.to_numeric(df.temperature) <= )
    pass


def format_phone_number():
    pass


def get_recording_taken(response: dict):
    recording_taken = response.get("recording_taken")
    return datetime.strptime(recording_taken,
                             '%Y-%m-%d %H:%M:%S')


def get_last_watered(response: dict) -> str:
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
    with Pool(processes=4) as pool:
        data_segments = pool.map(get_plant_data, plant_data)
        df = pd.DataFrame(columns=COLUMNS)

        # clean_data_segments = pool.map(clean_data, data_segments)
        for dataframe_segment in data_segments:
            df = df._append(dataframe_segment, ignore_index=True)

    return df


if __name__ == "__main__":
    plant_data = extract_main()
    df = transform_main(plant_data)

    print(df)
