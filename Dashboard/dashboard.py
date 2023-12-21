"""Script that creates the dashbaord for the plant data"""

import streamlit as st
from dotenv import load_dotenv
import altair as alt
import pandas as pd
from dashboard_functions import get_db_connection, load_data_from_database


st.set_page_config(page_title="LMNH Plant Analysis",
                   page_icon=":bar_char:",
                   layout="wide")

st.title(":bar_chart: :potted_plant: LMNH Plant Analysis :potted_plant: :bar_chart:")

# load_dotenv()
# connection = get_db_connection()

plants_data = pd.concat(
    map(pd.read_csv, ['example_dataset_1.csv', 'example_dataset_2.csv', 'example_dataset_3.csv',
                      'example_dataset_4.csv', 'example_dataset_5.csv', 'example_dataset_6.csv']), ignore_index=True)

plants_data['recording_taken'] = pd.to_datetime(plants_data['recording_taken'])

plants_sorted_by_id = plants_data.sort_values(by='plant_id', ascending=True)
unique_sorted_by_id = plants_sorted_by_id.drop_duplicates(subset='plant_id')


# -----SIDEBAR-----
st.sidebar.header("Please Filter Here:")
selected_plants_by_ID = st.sidebar.multiselect(
    "Select a Plant by it's ID 🪴 :",
    options=unique_sorted_by_id
)
selected_plants_by_name = st.sidebar.multiselect(
    "Select a Plant by it's Name 🪴 :",
    options=plants_data['name'].unique()
)

selected_plants_by_day = st.sidebar.multiselect(
    "Select a Day 🗓️:",
    options=plants_data['recording_taken'].dt.date.unique()
)

filter_by_plant_id = plants_data[(
    plants_data['plant_id'].isin(selected_plants_by_ID))]
filter_by_plant_name = plants_data[(
    plants_data['plant_id'].isin(selected_plants_by_ID))]
filter_by_day = plants_data[(
    plants_data['plant_id'].isin(selected_plants_by_ID))]

# ---OVERVIEW-----
st.subheader("Overview", divider='rainbow')
num_of_plants = plants_data['name'].nunique()
st.metric("Total Number of Plants", num_of_plants)

# TEMPERATURE AND MOISTURE OF THE PLANTS AS TIME HAS GONE


temperature_per_reading_graph = alt.Chart(filter_by_plant_id).mark_line().encode(
    x='recording_taken:T',
    y='temperature:Q',
    color='name:N'
)

st.subheader('Temperature overtime', divider='rainbow')
st.altair_chart(temperature_per_reading_graph, use_container_width=True)
