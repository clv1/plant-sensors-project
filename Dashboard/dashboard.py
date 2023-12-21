"""Script that creates the dashbaord for the plant data"""

import streamlit as st
from dotenv import load_dotenv
import altair as alt
import pandas as pd
from dashboard_functions import get_db_connection, load_data_from_database


st.set_page_config(page_title="LMNH Plant Analysis",
                   page_icon=":bar_char:",
                   layout = "wide")

st.title(":bar_chart: :potted_plant: LMNH Plant Analysis :potted_plant: :bar_chart:")

# load_dotenv()
# connection = get_db_connection()

plants_data = pd.read_csv("example_dataset.csv")