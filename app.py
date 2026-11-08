
import streamlit as st
import pandas as pd
from nycflights13 import flights, airlines

# Configure the application
st.set_page_config(page_title="FlightOps Lite", page_icon="✈️", layout="wide")

st.title("✈️ FlightOps Lite")
st.write("Explore real airline performance data from NYC airports in 2013.")

# Load flight data
df = flights.copy()

# Replace airline codes with full airline names
df = df.merge(airlines, on="carrier", how="left")

# Add a sidebar filter
st.sidebar.header("Filters")

airline_names = sorted(df["name"].dropna().unique())
selected_airline = st.sidebar.selectbox(
    "Select an airline",
    ["All Airlines"] + list(airline_names)
)

if selected_airline != "All Airlines":
    df = df[df["name"] == selected_airline]


# Filter flights by departure airport
selected_airport = st.sidebar.selectbox(
    "Select a departure airport",
    ["All Airports", "JFK", "LGA", "EWR"]
)

if selected_airport != "All Airports":
    df = df[df["origin"] == selected_airport]
    
# Save data before applying the month filter
yearly_df = df.copy()


# Filter flights by month
months = {
    "All Months": 0,
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

selected_month = st.sidebar.selectbox(
    "Select a month",
    list(months.keys())
)

if selected_month != "All Months":
    df = df[df["month"] == months[selected_month]]

# Check whether the selected filters have any matching flights
if df.empty:
    st.warning(
        "No flights found for these filters. "
        "Try selecting a different airline, airport, or month."
    )
    st.stop()

# Only analyze flights with recorded departure delay times
valid_flights = df.dropna(subset=["dep_delay"])

# Track missing departure-delay records
missing_delays = df["dep_delay"].isna().sum()

if missing_delays > 0:
    st.info(
        f"{missing_delays:,} flights have no recorded departure delay. "
        "These flights are excluded from delay calculations."
    )

# Calculate statistics
total_flights = len(df)

# Count flights that never departed
cancelled_flights = df["dep_time"].isna().sum()
cancellation_percentage = (cancelled_flights / total_flights) * 100 if total_flights > 0 else 0

measured_flights = len(valid_flights)
average_delay = valid_flights["dep_delay"].mean()
delayed_percentage = (valid_flights["dep_delay"] > 15).mean() * 100

# Display summary
st.subheader("Flight Performance Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Flights", f"{total_flights:,}")
col2.metric("Average Departure Delay", f"{average_delay:.1f} min")
col3.metric("Delayed Flights (>15 min)", f"{delayed_percentage:.1f}%")
col4.metric(
    "No Recorded Departure",
    f"{cancelled_flights:,}",
    help=f"{cancellation_percentage:.1f}% of selected flights"
)


st.caption(
    f"Delay statistics use {measured_flights:,} flights with recorded "
    "departure delays. Missing delay values are excluded."
)

# Compare airlines using a chart
st.subheader("Average Departure Delay by Airline")

chart_data = (
    valid_flights.groupby("name")["dep_delay"]
    .mean()
    .sort_values(ascending=False)
)


st.bar_chart(
    chart_data,
    horizontal=True,
    height=750,
    width="stretch",
    sort=False
)



# Monthly delay trends
st.subheader("Monthly Departure Delay Trends")

monthly_delays = (
    yearly_df.dropna(subset=["dep_delay"])
    .groupby("month")["dep_delay"]
    .mean()
    .reset_index()
)

monthly_delays = monthly_delays.rename(
    columns={
        "month": "Month",
        "dep_delay": "Average Delay (minutes)"
    }
)

st.line_chart(
    monthly_delays,
    x="Month",
    y="Average Delay (minutes)"
)

# Display a preview of the dataset
st.subheader("Flight Records")

st.dataframe(
    df[["name", "origin", "dest", "dep_delay", "arr_delay"]].head(100),
    width="stretch"
)


# Allow users to download filtered flight data
st.subheader("Export Flight Data")

export_columns = [
    "name",
    "origin",
    "dest",
    "month",
    "day",
    "dep_delay",
    "arr_delay"
]

csv_data = df[export_columns].to_csv(index=False)

st.download_button(
    label="Download Filtered Flights (CSV)",
    data=csv_data,
    file_name="flightops_filtered_flights.csv",
    mime="text/csv"
)
