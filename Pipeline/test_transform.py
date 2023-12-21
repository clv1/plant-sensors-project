"""Script that tests the functions in transform.py"""
# pylint: disable=C0301

from datetime import datetime
import pandas as pd
from transform import make_dataframe, make_plant_dataframe, get_botanist, get_image, get_last_watered, get_location, get_recording_taken, get_scientific_name, transform_main, clean_data

TEST_DICT = {'botanist': {'email': 'eliza.andrews@lnhm.co.uk', 'name': 'Eliza Andrews',
                          'phone': '(846)669-6651x75948'},
             'images': {'license': 4, 'license_name': 'Attribution License',
                        'license_url': 'https://creativecommons.org/licenses/by/2.0/',
                        'medium_url': 'https://perenual.com/storage/species_image/2193_crassula_ovata/medium/33253726791_980c738a1e_b.jpg',
                        'original_url': 'https://perenual.com/storage/species_image/2193_crassula_ovata/og/33253726791_980c738a1e_b.jpg',
                        'regular_url': 'https://perenual.com/storage/species_image/2193_crassula_ovata/regular/33253726791_980c738a1e_b.jpg',
                        'small_url': 'https://perenual.com/storage/species_image/2193_crassula_ovata/small/33253726791_980c738a1e_b.jpg',
                        'thumbnail': 'https://perenual.com/storage/species_image/2193_crassula_ovata/thumbnail/33253726791_980c738a1e_b.jpg'},
             'last_watered': 'Wed, 20 Dec 2023 14:02:15 GMT', 'name': 'Crassula Ovata', 'origin_location': ['17.94979', '-94.91386',
                                                                                                            'Acayucan', 'MX', 'America/Mexico_City'], 'plant_id': 49, 'recording_taken': '2023-12-21 10:29:12',
             'scientific_name': ['Crassula ovata'], 'soil_moisture': 28.457718736637517, 'temperature': 9.391985356472631}

TEST_PLANT_LIST = [[0, 'Epipremnum Aureum', None, datetime(2023, 12, 20, 14, 3, 4), datetime(2023, 12, 21, 11, 4, 30), 26.73178776089061, 27.480069274006347, 'carl.linnaeus@lnhm.co.uk', 'Carl', 'Linnaeus', '(146)994-1635x35992', None, '-19.32556', '-41.25528', 'Resplendor', 'Sao_Paulo', 'BR', 'America'], [
    1, 'Venus flytrap', None, datetime(2023, 12, 20, 13, 54, 32), datetime(2023, 12, 21, 11, 4, 31), 25.00034452460629, 12.014886889446773, 'gertrude.jekyll@lnhm.co.uk', 'Gertrude', 'Jekyll', '001-481-273-3691x127', None, '33.95015', '-118.03917', 'South Whittier', 'Los_Angeles', 'US', 'America']]

BAD_TEMP_PLANT_LIST = [[0, 'Epipremnum Aureum', None, datetime(2023, 12, 20, 14, 3, 4), datetime(2023, 12, 21, 11, 4, 30), 26.73178776089061, 50, 'carl.linnaeus@lnhm.co.uk', 'Carl', 'Linnaeus', '(146)994-1635x35992', None, '-19.32556', '-41.25528', 'Resplendor', 'Sao_Paulo', 'BR', 'America'], [
    1, 'Venus flytrap', None, datetime(2023, 12, 20, 13, 54, 32), datetime(2023, 12, 21, 11, 4, 31), 25.00034452460629, 12.014886889446773, 'gertrude.jekyll@lnhm.co.uk', 'Gertrude', 'Jekyll', '001-481-273-3691x127', None, '33.95015', '-118.03917', 'South Whittier', 'Los_Angeles', 'US', 'America']]


