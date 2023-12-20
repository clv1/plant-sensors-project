'''Prepares string for use in handler function.'''
from os import environ
from dotenv import load_dotenv
import pandas as pd
import pprint
import json
import boto3
import pyodbc


def get_db_connection():
    """Connects to the database"""
    load_dotenv()
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={environ["DB_HOST"]};DATABASE={environ["DB_NAME"]};UID={environ["DB_USER"]};PWD={environ["DB_PASSWORD"]}'
    # Establish a connection to the database
    try:
        connection = pyodbc.connect(conn_str)
        print("Connected to the database successfully!")
        return connection
    except pyodbc.Error as e:
        print("Error in connection: ", e)


connection = get_db_connection()

with connection.cursor() as curr:
    curr.execute("""USE plants;""")
    curr.execute("""SELECT * FROM s_alpha.botanist;""")
    data = curr.fetchall()


# Temporary...will use a database connection :)
df = pd.read_csv('example_dataset.csv', index_col=0)

TEMP_RANGE_CONTINENT = {'America': [20, 35], 'Africa': [
    25, 35], 'Asia': [25, 35], 'Europe': [9, 25], 'Pacific': [25, 35]}
MOISTURE_LIMIT = [5, 60]

# --- PREVIOUS IDEA
# generate a baseline average temp and moisture data from
# (previously extracted from a bunch of database readings)
# set a range of +-10 (%)
# what happens to moisture when plant is watered - does it shoot up
# do some background research/visualisation to see existing patterns?

# --- CURRENT PLAN FOR HEALTH CHECK
# extract past 2-3 readings -> get average
# threshold = avg
# if temp is += 3˚C
# moisture should not be below -> 0%-5% or >60% (temporary parameters that can be easily adjusted after seeing more data)

client = boto3.client('ses', region_name='eu-west-2')

def check_plant_vitals(df: pd.DataFrame) -> list[dict]:
    '''Checks if a plants vitals are healthy, if not unhealthy plants are returned as a list.'''
    unhealthy_plants = []
    for index, plant in df.iterrows():
        continent = plant.get('continent')
        temp = plant.get('temperature')
        moisture = plant.get('soil_moisture')

        if continent in TEMP_RANGE_CONTINENT:
            temp_range = TEMP_RANGE_CONTINENT.get(f'{continent}')
            if not temp_range[0] <= temp or temp <= temp_range[1] and MOISTURE_LIMIT[0] <= moisture <= MOISTURE_LIMIT[1]:
                unhealthy_plants.append({
                    'plant_id': plant['plant_id'],
                    'temperature': temp,
                    'soil_moisture': moisture,
                    'botanist_email': plant['email'],
                    'optimum_temp': temp_range,
                    'continent': continent
                })
    return unhealthy_plants



def send_email(unhealthy_plants:list[dict]):
    plant_warning  = generate_html_string(unhealthy_plants)
   
    response = client.send_email(
        Destination={
            'ToAddresses': ['trainee.anurag.kaur@sigmalabs.co.uk', 'trainee.ishika.madhav@sigmalabs.co.uk']
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': plant_warning
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'Unhealthy Plant Detected by Sensor.',
            },
        },
        Source='trainee.anurag.kaur@sigmalabs.co.uk'
    )

    return response

def generate_html_string(plants:list[dict]) -> str:
    """Generates HTML string for the email"""

    warning_string = '<body>'

    for plant in plants:
        
        plant_id = plant.get('plant_id')
        temperature = plant.get('temperature')
        optimum_temp = plant.get('optimum_temp')

        if temperature > optimum_temp[1]:
            difference = temperature - optimum_temp[1]
            warning_string += f""" <li> Plant {plant_id} is above optimum temperature by {difference}. The optimum temperature range is {optimum_temp} but the temperature is {temperature} </li>"""
        
        if temperature < optimum_temp[0]:
            difference = optimum_temp[0] - temperature
            warning_string += f""" <li> Plant {plant_id} is below optimum temperature by {difference}. The optimum temperature range is {optimum_temp} but the temperature is {temperature} </li>"""
    
    warning_string += '</body>'
    return warning_string 


# def handler(event=check_plant_vitals(df), context=None): 
#     if event:
#         return send_email(event)
#     return None


if __name__ == "__main__":

    json = check_plant_vitals(df)
    send_email(json)
