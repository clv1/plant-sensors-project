"""Script that creates the dashbaord for the plant data"""

from dotenv import load_dotenv
import streamlit as st
import altair as alt
import pandas as pd
from dashboard_functions import get_db_connection, load_all_data, load_last_24_data, get_unique_plant_ids, make_temperature_graph, make_moisture_graph, make_country_pie_chart, get_botanists_and_plants, make_watered_per_day_chart, make_watered_per_hour_chart

if __name__ == "__main__":

    st.set_page_config(page_title="LMNH Plant Analysis",
                       page_icon=":bar_char:",
                       layout="wide")

    st.title(
        ":bar_chart: :potted_plant: LMNH Plant Analysis :potted_plant: :bar_chart:")

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
    add_selectbox = st.sidebar.selectbox(
        "Select this box if you would like to view data for the past 24 hours",
        ("All data", "Last 24 Hours")
    )

    # ---OVERVIEW-----
    st.subheader("Overview", divider='rainbow')

    col1, col2 = st.columns(2)

    num_of_plants = plants_data['name'].nunique()
    col1.metric("Total Number of Plants", num_of_plants)
    col2.write(get_botanists_and_plants(plants_data))

    # TEMPERATURE OVERTIME
    st.subheader('Temperature overtime', divider='rainbow')

    if add_selectbox == "All data":
        st.altair_chart(make_temperature_graph(
            plants_data, plant_id), use_container_width=True)

    if add_selectbox == "Last 24 Hours":
        st.altair_chart(make_temperature_graph(
            plants_data_24, plant_id), use_container_width=True)

    # MOISTURE OVERTIME
    st.subheader('Moisture overtime', divider='rainbow')

    if add_selectbox == "All data":
        st.altair_chart(make_moisture_graph(
            plants_data, plant_id), use_container_width=True)

    if add_selectbox == "Last 24 Hours":
        st.altair_chart(make_moisture_graph(
            plants_data_24, plant_id), use_container_width=True)

    # LAST WATERED

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("How many plants are being watered each day?")

        st.altair_chart(make_watered_per_day_chart(plants_data))

    with col2:
        st.subheader(
            "How many have been watered per hour in the last 24 hours?")

        st.altair_chart(make_watered_per_hour_chart(plants_data_24))

    # COUNTRIES AND PLANTS

    st.subheader('The Diversity of the plants based on Country')
    st.altair_chart(make_country_pie_chart(plants_data))
