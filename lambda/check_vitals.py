'''Prepares string for use in handler function.'''
from os import environ
from dotenv import load_dotenv
import pandas as pd
import pprint
import json
import boto3

# Temporary...will use a database connection :)
df = pd.read_csv('example_dataset.csv', index_col=0)

TEMP_RANGE_CONTINENT = {'America': [20, 35], 'Africa': [
    25, 35], 'Asia': [25, 35], 'Europe': [9, 25], 'Pacific': [25, 35]}
MOISTURE_LIMIT = [5, 60]

# generate a baseline average temp and moisture data from
# (previously extracted from a bunch of database readings)
# set a range of +-10 (%)
# what happens to moisture when plant is watered - does it shoot up
# do some background research/visualisation to see existing patterns?

# extract past 2-3 readings -> get average
# threshold = avg
# if temp is += 3˚C
# moisture should not be below -> 0%-5%


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


def send_email():
    response = client.send_email(
        Destination={
            'ToAddresses': ['trainee.anurag.kaur@sigmalabs.co.uk']
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': 'This is the message body in text format.',
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'Unhealthy Plant',
            },
        },
        Source='SourceEmailAddress'
    )

    print(response)

    return {
        'statusCode': 200,
        'body': json.dumps("Email Sent Successfully. MessageId is: " + response['MessageId'])
    }


# we want to send an email only IF there are unhealthy plants (i.e. unhealthy_plants list is empty)
# Q: what does the message in the handler go to?
def handler(event=None, context=None):
    return {'message': check_plant_vitals(df)}


if __name__ == "__main__":
    pprint.pprint(check_plant_vitals(df))
