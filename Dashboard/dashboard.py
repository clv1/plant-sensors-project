"""Script that creates the dashbaord for the plant data"""

import streamlit as st
from dotenv import load_dotenv
import altair as alt
import pandas as pd
from dashboard_functions import get_db_connection, load_all_data, load_last_24_data, get_unique_plant_ids, make_temperature_against_recording_graph, make_moisture_against_recording_graph, get_unique_botanists, make_country_pie_chart

if __name__ == "__main__":

    st.set_page_config(page_title="LMNH Plant Analysis",
                       page_icon=":bar_char:",
                       layout="wide")

    st.title(
        ":bar_chart: :potted_plant: LMNH Plant Analysis :potted_plant: :bar_chart:")

    load_dotenv()
    connection = get_db_connection()

    plants_data = load_all_data(connection)
    plants_data_24 = load_last_24_data(connection)

    plants_data['recording_taken'] = pd.to_datetime(
        plants_data['recording_taken'])
    plants_data['last_watered'] = pd.to_datetime(plants_data['last_watered'])

    # -----SIDEBAR-----

    st.sidebar.write(plants_data[['plant_id', 'name']].drop_duplicates())
    st.sidebar.header("Please Filter Here:")

    plant_id = st.sidebar.multiselect(
        "Select a Plant by it's ID 🪴 :",
        options=get_unique_plant_ids(plants_data).plant_id
    )
    botanists = st.sidebar.multiselect(
        "Select a Botanist 🧑‍🌾:",
        options=get_unique_botanists(plants_data).botanist_name
    )
    add_selectbox = st.sidebar.selectbox(
        "Select this box if you would like to view data for the past 24 hours?",
        ("All data", "Last 24 Hours")
    )

    # ---OVERVIEW-----
    st.subheader("Overview", divider='rainbow')
    num_of_plants = plants_data['name'].nunique()
    st.metric("Total Number of Plants", num_of_plants)

    # TEMPERATURE AND MOISTURE OF THE PLANTS AS TIME HAS GONE
    st.subheader('Temperature overtime', divider='rainbow')

    if add_selectbox == "All data":
        st.altair_chart(make_temperature_against_recording_graph(
            plants_data, 'plant_id', plant_id), use_container_width=True)
    if add_selectbox == "Last 24 Hours":
        st.altair_chart(make_temperature_against_recording_graph(
            plants_data_24, 'plant_id', plant_id), use_container_width=True)

    # MOISTURE OF PLANTS AS TIME HAS GONE
    st.subheader('Moisture overtime', divider='rainbow')

    if add_selectbox == "All data":
        st.altair_chart(make_moisture_against_recording_graph(
            plants_data, 'plant_id', plant_id), use_container_width=True)
    if add_selectbox == "Last 24 Hours":
        st.altair_chart(make_moisture_against_recording_graph(
            plants_data_24, 'plant_id', plant_id), use_container_width=True)

    # COUNTRIES AND PLANTS

    st.subheader('The Diveristy of the plants based on Country')
    st.altair_chart(make_country_pie_chart(plants_data))

    # Plant images

    for index, row in get_unique_plant_ids(plants_data).iterrows():
        st.subheader(f"Plant ID: {row['plant_id']}, Name: {row['name']}")
        if row['image_url']:
            st.image(row['image_url'], caption=row['name'])
