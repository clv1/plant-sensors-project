"""Script that creates the dashbaord for the plant data"""

import streamlit as st
from dotenv import load_dotenv
import altair as alt
import pandas as pd
from dashboard_functions import get_db_connection, load_data_from_database, get_unique_plant_ids, make_temperature_against_recording_graph, make_moisture_against_recording_graph


st.set_page_config(page_title="LMNH Plant Analysis",
                   page_icon=":bar_char:",
                   layout="wide")

st.title(
    ":bar_chart: :potted_plant: LMNH Plant Analysis :potted_plant: :bar_chart:")

# load_dotenv()
# connection = get_db_connection()

plants_data = pd.concat(
    map(pd.read_csv, ['example_dataset_1.csv', 'example_dataset_2.csv', 'example_dataset_3.csv',
                      'example_dataset_4.csv', 'example_dataset_5.csv', 'example_dataset_6.csv']), ignore_index=True)

plants_data['recording_taken'] = pd.to_datetime(
    plants_data['recording_taken'])
plants_data['last_watered'] = pd.to_datetime(plants_data['last_watered'])

# -----SIDEBAR-----

st.sidebar.write(plants_data[['plant_id', 'name']])
st.sidebar.header("Please Filter Here:")

plant_id = st.sidebar.multiselect(
    "Select a Plant by it's ID 🪴 :",
    options=get_unique_plant_ids(plants_data)
)
day = st.sidebar.multiselect(
    "Select a Day 🗓️:",
    options=plants_data['recording_taken'].dt.date.unique(),
)


# ---OVERVIEW-----
st.subheader("Overview", divider='rainbow')
num_of_plants = plants_data['name'].nunique()
st.metric("Total Number of Plants", num_of_plants)

# TEMPERATURE AND MOISTURE OF THE PLANTS AS TIME HAS GONE

st.subheader('Temperature overtime', divider='rainbow')
st.altair_chart(make_temperature_against_recording_graph(
    plants_data, plant_id), use_container_width=True)

# MOISTURE OF PLANTS AS TIME HAS GONE
st.subheader('Moisture overtime', divider='rainbow')
st.altair_chart(make_moisture_against_recording_graph(
    plants_data, plant_id), use_container_width=True)