BAD_MOISTURE_PLANT_LIST = [[0, 'Epipremnum Aureum', None, datetime(2023, 12, 20, 14, 3, 4), datetime(2023, 12, 21, 11, 4, 30), -10, 27.480069274006347, 'carl.linnaeus@lnhm.co.uk', 'Carl', 'Linnaeus', '(146)994-1635x35992', None, '-19.32556', '-41.25528', 'Resplendor', 'Sao_Paulo', 'BR', 'America'], [
    1, 'Venus flytrap', None, datetime(2023, 12, 20, 13, 54, 32), datetime(2023, 12, 21, 11, 4, 31), 25.00034452460629, 12.014886889446773, 'gertrude.jekyll@lnhm.co.uk', 'Gertrude', 'Jekyll', '001-481-273-3691x127', None, '33.95015', '-118.03917', 'South Whittier', 'Los_Angeles', 'US', 'America']]


COLUMNS = ['plant_id', 'name', 'scientific_name', 'last_watered', 'recording_taken',
           'soil_moisture', 'temperature', 'email', 'botanist_first_name',
           'botanist_last_name', 'phone_number', 'image_url', 'longitude',
           'latitude', 'town', 'country', 'country_abbreviation', 'continent']


def test_get_recording_taken():
    """Tests that the recording taken string is converted into the correct datetime."""
    assert get_recording_taken(TEST_DICT) == datetime(2023, 12, 21, 10, 29, 12)


def test_get_last_watered():
    """Tests that the last watered string is converted into the correct datetime."""
    assert get_last_watered(TEST_DICT) == datetime(2023, 12, 20, 14, 2, 15)


def test_get_image():
    """Tests that the correct image is obtained using get_image()."""
    assert get_image(
        TEST_DICT) == 'https://perenual.com/storage/species_image/2193_crassula_ovata/og/33253726791_980c738a1e_b.jpg'


def test_get_no_image():
    """Tests that no image is obtained using get_image() on an empty dict."""
    assert get_image({}) is None


def test_get_scientific_name():
    """Tests that the correct scientific name is obtained using get_scientific_name()."""
    assert get_scientific_name(TEST_DICT) == 'Crassula ovata'


def test_get_no_scientific_name():
    """Tests that no scientific name is obtained using get_scientific_name() on an empty dict."""
    assert get_scientific_name({}) is None


def test_get_location():
    """Tests that the correct location is obtained using get_location()."""
    assert get_location(TEST_DICT) == (
        '17.94979', '-94.91386', 'Acayucan', 'Mexico_City', 'MX', 'America')


def test_get_botanist():
    """Tests that the correct botanist is obtained using get_botanist()."""
    assert get_botanist(TEST_DICT) == ('Eliza', 'Andrews',
                                       'eliza.andrews@lnhm.co.uk', '(846)669-6651x75948')


def test_make_dataframe():
    """Tests that a dataframe with the correct column names is made using make_dataframe()."""
    df = make_dataframe(TEST_PLANT_LIST)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == COLUMNS


def test_transform_main():
    """Tests that a dataframe with the correct column names is made using transform_main()."""
    df = transform_main([[TEST_DICT]])
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == COLUMNS


def test_clean_data_temp():
    """Tests that the dataframe has entries removed that are invalid temperatures."""
    df = pd.DataFrame(BAD_TEMP_PLANT_LIST, columns=COLUMNS)
    assert isinstance(df, pd.DataFrame)
    assert len(df.index) == 2
    df = clean_data(df)
    assert len(df.index) == 1


def test_clean_data_bad_moisture():
    """Tests that the dataframe has entries removed that are invalid soil moistures."""
    df = pd.DataFrame(BAD_MOISTURE_PLANT_LIST, columns=COLUMNS)
    assert isinstance(df, pd.DataFrame)
    assert len(df.index) == 2
    df = clean_data(df)
    assert len(df.index) == 1


def test_clean_data_good():
    """Tests that clean data removes only bad values"""
    df = pd.DataFrame(TEST_PLANT_LIST, columns=COLUMNS)
    assert isinstance(df, pd.DataFrame)
    assert len(df.index) == 2
    df = clean_data(df)
    assert len(df.index) == 2


def test_make_plant_dataframe():
    """Tests a dataframe of correct length is made with the correct column names."""
    df = make_plant_dataframe([TEST_DICT])
    assert isinstance(df, pd.DataFrame)
    assert len(df.index) == 1
    assert list(df.columns) == COLUMNS
