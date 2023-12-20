"""Script that tests the functions in extract.py"""

import pytest
from unittest.mock import patch

from extract import get_plant_data

URL = "https://data-eng-plants-api.herokuapp.com/plants/"


def test_get_plants_data_not_a_list():
    """Tests that checks raises an error if plant range is not a list"""

    plant_range = '1,2,3,4,5'

    with pytest.raises(TypeError):
        get_plant_data(plant_range)


def test_get_plants_data_not_a_list_of_ints():
    """Tests that checks raises an error if plant range is not a list of ints"""

    plant_range_all_strings = ['1', '2', '3', '4']
    plant_range_one_string = [1, 2, 3, '4']

    with pytest.raises(TypeError):
        get_plant_data(plant_range_all_strings)

    with pytest.raises(TypeError):
        get_plant_data(plant_range_one_string)


def test_get_plants_data_success(requests_mock):
    """Test that checks get plant data is working"""

    plant_range = [1, 2, 3, 4, 5]
    for plant in plant_range:
        requests_mock.get(f"{URL}{plant}",
                          status_code=200, json=[{}])

    get_plant_data(plant_range)

    assert requests_mock.called
    assert requests_mock.call_count == 5
    assert requests_mock.last_request.method == "GET"
