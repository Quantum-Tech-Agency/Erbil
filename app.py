import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title="Erbil Land Viewer", layout="wide")
st.title("🌍 Erbil Land Viewer")

# ---- Load data ----
uploaded_file = st.file_uploader("Upload your lands CSV", type=["csv"])

if uploaded_file is not None:
    lands_df = pd.read_csv(uploaded_file)
else:
    try:
        lands_df = pd.read_csv("lands.csv")
    except FileNotFoundError:
        st.error("No CSV file found! Please upload your lands CSV.")
        st.stop()

# ---- Category selector ----
land_types = lands_df['type'].unique().tolist()
selected_type = st.selectbox("Select land type to display:", land_types)

filtered_df = lands_df[lands_df['type'] == selected_type]

# ---- Map Section ----
st.subheader(f"Map of {selected_type.capitalize()} Lands")

# Center map on Erbil
m = folium.Map(location=[36.1911, 44.0091], zoom_start=12)

# Add MapTiler tiles
maptiler_key = "juDGsKHyHDg2rzVyrSi7"  # your key
folium.TileLayer(
    tiles=f"https://api.maptiler.com/maps/streets/{{z}}/{{x}}/{{y}}.png?key={maptiler_key}",
    attr='MapTiler',
    name='MapTiler Streets',
    overlay=True,
    control=True
).add_to(m)

# Marker colors
color_map = {
    'empty': 'red',
    'agri': 'green'
}
marker_color = color_map.get(selected_type, 'blue')

# Add markers
for _, row in filtered_df.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"<b>{row['name']}</b><br>"
              f"District: {row['district']}<br>"
              f"Area: {row['area']} m²",
        icon=folium.Icon(color=marker_color, icon='info-sign')
    ).add_to(m)

st_folium(m, width=900, height=500)

# ---- Charts Section ----
st.subheader(f"Statistics for {selected_type.capitalize()} Lands")

# Lands per district
if not filtered_df.empty:
    district_counts = filtered_df['district'].value_counts().reset_index()
    district_counts.columns = ['District', 'Number of Lands']
    fig1 = px.bar(district_counts, x='District', y='Number of Lands',
                  title=f'{selected_type.capitalize()} Lands per District')
    st.plotly_chart(fig1, use_container_width=True)

    # Area distribution
    if 'area' in filtered_df.columns:
        fig2 = px.histogram(filtered_df, x='area', nbins=10,
                            title=f'Distribution of {selected_type.capitalize()} Land Areas (m²)')
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No lands found for this category.")
