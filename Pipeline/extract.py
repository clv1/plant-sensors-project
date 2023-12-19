"""Contains functions that extract the plant data from the plants api"""

from multiprocessing import Pool
import requests

URL = "https://data-eng-plants-api.herokuapp.com/plants/"


def get_plant_data(plant_range: list[int]) -> list[dict]:
    """Gets the data from the plants api"""
    return [requests.get(f'{URL}{plant}').json() for plant in plant_range]


def extract_main() -> list[list[dict]]:
    """Multiprocessing to get all plants from the api quicker"""
    plant_segments = [list(range(0, 13)), list(
        range(13, 26)), list(range(26, 39)), list(range(39, 50))]

    with Pool(processes=4) as pool:
        data_segments = pool.map(get_plant_data, plant_segments)

    return data_segments


if __name__ == "__main__":
    extract_main()
