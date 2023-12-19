import requests
import pandas as pd


def get_plant_data() -> list[list[str]]:
    plant_range = [num for num in range(0, 1)]
    url = "https://data-eng-plants-api.herokuapp.com/plants/"
    # return [requests.get(f'{url}{plant}').json() for plant in plant_range]
    data = []
    for plant in plant_range:
        response = requests.get(f'{url}{plant}').json()
        # print(response)
        botanist = response.get("botanist")
        email = botanist.get("email")
        first_name = botanist.get("name").split()[0]
        last_name = botanist.get("name").split()[1]
        phone_number = botanist.get("phone")

        image_url = response.get("images").get("original_url")

        location = response.get("origin_location")
        longitude = location[0]
        latitude = location[1]
        town = location[2]
        country_abbreviation = location[3]
        country = location[4].split("/")[1]
        continent = location[4].split("/")[0]

        data.append([response.get("plant_id"), response.get(
            "name"), response.get("scientific_name")[0], response.get("last_watered"), response.get("recording_taken"), response.get("soil_moisture"), response.get("temperature"), email, first_name, last_name, phone_number, image_url, longitude, latitude, town, country, country_abbreviation, continent])
    return data


def make_dataframe(plants: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(columns=['plant_id', 'name', 'scientific_name'])


if __name__ == "__main__":
    plants = get_plant_data()
    print(plants)
    # df = pd.DataFrame(response)
    # print(df)
