import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes.
@st.cache_data
def load_data():
    path = Path(__file__).resolve().parent.parent / 'data' / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")

# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
#   a) st.selectbox for Region (with 'All')
#   b) st.multiselect for Countries (updates based on region — chained)
#   c) st.date_input for date range (two-handle; convert years to Jan-1 dates)
#   d) st.radio for Metric: "Total CO2 (Mt)" vs "CO2 per capita"
#   e) st.checkbox labelled "Show only top emitter highlighted"
#
# Guards:
#   - empty countries → st.warning + st.stop()
#   - incomplete date_input → st.warning + st.stop()
# Convert date_input result to pd.Timestamp before filtering.
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    # a) Region selectbox
    regions = ["All"] + sorted(df["Region"].unique().tolist())
    region = st.selectbox("Region", regions)

    # b) Countries multiselect — chained off the region choice
    if region == "All":
        countries_available = sorted(df["Country"].unique().tolist())
    else:
        countries_available = sorted(
            df.loc[df["Region"] == region, "Country"].unique().tolist()
        )
    countries = st.multiselect(
        "Countries", countries_available, default=countries_available
    )

    # c) Date range — two-handle date_input, converted from year bounds
    min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
    date_range = st.date_input(
        "Date range",
        value=(datetime(min_year, 1, 1), datetime(max_year, 1, 1)),
        min_value=datetime(min_year, 1, 1),
        max_value=datetime(max_year, 1, 1),
    )

    # d) Metric radio
    metric_label = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])
    metric_col = "CO2_Mt" if metric_label == "Total CO2 (Mt)" else "CO2_per_capita"

    # e) Highlight checkbox
    highlight_top = st.checkbox("Show only top emitter highlighted")

# ── Guards ─────────────────────────────────────────────────────────────────
if not countries:
    st.warning("Select at least one country to continue.")
    st.stop()

if len(date_range) != 2:
    st.warning("Please select a complete date range (start and end).")
    st.stop()

start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])

# ── Apply filters ────────────────────────────────────────────────────────────
filtered = df[
    (df["Country"].isin(countries))
    & (df["Date"] >= start_date)
    & (df["Date"] <= end_date)
]
if region != "All":
    filtered = filtered[filtered["Region"] == region]

# ── TASK 2: Filter summary caption ────────────────────────────────────────────
# Show: "X countries | Region | Date range | Metric"
# BBD rule: always show users how many records match current filters
# ─────────────────────────────────────────────────────────────────────────────
st.caption(
    f"**{len(countries)} countries** | {region} | "
    f"{start_date.year}–{end_date.year} | {metric_label} "
    f"({len(filtered)} records matched)"
)

# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
#   - Total CO2 in last year of selected range (sum across selected countries)
#   - % change from first to last year
#   - Country with highest emissions in last year
# ─────────────────────────────────────────────────────────────────────────────
if not filtered.empty:
    first_year_in_range = filtered["Year"].min()
    last_year_in_range = filtered["Year"].max()

    total_last_year = filtered.loc[filtered["Year"] == last_year_in_range, metric_col].sum()
    total_first_year = filtered.loc[filtered["Year"] == first_year_in_range, metric_col].sum()

    pct_change = (
        (total_last_year - total_first_year) / total_first_year * 100
        if total_first_year
        else 0
    )

    top_emitter_last_year = filtered.loc[
        filtered["Year"] == last_year_in_range
    ].sort_values(metric_col, ascending=False).iloc[0]["Country"]

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(f"Total {metric_label} ({last_year_in_range})", f"{total_last_year:,.1f}")
    kpi2.metric(
        f"Change since {first_year_in_range}",
        f"{pct_change:+.1f}%",
        delta=f"{pct_change:+.1f}%",
    )
    kpi3.metric(f"Top emitter ({last_year_in_range})", top_emitter_last_year)

# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
#   Left: line chart — selected metric over time, one line per country
#         If "Show only top emitter highlighted" checkbox is on:
#           - grey all lines except the highest emitter in the date range
#           - label that country at the end of its line (SWD grey-and-highlight)
#   Right: bar chart — ranking for the last year in selected date range
#
# BBD colour requirement: name the colour type in a comment next to each chart
# SWD requirements: white background, insight title, use_container_width=True
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    # Line chart — categorical colour palette (one distinct hue per country)
    top_emitter = (
        filtered.groupby("Country")[metric_col].sum().idxmax()
        if not filtered.empty
        else None
    )

    fig_line = px.line(
        filtered.sort_values("Date"),
        x="Date",
        y=metric_col,
        color="Country",
        title=(
            f"{top_emitter} leads on {metric_label.lower()} over the selected period"
            if top_emitter
            else f"{metric_label} over time"
        ),
    )

    if highlight_top and top_emitter is not None:
        # SWD grey-and-highlight: mute every line except the top emitter,
        # and use a single accent (highlight) colour instead of a full
        # categorical palette so the eye goes straight to the one that matters.
        for trace in fig_line.data:
            if trace.name == top_emitter:
                trace.line.color = "#D62728"  # highlight colour
                trace.line.width = 3
            else:
                trace.line.color = "#B0B0B0"  # grey (muted)
                trace.line.width = 1

        # Label the highlighted country at the end of its line
        last_point = filtered[filtered["Country"] == top_emitter].sort_values("Date").iloc[-1]
        fig_line.add_annotation(
            x=last_point["Date"],
            y=last_point[metric_col],
            text=top_emitter,
            showarrow=False,
            xanchor="left",
            font=dict(color="#D62728", size=12),
        )
        fig_line.update_layout(showlegend=False)

    fig_line.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=60, t=50, b=10),
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    # Bar chart — sequential colour scale (encodes the ranking magnitude)
    if not filtered.empty:
        last_year_in_range = filtered["Year"].max()
        last_year_df = filtered[filtered["Year"] == last_year_in_range].sort_values(
            metric_col, ascending=True
        )
        top_country_last_year = last_year_df.iloc[-1]["Country"]

        fig_bar = px.bar(
            last_year_df,
            x=metric_col,
            y="Country",
            orientation="h",
            color=metric_col,
            color_continuous_scale="Blues",
            title=f"{top_country_last_year} ranks highest in {last_year_in_range}",
        )
        fig_bar.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No data for the current filter selection.")