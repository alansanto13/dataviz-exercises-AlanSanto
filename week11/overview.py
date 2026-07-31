import os
import sys

import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_gapminder

df = load_gapminder()

st.header("How do countries compare today?")
st.caption("Bubble = population | Colour = continent (BBD: categorical)")

continents = sorted(df["Continent"].unique())
selected = st.multiselect("Continent", continents, default=continents)
df_v = df[df["Continent"].isin(selected)]

if df_v.empty:
    st.warning("Select at least one continent.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Countries", len(df_v))
c2.metric("Avg Life Expectancy", f"{df_v['Life_expectancy'].mean():.1f} yrs")
c3.metric(
    "Richest country",
    df_v.loc[df_v["GDP_per_capita"].idxmax(), "Country"],
    f"${df_v['GDP_per_capita'].max():,.0f}",
)
st.divider()

# BBD CATEGORICAL colour: continent = unordered distinct category
fig = px.scatter(
    df_v, x="GDP_per_capita", y="Life_expectancy", size="Population", color="Continent",
    hover_name="Country", log_x=True, size_max=55,
    labels={"GDP_per_capita": "GDP per Capita (log)", "Life_expectancy": "Life Expectancy (yrs)"},
    title="Wealthier nations live longer — but diminishing returns above $10,000",
)
fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", font=dict(family="Arial", size=12))
fig.update_traces(marker=dict(opacity=0.75, line=dict(width=0.5, color="white")))
st.plotly_chart(fig, use_container_width=True)