"""Contains functions that extract the plant data from the plants api"""
import logging
from multiprocessing import Pool
import requests

URL = "https://data-eng-plants-api.herokuapp.com/plants/"


def get_plant_data(plant_range: list[int]) -> list[dict]:
    """Gets the data from the plants api"""

    if not isinstance(plant_range, list):
        raise TypeError('The plant range must be a list of integers')

    if not all(isinstance(x, int) for x in plant_range):
        raise TypeError('The plant range must be a list of integers')

    return [requests.get(f'{URL}{plant}').json() for plant in plant_range]


def extract_main() -> list[list[dict]]:
    """Multiprocessing to get all plants from the api quicker"""

    plant_segments = [list(range(0, 13)), list(
        range(13, 26)), list(range(26, 39)), list(range(39, 50))]

    with Pool(processes=4) as pool:
        logging.info('Extraction Started')
        data_segments = pool.map(get_plant_data, plant_segments)
        logging.info('Extraction Complete')

    return data_segments


if __name__ == "__main__":
    extract_main()
