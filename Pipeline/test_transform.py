"""Script that tests the functions in transform.py"""

import pytest
from unittest.mock import patch
from datetime import datetime

from transform import *

TEST_DICT = {'botanist': {'email': 'eliza.andrews@lnhm.co.uk', 'name': 'Eliza Andrews', 'phone': '(846)669-6651x75948'},
             'images': {'license': 4, 'license_name': 'Attribution License', 'license_url': 'https://creativecommons.org/licenses/by/2.0/',
                        'medium_url': 'https://perenual.com/storage/species_image/2193_crassula_ovata/medium/33253726791_980c738a1e_b.jpg',
                        'original_url': 'https://perenual.com/storage/species_image/2193_crassula_ovata/og/33253726791_980c738a1e_b.jpg',
                        'regular_url': 'https://perenual.com/storage/species_image/2193_crassula_ovata/regular/33253726791_980c738a1e_b.jpg',
                        'small_url': 'https://perenual.com/storage/species_image/2193_crassula_ovata/small/33253726791_980c738a1e_b.jpg',
                        'thumbnail': 'https://perenual.com/storage/species_image/2193_crassula_ovata/thumbnail/33253726791_980c738a1e_b.jpg'},
             'last_watered': 'Wed, 20 Dec 2023 14:02:15 GMT', 'name': 'Crassula Ovata', 'origin_location': ['17.94979', '-94.91386',
                                                                                                            'Acayucan', 'MX', 'America/Mexico_City'], 'plant_id': 49, 'recording_taken': '2023-12-21 10:29:12',
             'scientific_name': ['Crassula ovata'], 'soil_moisture': 28.457718736637517, 'temperature': 9.391985356472631}


def test_get_recording_taken():
    assert get_recording_taken(TEST_DICT) == datetime(2023, 12, 21, 10, 29, 12)


def test_get_last_watered():
    assert get_last_watered(TEST_DICT) == datetime(2023, 12, 20, 14, 2, 15)
