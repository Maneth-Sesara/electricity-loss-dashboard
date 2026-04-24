import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Global Electricity Losses Dashboard",
    layout="wide"
)

st.title("Global Electricity Losses and Energy Efficiency Dashboard")

st.write("""
This dashboard analyses electric power transmission and distribution losses as a percentage of total electricity output.
It uses World Bank data to help users explore electricity loss trends across countries and years.
Higher electricity losses may indicate infrastructure inefficiency, while lower losses can suggest better energy efficiency.
""")

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_electricity_losses.csv")

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    meta = pd.read_csv("Metadata_Country_API_EG.ELC.LOSS.ZS_DS2_en_csv_v2_3166.csv")

    meta = meta[["Country Code", "Region"]]

    df = df.merge(meta, left_on="Country_Code", right_on="Country Code", how="left")

    # keep only actual countries
    df = df[df["Region"].notna()]

    df = df.drop(columns=["Country Code", "Region"])

    df = df.dropna(subset=["Country", "Country_Code", "Year", "Electricity_Loss_Percentage"])

    return df
    # keep only actual countries
    df = df[df["Region"].notna()]

    df = df.drop(columns=["Country Code", "Region"])

    df = df.dropna(subset=["Country", "Country_Code", "Year", "Electricity_Loss_Percentage"])

    return df

df = load_data()

st.sidebar.header("Dashboard Filters")

countries = sorted(df["Country"].unique())

selected_country = st.sidebar.selectbox(
    "Select a country",
    countries
)

min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

selected_year_range = st.sidebar.slider(
    "Select year range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

filtered_df = df[
    (df["Year"] >= selected_year_range[0]) &
    (df["Year"] <= selected_year_range[1])
]

country_df = filtered_df[filtered_df["Country"] == selected_country]

st.subheader("Dataset Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Countries", df["Country"].nunique())

with col2:
    st.metric("Year Range", f"{min_year} - {max_year}")

with col3:
    average_loss = filtered_df["Electricity_Loss_Percentage"].mean()
    st.metric("Average Electricity Loss", f"{average_loss:.2f}%")

st.subheader(f"Electricity Loss Trend for {selected_country}")

fig_line = px.line(
    country_df,
    x="Year",
    y="Electricity_Loss_Percentage",
    markers=True,
    title=f"Electricity Transmission and Distribution Losses in {selected_country}"
)

fig_line.update_layout(
    xaxis_title="Year",
    yaxis_title="Electricity Loss (%)"
)

st.plotly_chart(fig_line, use_container_width=True)

available_years = sorted(filtered_df["Year"].unique())

selected_year = st.selectbox(
    "Select a year for country comparison",
    available_years
)

year_df = filtered_df[filtered_df["Year"] == selected_year]

st.subheader(f"Top 10 Countries with Highest Electricity Losses in {selected_year}")

top_10 = year_df.sort_values(
    by="Electricity_Loss_Percentage",
    ascending=False
).head(10)

fig_top = px.bar(
    top_10,
    x="Electricity_Loss_Percentage",
    y="Country",
    orientation="h",
    title=f"Highest Electricity Losses in {selected_year}"
)

fig_top.update_layout(
    xaxis_title="Electricity Loss (%)",
    yaxis_title="Country"
)

st.plotly_chart(fig_top, use_container_width=True)

st.subheader(f"Top 10 Countries with Lowest Electricity Losses in {selected_year}")

bottom_10 = year_df.sort_values(
    by="Electricity_Loss_Percentage",
    ascending=True
).head(10)

fig_bottom = px.bar(
    bottom_10,
    x="Electricity_Loss_Percentage",
    y="Country",
    orientation="h",
    title=f"Lowest Electricity Losses in {selected_year}"
)

fig_bottom.update_layout(
    xaxis_title="Electricity Loss (%)",
    yaxis_title="Country"
)

st.plotly_chart(fig_bottom, use_container_width=True)

st.subheader("Key Insights")

st.write("""
- Electricity transmission and distribution losses vary significantly between countries.
- Countries with higher losses may indicate inefficiency in infrastructure or grid management.
- Countries with lower losses may have more efficient electricity distribution systems.
- Comparing trends over time helps identify whether electricity efficiency is improving or declining.
- Reducing electricity losses supports sustainability by reducing wasted energy and improving resource efficiency.
""")

st.subheader("Filtered Dataset")
st.dataframe(filtered_df)
