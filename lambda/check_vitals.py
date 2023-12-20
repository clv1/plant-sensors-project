'''Prepares string for use in handler function.'''
from os import environ
from dotenv import load_dotenv
import pandas as pd

df = pd.read_csv('example_dataset.csv', index_col=0)

TEMP_RANGE_CONTINENT = {'America': [20, 35], 'Africa': [
    25, 35], 'Asia': [25, 35], 'Europe': [9, 25], 'Pacific': [25, 35]}
MOISTURE_LIMIT = [20, 60]


def check_plant_vitals(df: pd.core.frame.DataFrame) -> list[dict]:
    '''Checks if a plants vitals are healthy, if not unhealthy plants are returned as a list.'''
    unhealthy_plants = []
    for index, plant in df.iterrows():
        continent = plant.get('continent')
        temp = plant.get('temperature')
        moisture = plant.get('soil_moisture')

        if continent in TEMP_RANGE_CONTINENT:
            temp_range = TEMP_RANGE_CONTINENT.get(f'{continent}')
            if not temp_range[0] <= temp or temp <= temp_range[1] and moisture_limit[0] <= moisture <= moisture_limit[1]:
                unhealthy_plants.append({
                    'plant_id': plant['plant_id'],
                    'temperature': temp,
                    'soil_moisture': moisture,
                    'botanist_email': plant['email'],
                    'optimum_temp': temp_range,
                    'continent': continent
                })
    return unhealthy_plants



def handler(event=None, context=None):
    return {'message': check_plant_vitals(df)}
