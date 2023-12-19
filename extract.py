from multiprocessing import Pool
import requests
import pandas as pd

URL = "https://data-eng-plants-api.herokuapp.com/plants/"


def get_plant_data(plant_range: list[int]) -> list[list[str]]:
    """Gets plant data and collates it into a dataframe"""

    data = []

    for index, plant in enumerate(plant_range):
        print(f"{index + 1}/{len(plant_range)}")

        response = requests.get(f'{URL}{plant}').json()

        if response.get("error"):
            continue

        # gets botanist details
        first_name, last_name, email, phone_number = get_botanist(response)

        image_url = get_image(response)

        # gets location details
        longitude, latitude, town, country, country_abbreviation, continent = get_location(
            response)

        print(get_image(response))

        scientific_name = get_scientific_name(response)

        data.append([response.get("plant_id"), response.get(
            "name"), scientific_name, response.get("last_watered"), response.get("recording_taken"), response.get("soil_moisture"), response.get("temperature"), email, first_name, last_name, phone_number, image_url, longitude, latitude, town, country, country_abbreviation, continent])

    return make_dataframe(data)


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
    return pd.DataFrame(plants, columns=['plant_id', 'name', 'scientific_name', 'last_watered', 'recording_taken', 'soil_moisture', 'temperature', 'email',
                                         'botanist_first_name', 'botanist_last_name', 'phone_number', 'image_url', 'longitude', 'latitude', 'town', 'country', 'country_abbreviation', 'continent'])


def extract_main():
    """Multiprocessing of all plants and building their data into a dataframe"""
    plant_segments = [[num for num in range(0, 13
                                            )], [num for num in range(13, 26
                                                                      )], [num for num in range(26, 39
                                                                                                )], [num for num in range(39, 50)]]

    with Pool(processes=4) as pool:
        dataframe_segments = pool.map(get_plant_data, plant_segments)
        df = pd.DataFrame(columns=['plant_id', 'name', 'scientific_name', 'last_watered', 'recording_taken', 'soil_moisture', 'temperature', 'email',
                                   'botanist_first_name', 'botanist_last_name', 'phone_number', 'image_url', 'longitude', 'latitude', 'town', 'country', 'country_abbreviation', 'continent'])

        for dataframe_segment in dataframe_segments:
            df = df._append(dataframe_segment, ignore_index=True)
    return df


if __name__ == "__main__":

    df = extract_main()
    print(df)
