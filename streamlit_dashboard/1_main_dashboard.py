import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd

st.set_page_config(
    page_title='Global Disaster Atlas',
    page_icon = 'streamlit_dashboard/assets/icons/atlas_icon.png',
    layout='wide',
    initial_sidebar_state='collapsed'
)
st.title('Main Dashboard')

df = pd.read_csv('streamlit_dashboard/assets/dataset/cleaned_data.csv')

st.write(df.head())
st.write('# Chloropleth Map based on Disaster')

def create_map(filtered_df):
    fig = px.choropleth(
        filtered_df,
        locations="Country",
        locationmode='country names',
        color="Total Deaths",
        hover_name="Country",
        hover_data=['Total Affected', 'Total Damage (\'000 US$)'],
        color_continuous_scale=px.colors.sequential.OrRd,
        range_color=(0, 100),
        title="Global Disaster Impact by Country"
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="Black",
        showcoastlines=True,
        coastlinecolor="Black",
        showland=True,
        landcolor="lightgray",
        projection_type="equirectangular"
    )

    return fig

# Function to update the figure when a different disaster type is selected
def update_map(disaster_type):
    filtered_df = df[df['Disaster Type'] == disaster_type]
    return create_map(filtered_df)

# Create initial map for the default disaster type
initial_disaster_type = 'Flood'
fig = update_map(initial_disaster_type)

# Create a dropdown menu to filter by disaster type
disaster_types = df['Disaster Type'].unique()

# Adding dropdown filter for Disaster Type
fig.update_layout(
    updatemenus=[{
        'buttons': [
            {
                'label': disaster_type,
                'method': 'restyle',
                'args': [{'z': [df[df['Disaster Type'] == disaster_type]['Total Deaths']]},
                         {'title': f"Global {disaster_type} Disaster Impact"}]
            } for disaster_type in disaster_types
        ],
        'direction': 'down',
        'showactive': True,
        'x': 0.5,  # Centering the dropdown horizontally
        'xanchor': "center",
        'y': 1.1,  # Move dropdown above the title
        'yanchor': "top"
    }],
    title_x=0.5,  # Center the title
    margin={"t": 100, "b": 50},  # Adjust the top and bottom margins to create a better gap
)

# Display the updated figure
st.plotly_chart(fig)

col1,col2 = st.columns(2)
df["Total Damage, Adjusted ('000 US$)"] = pd.to_numeric(df["Total Damage, Adjusted ('000 US$)"], errors='coerce')

df["Total Damage, Adjusted ('000 US$)"].fillna(0, inplace=True)

# Line Chart: Total Damage, Adjusted over Time by Disaster Subgroup with hover functionality and improved layout
fig_line = px.line(
    df,
    x='Start_Date',
    y="Total Damage, Adjusted ('000 US$)",
    color='Disaster Subgroup',
    title="Total Damage Over Time by Disaster Subgroup",
    labels={
        "Total Damage, Adjusted ('000 US$)": "Total Damage, Adjusted ('000 US$)",
        'Start_Date': 'Date'
    },
    line_shape='linear'  # Change to 'linear' to avoid jagged lines
)

# Update layout for better visibility
fig_line.update_layout(
    xaxis_title='Date',
    yaxis_title="Total Damage, Adjusted ('000 US$)",
    hovermode='x unified',  # Show hover details for all lines at the same x-axis point
    legend_title_text='Disaster Subgroup',
    template='plotly_white',  # Improve visual appearance
    height=600,  # Increase plot height
)

# Improve hover and trace visibility
fig_line.update_traces(
    mode='lines+markers',  # Show lines with markers to improve point visibility
    marker=dict(size=4),  # Increase marker size
    hovertemplate='<b>Date</b>: %{x}<br><b>Total Damage</b>: %{y:.2f} (\'000 US$)<br><b>Disaster Subgroup</b>: %{fullData.name}'
)

# Show the plot
col1.plotly_chart(fig_line)
df['Start_Date'] = pd.to_datetime(df['Start_Date'])
df_sorted = df.sort_values(by='Start_Date')

# Cumulative sum of Total Deaths by Region
df_sorted['Cumulative_Deaths'] = df_sorted.groupby('Region')['Total Deaths'].cumsum()

# Cumulative Line Chart: Total Deaths by Region Over Time with improved styling
fig_cumulative_deaths = px.line(
    df_sorted,
    x='Start_Date',
    y='Cumulative_Deaths',
    color='Region',
    title="Cumulative Total Deaths by Region Over Time",
    labels={'Cumulative_Deaths': 'Cumulative Total Deaths', 'Start_Date': 'Date'},
    hover_data=['Disaster Type', 'Country'],  # Show additional data on hover
    line_shape='linear'  # Change to 'linear' to avoid jagged lines
)

# Update layout for better visibility
fig_cumulative_deaths.update_layout(
    xaxis_title='Date',
    yaxis_title='Cumulative Total Deaths',
    hovermode='x unified',  # Show hover details for all lines at the same x-axis point
    legend_title_text='Region',
    template='plotly_white',  # Improve visual appearance with white background
    height=600,  # Increase plot height
)

# Improve hover and trace visibility
fig_cumulative_deaths.update_traces(
    mode='lines+markers',  # Show lines with markers to improve point visibility
    marker=dict(size=4),  # Increase marker size for better readability
    hovertemplate='<b>Date</b>: %{x}<br><b>Cumulative Deaths</b>: %{y}<br><b>Region</b>: %{fullData.name}<br><b>Disaster Type</b>: %{customdata[0]}<br><b>Country</b>: %{customdata[1]}'  # Custom hover data
)

# Show the plot
col2.plotly_chart(fig_cumulative_deaths)

all_countries = df['Country'].unique()

# Create the dynamic bar chart
fig_bar = px.bar(
    df,
    x='Disaster Type',
    y='Total Deaths',
    color='Country',
    title="Total Deaths by Disaster Type and Country",
    labels={'Total Deaths': 'Total Deaths', 'Disaster Type': 'Disaster Type'},
    category_orders={'Country': all_countries}  # Ensure all countries appear in the filter
)

col1.plotly_chart(fig_bar)
# Scatter Plot: Total Deaths vs. Total Damage (Adjusted) by Disaster Subgroup
fig_scatter = px.scatter(
    df,
    x="Total Damage, Adjusted ('000 US$)",
    y='Total Deaths',
    color='Disaster Subgroup',
    size='Total Deaths',  # Bubble size based on Total Deaths
    hover_data=['Country', 'Disaster Type'],  # Add more details to the hover tooltip
    title="Scatter Plot: Total Deaths vs. Total Damage by Disaster Subgroup",
    labels={
        "Total Damage, Adjusted ('000 US$)": "Total Damage, Adjusted ('000 US$)",
        "Total Deaths": "Total Deaths"
    },
    template='plotly_white'
)

# Improve layout
fig_scatter.update_layout(
    xaxis_title="Total Damage, Adjusted ('000 US$)",
    yaxis_title="Total Deaths",
    height=600,
    legend_title="Disaster Subgroup"
)

# Display the initial scatter plot
col2.plotly_chart(fig_scatter)
