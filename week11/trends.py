import os
import sys

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_gapminder

df = load_gapminder()

st.header("What explains the differences?")
st.caption("BBD squiggle: drill from summary → individual country story")

# session_state persists the selected country across reruns AND across tabs
if "highlight_country" not in st.session_state:
    st.session_state.highlight_country = "China"

countries = sorted(df["Country"].unique())
st.session_state.highlight_country = st.selectbox(
    "Highlight a country", countries,
    index=countries.index(st.session_state.highlight_country),
)
h = st.session_state.highlight_country
h_continent = df[df["Country"] == h]["Continent"].values[0]

tab1, tab2 = st.tabs(["GDP vs Life Expectancy", "Continent comparison"])

with tab1:
    # BBD/SWD HIGHLIGHT: one bold colour, all others grey
    colors = ["#E63946" if c == h else "#DDDDDD" for c in df["Country"]]
    fig1 = go.Figure(go.Scatter(
        x=df["GDP_per_capita"], y=df["Life_expectancy"],
        mode="markers", marker=dict(color=colors, size=9, opacity=0.85),
        text=df["Country"], hovertemplate="%{text}<extra></extra>",
    ))
    fig1.add_annotation(
        x=df[df["Country"] == h]["GDP_per_capita"].values[0],
        y=df[df["Country"] == h]["Life_expectancy"].values[0],
        text=f"<b>{h}</b>", showarrow=True, arrowhead=1, ax=40, ay=-30,
        font=dict(color="#E63946", size=11, family="Arial"),
    )
    fig1.update_xaxes(type="log", gridcolor="#EEEEEE", title="GDP per Capita (log)")
    fig1.update_yaxes(gridcolor="#EEEEEE", title="Life Expectancy (yrs)")
    fig1.update_layout(plot_bgcolor="white", paper_bgcolor="white", font=dict(family="Arial", size=12))
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    continent_df = df[df["Continent"] == h_continent].sort_values("Life_expectancy")
    colors2 = ["#E63946" if c == h else "#2E75B6" for c in continent_df["Country"]]
    fig2 = go.Figure(go.Bar(
        x=continent_df["Life_expectancy"], y=continent_df["Country"],
        orientation="h", marker_color=colors2, marker_line_width=0,
    ))
    fig2.update_layout(
        title=f"{h} vs {h_continent} peers — life expectancy",
        plot_bgcolor="white", paper_bgcolor="white", font=dict(family="Arial", size=12),
        xaxis=dict(gridcolor="#EEEEEE", range=[0, continent_df["Life_expectancy"].max() * 1.1]),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig2, use_container_width=True)

# BBD TEACHING POINT: this is the squiggle in action.
# Page 1 (summary) -> Page 2 (pattern across income tiers) -> Page 3 (individual story)
# The user keeps asking "why?" and each page answers the next question.