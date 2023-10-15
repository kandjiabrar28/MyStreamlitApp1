import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL=(
"MotorVehicleCollisions.csv"
)
st.title("Collisions de Véhicules à Moteur à New York ")
st.markdown("Cette application est un tableau de bord simplifié qui permet d'analyser les collisions de véhicules à moteur à New York")

@st.cache_data(persist=True)
def load_data(nrows):
    data=pd.read_csv(DATA_URL, nrows = nrows, parse_dates = [['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)

    return data

data = load_data(100000)
original_data=data

st.header("Où y a-t-il plus de blessés à New York?")
injured_people=st.slider("Nombre de personnes blessées dans des véhicules à moteur à New York", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))


st.header("Combien de collisions se produisent à un moment donné de la journée")
hour=st.slider("Heure à regarder", 0, 23)
data=data[data['date/time'].dt.hour == hour]

st.markdown("Collisions de vhicules entre %i:00 and %i:00" % (hour, (hour +1) % 24))

midpoint=(np.average(data['latitude']),np.average(data['longitude']))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude":midpoint[0],
        "longitude":midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time','latitude','longitude']],
            get_position=['longitude','latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0,1000],
        ),
    ],
))

st.subheader("Répartition par minutes entre %i:00 et %i:00" % (hour, (hour + 1) %24))
filtered=data[
    (data['date/time'].dt.hour >= hour)&(data['date/time'].dt.hour < (hour + 1))
]

hist=np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data=pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)

st.write(fig)  

st.header("Top 5 des rues les plus dangereuses par type concerné")
select=st.selectbox('type de personnes affectées',['Pedestrians','Cyclists','Motorists'])

if select=='Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name","injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])

elif select=='Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name","injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name","injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])

if st.checkbox("AFFICHER LES DONNEES BRUTES", False):
    st.subheader("DONNEES BRUTES")
    st.write(data)
