import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(
    page_title='Static Graphs',
    page_icon = 'streamlit_dashboard/assets/icons/earthquake.png'
)


st.title('Static Graphs')
st.write('This page provides all the static graphs')

df = pd.read_csv('streamlit_dashboard/assets/dataset/cleaned_data.csv')

plt.figure(figsize=(12, 6))
sns.countplot(y='Disaster Type', data=df, order=df['Disaster Type'].value_counts().index)
plt.title('Frequency of Each Disaster Type')
plt.xlabel('Count')
plt.ylabel('Disaster Type')
plt.xscale('log')  # Use a logarithmic scale
st.pyplot(plt)

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Sample DataFrame creation (if needed)
# Assuming `impact_by_region` is your DataFrame from previous steps
# impact_by_region = pd.DataFrame(...)

# Normalize the impact data by region
normalized_impact = impact_by_region.div(impact_by_region.sum(axis=1), axis=0)

# Create a stacked bar plot
ax = normalized_impact.plot(kind='barh', stacked=True, figsize=(14, 8), colormap='viridis')

# Customize the plot
plt.title('Normalized Total Affected by Disaster Type and Region (Stacked Bar Chart)')
plt.xlabel('Percentage of Total Affected')
plt.ylabel('Region')

# Add legend and adjust layout
plt.legend(title='Disaster Type', bbox_to_anchor=(1.05, 1), loc='upper left')
st.pyplot(plt)