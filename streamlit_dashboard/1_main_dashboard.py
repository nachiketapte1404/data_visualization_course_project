import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd

st.set_page_config(
    page_title='Global Disaster Atlas',
    page_icon = './assets/icons/atlas_icon.png',
    layout='wide',
    initial_sidebar_state='collapsed'
)
st.title('Main Dashboard')

df = pd.read_csv('./assets/dataset/cleaned_data.csv')

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
fig_line = px.line(
    df,
    x='Start_Date',
    y="Total Damage, Adjusted ('000 US$)",  # Keep the original column name
    color='Disaster Subgroup',
    title="Total Damage Over Time by Disaster Subgroup",
    labels={
        "Total Damage, Adjusted ('000 US$)": "Total Damage (US$)",  # Modify y-axis label
        'Start_Date': 'Date'
    },
    line_shape='linear'  # Ensure smooth lines
)

# Update layout for better visibility
fig_line.update_layout(
    xaxis_title='Date',
    yaxis_title="Total Damage (US$)",  # Change y-axis title
    hovermode='x unified',  # Unified hover for all lines at the same x-axis point
    legend_title_text='Disaster Subgroup',
    template='plotly_white',  # Enhance the visual style
    height=600,  # Set the plot height
)

# Update hover and trace styles
fig_line.update_traces(
    mode='lines+markers',  # Display both lines and markers for better point visibility
    marker=dict(size=4),  # Set marker size
    hovertemplate='<b>Date</b>: %{x}<br><b>Total Damage</b>: %{y:.2f} (\'US$)<br><b>Disaster Subgroup</b>: %{fullData.name}'  # Retain detailed hover with '000 US$'
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
# Function to remove outliers using the IQR method
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

# List of specific disaster types
disaster_types = ['Earthquake', 'Flood', 'Storm']

# Extend the custom color palette to avoid white/light colors
extended_color_palette = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
    '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#393b79', '#637939',
    '#8c6d31', '#843c39', '#7b4173', '#5254a3', '#6b6ecf', '#9c9ede',
    '#8ca252', '#b5cf6b', '#cedb9c', '#bd9e39', '#e7ba52', '#e7969c',
    '#f28e2b', '#76b7b2', '#59a14f', '#edc948', '#4e79a7', '#9c755f',
    '#ff9da7', '#e15759', '#b07aa1', '#ffbb78', '#86bcb6', '#f1ce63'
]

# Loop through each specified disaster type and create a scatter plot for each
for disaster_type in disaster_types:
    # Convert necessary columns to numeric types
    df['Magnitude Scale'] = pd.to_numeric(df['Magnitude Scale'], errors='coerce')
    df['Total Deaths'] = pd.to_numeric(df['Total Deaths'], errors='coerce')
    df['Total Damage (\'000 US$)'] = pd.to_numeric(df['Total Damage (\'000 US$)'], errors='coerce')

    # Filter the dataframe for the current disaster type
    df_filtered = df[(df['Disaster Type'] == disaster_type) &
                    (df['Total Deaths'] > 0) & (df['Magnitude'] > 0)]

    # Remove outliers from Magnitude and Total Deaths
    df_filtered = remove_outliers(df_filtered, 'Magnitude')
    df_filtered = remove_outliers(df_filtered, 'Total Deaths')

    # Create the scatter plot for the specific disaster type
    fig_magnitude_deaths = px.scatter(
        df_filtered,
        x='Magnitude',
        y='Total Deaths',
        color='Country',  # Differentiate points by country
        size='Total Damage (\'000 US$)',
        title=f"Magnitude vs Total Deaths for {disaster_type} ((.) represent data not available for that country)",
        labels={'Magnitude Scale': 'Disaster Magnitude', 'Total Deaths': 'Total Deaths'},
        hover_data=['Country', 'Region'],
        color_discrete_sequence=extended_color_palette  # Use the extended custom dark color palette
    )

    # Add a narrow border to the markers
    fig_magnitude_deaths.update_traces(
        marker=dict(
            line=dict(
                width=0.5,  # Very narrow border
                color='black'  # Border color
            )
        )
    )

    # Update layout for better readability
    fig_magnitude_deaths.update_layout(
        xaxis_title='Disaster Magnitude',
        yaxis_title='Total Deaths',
        template='plotly_white',
        height=600,
    )

    # Show the plot for the current disaster type
    col1.plotly_chart(fig_magnitude_deaths)

## Heatmap

# Create a pivot table with counts of each Disaster Type per Subregion
df_pivot = df.groupby(['Subregion', 'Disaster Type']).size().unstack(fill_value=0)

# Calculate total counts for each subregion
subregion_counts = df_pivot.sum(axis=1)

# Set a threshold for minimum number of disasters
threshold = 15  # Adjust this value as needed

# Filter out subregions with total counts below the threshold
df_pivot_filtered = df_pivot.loc[subregion_counts[subregion_counts >= threshold].index]

# Calculate total counts for each disaster type after filtering subregions
total_counts = df_pivot_filtered.sum(axis=0)

# Filter out disaster types with counts below the threshold
df_pivot_filtered = df_pivot_filtered.loc[:, total_counts[total_counts > threshold].index]

# Create the heatmap with improved aesthetics
fig_heatmap = px.imshow(
    df_pivot_filtered,
    labels={'color': 'Disaster Count'},
    title='Disaster Frequency by Subregion and Type (Filtered)',
    color_continuous_scale='Viridis',
    text_auto=True  # Show the count on the heatmap
)

# Update layout for better appearance
fig_heatmap.update_layout(
    title_font_size=24,  # Title font size
    xaxis_title='Disaster Type',  # X-axis title
    yaxis_title='Subregion',  # Y-axis title
    xaxis_tickangle=-45,  # Angle x-axis ticks for better readability
    yaxis_autorange='reversed',  # Reverse the y-axis to have the first subregion at the top
    coloraxis_colorbar=dict(
        title='Disaster Count',  # Title for the color bar
        titlefont=dict(size=14),  # Color bar title font size
        tickfont=dict(size=12)  # Color bar tick font size
    ),
    width=1100,  # Increase width of the heatmap
    height=800   # Increase height of the heatmap
)

# Show the enhanced heatmap
st.plotly_chart(fig_heatmap)

