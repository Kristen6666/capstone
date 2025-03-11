
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("COVID-19 Dashboard")
st.write("This webapp displays daily or cumulative COVID-19 case counts from the Johns Hopkins CSSE COVID Dashboard.")

@st.cache_data
def load_data():
    url = (
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
        "csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    )
    df = pd.read_csv(url)
    # Convert wide-format data into long-format:
    # Date columns become a single 'Date' column; values go into 'Cumulative'
    df = df.melt(
        id_vars=["Province/State", "Country/Region", "Lat", "Long"],
        var_name="Date",
        value_name="Cumulative"
    )
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Date", "Country/Region"])
    return df

data = load_data()

st.sidebar.header("Options")
# Multi-select for countries (searchable by default)
all_countries = sorted(data["Country/Region"].unique())
selected_countries = st.sidebar.multiselect("Select Countries", all_countries, default=["US"])

# Radio button for display mode: "Cumulative" or "Daily"
display_mode = st.sidebar.radio("Display Mode", options=["Cumulative", "Daily"])

if not selected_countries:
    st.warning("Please select at least one country.")
    st.stop()

# Filter and aggregate data for selected countries
df_filtered = data[data["Country/Region"].isin(selected_countries)].copy()
df_filtered = df_filtered.groupby(["Date", "Country/Region"])["Cumulative"].sum().reset_index()

if display_mode == "Daily":
    # Compute daily new cases by taking differences for each country
    df_filtered = df_filtered.sort_values(["Country/Region", "Date"])
    df_filtered["Daily"] = df_filtered.groupby("Country/Region")["Cumulative"].diff().fillna(df_filtered["Cumulative"])
    df_filtered = df_filtered.rename(columns={"Daily": "Cases"})
else:
    df_filtered = df_filtered.rename(columns={"Cumulative": "Cases"})

# Create an interactive line chart using Plotly
fig = px.line(
    df_filtered,
    x="Date",
    y="Cases",
    color="Country/Region",
    title=f"{display_mode} COVID-19 Cases"
)
fig.update_layout(legend_title_text="Country")
st.plotly_chart(fig, use_container_width=True)

st.info("Use the sidebar to select countries and display mode.")
