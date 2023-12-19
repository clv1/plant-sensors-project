from os import environ
from dotenv import load_dotenv
import pandas as pd

df = pd.read_csv('example_dataset.csv', index_col=0)

temp_range_continent = {'America': [20, 35], 'Africa': [
    25, 35], 'Asia': [25, 35], 'Europe': [9, 25], 'Pacific': [25, 35]}
moisture_limit = [20, 60]


def check_plant_vitals(plant: dict):
    continent = plant.get('continent')
    temp = plant.get('temperature')
    moisture = plant['soil_moisture']

    if continent in temp_range_continent:
        temp_range = temp_range_continent.get(f'{continent}')
        if temp_range[0] >= temp or temp >= temp_range[1] or moisture_limit[0] >= moisture >= moisture_limit[1]:
            print("plant is unhealthy")
            return {
                'plant_id': plant['plant_id'],
                'temperature': temp,
                'soil_moisture': moisture,
                'botanist_email': plant['email']
            }
    return 'plant healthy'


for _, plant in df:
    fault_string = check_plant_vitals(plant)

    def handler(event=None, context=None):
        return {'message': fault_string}
