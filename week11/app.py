# app.py — entry point
# BBD principle: page titles are QUESTIONS, not topic labels.
# Run with: streamlit run app.py

import streamlit as st

st.set_page_config(page_title="Gapminder Dashboard", layout="wide")

pg = st.navigation([
    st.Page("pages/01_overview.py",
            title="How do countries compare today?",     icon="🌍"),
    st.Page("pages/02_trends.py",
            title="How does wealth relate to emissions?", icon="📈"),
    st.Page("pages/03_compare.py",
            title="What explains the differences?",       icon="🔍"),
])
pg.run()