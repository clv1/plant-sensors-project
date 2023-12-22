'''Prepares string for use in handler function.'''
from os import environ
from dotenv import load_dotenv
import pandas as pd
import boto3
from datetime import datetime
from pymssql import connect


def get_db_connection():

    conn = connect(
        server=environ["DB_HOST"],
        port=environ["DB_PORT"],
        user=environ["DB_USER"],
        password=environ["DB_PASSWORD"],
        database=environ["DB_NAME"],
        as_dict=True
    )

    return conn




def load_all_data(conn) -> pd.DataFrame:
    """Loads all recording event data as a dataframe."""

    query="""SELECT s_alpha.recording_event.*, s_alpha.plant.name, s_alpha.plant.image_url,
            s_alpha.botanist.first_name, s_alpha.botanist.last_name,
            s_alpha.origin_location.country
            FROM s_alpha.recording_event
            JOIN s_alpha.plant
            ON s_alpha.plant.plant_id = s_alpha.recording_event.plant_id
            JOIN s_alpha.botanist
            ON s_alpha.botanist.botanist_id = s_alpha.recording_event.botanist_id
            JOIN s_alpha.origin_location
            ON s_alpha.origin_location.origin_location_id = s_alpha.plant.origin_location_id;"""
    with conn.cursor() as curr:
        curr.execute(query)
        data = curr.fetchall()
    df = pd.DataFrame(data)
    return df

def load_current_data(connection):
    df = load_all_data(connection)
    current_time = datetime.now().minute
    df = df[df['recording_taken'].dt.minute == current_time]
    return df

def generate_avg_temp(df, plant:dict):
    name = plant.get('name')
    plant_df = df[df['name']==name]
    sort_by_time = plant_df.sort_values(by='recording_taken', ascending=False)
    last_recorded_values = sort_by_time.head(3)
    return last_recorded_values['temperature'].mean()


# --- CURRENT PLAN FOR HEALTH CHECK
# extract past 2-3 readings -> get average
# threshold = avg
# if temp is += 3˚C
# moisture should not be below -> 0%-5% or >60% (temporary parameters that can be easily adjusted after seeing more data)


def check_plant_vitals(df: pd.DataFrame) -> list[dict]:
    '''Checks if a plants vitals are healthy, if not unhealthy plants are returned as a list.'''
    unhealthy_plants = []
    for index, plant in df.iterrows():
        temp = plant.get('temperature')
        moisture = plant.get('soil_moisture')
        avg_temperature = int(generate_avg_temp(df, plant))
        if (avg_temperature-3) >= temp or temp >= (avg_temperature+3):
            unhealthy_plants.append({
                'plant_id': plant['plant_id'],
                'temperature': temp,
                'soil_moisture': moisture,
                'avg_temp': avg_temperature
            })
    return unhealthy_plants


def send_email(unhealthy_plants:list[dict]):
    plant_warning  = generate_html_string(unhealthy_plants)
    client = boto3.client('ses', region_name='eu-west-2', aws_access_key_id=environ["ACCESS_KEY_ID"],
                           aws_secret_access_key=environ["SECRET_ACCESS_KEY"])
   
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
        avg = plant.get('avg_temp')
        if temperature > avg:
            difference = temperature - avg
            warning_string += f""" <li> Plant {plant_id} is above optimum temperature by {difference}˚C. The average temperature is {avg}˚C but the temperature is {temperature}˚C </li>"""
        
        if temperature < avg:
            difference = avg - temperature
            warning_string += f""" <li> Plant {plant_id} is below optimum temperature by {difference}˚C. The average temperature is {avg}˚C but the temperature is {temperature}˚C</li>"""
    
    warning_string += '</body>'
    return warning_string 

def handler(event=None, context=None):
    load_dotenv()
    connection = get_db_connection()
    df = load_all_data(connection)
    unhealthy_plants = check_plant_vitals(df)
    if unhealthy_plants != []:
        return send_email(unhealthy_plants)
    return None


