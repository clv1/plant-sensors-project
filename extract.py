from multiprocessing import Pool
import requests

URL = "https://data-eng-plants-api.herokuapp.com/plants/"


def get_plant_data(plant_range: list[int]) -> list[dict]:
    return [requests.get(f'{URL}{plant}').json() for plant in plant_range]


def extract_main():
    """Multiprocessing of all plants and building their data into a dataframe"""
    plant_segments = [[num for num in range(0, 13
                                            )], [num for num in range(13, 26
                                                                      )], [num for num in range(26, 39
                                                                                                )], [num for num in range(39, 50)]]

    with Pool(processes=4) as pool:
        data_segments = pool.map(get_plant_data, plant_segments)

    return data_segments


if __name__ == "__main__":
    extract_main()
