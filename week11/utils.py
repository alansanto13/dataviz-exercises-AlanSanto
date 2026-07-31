# utils.py
# Shared data loading — put @st.cache_data functions here so every page
# reuses the SAME cached result instead of re-reading the CSV from disk.

import os

import pandas as pd
import streamlit as st

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "gapminder.csv")


@st.cache_data
def load_gapminder():
    """Load the Gapminder snapshot dataset.

    Cache key = this function itself, so app.py and every page in
    pages/ that call load_gapminder() share one cached DataFrame.
    """
    return pd.read_csv(DATA_PATH)