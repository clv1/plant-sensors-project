from multiprocessing import Pool
import requests
import pandas as pd


def get_plant_data(plant_range: list[int]) -> list[list[str]]:
    url = "https://data-eng-plants-api.herokuapp.com/plants/"
    data = []
    i = 1
    for plant in plant_range:
        print(f"{i}/{len(plant_range)}")
        i += 1

        response = requests.get(f'{url}{plant}').json()

        if response.get("error"):
            continue

        first_name, last_name, email, phone_number = get_botanist(response)

        image_url = get_image(response)

        longitude, latitude, town, country, country_abbreviation, continent = get_location(
            response)

        if response.get("scientific_name"):
            scientific_name = response.get("scientific_name")[0]
        else:
            scientific_name = None

        data.append([response.get("plant_id"), response.get(
            "name"), scientific_name, response.get("last_watered"), response.get("recording_taken"), response.get("soil_moisture"), response.get("temperature"), email, first_name, last_name, phone_number, image_url, longitude, latitude, town, country, country_abbreviation, continent])

    return make_dataframe(data)


def get_image(response):
    if response.get("images"):
        return response.get("images").get("original_url")


def get_location(response: dict) -> list[str]:
    location = response.get("origin_location")
    if location:
        longitude = location[0]
        latitude = location[1]
        town = location[2]
        country_abbreviation = location[3]
        country = location[4].split("/")[1]
        continent = location[4].split("/")[0]
    return longitude, latitude, town, country, country_abbreviation, continent


def get_botanist(response: dict) -> list[str]:
    botanist = response.get("botanist")
    if botanist:
        email = botanist.get("email")
        first_name = botanist.get("name").split()[0]
        last_name = botanist.get("name").split()[1]
        phone_number = botanist.get("phone")
    return first_name, last_name, email, phone_number


def make_dataframe(plants: list[list]) -> pd.DataFrame:
    df = pd.DataFrame(plants, columns=['plant_id', 'name', 'scientific_name', 'last_watered', 'recording_taken', 'soil_moisture', 'temperature', 'email',
                      'botanist_first_name', 'botanist_last_name', 'phone_number', 'image_url', 'longitude', 'latitude', 'town', 'country', 'country_abbreviation', 'continent'])

    return df


if __name__ == "__main__":
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

    print(df)
