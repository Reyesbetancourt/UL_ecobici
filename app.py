import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Ecobici CDMX",
    layout="wide"
)

@st.cache_data(ttl=60)
def obtener_datos_ecobici():
    url_info = "https://gbfs.mex.lyftbikes.com/gbfs/en/station_information.json"
    url_status = "https://gbfs.mex.lyftbikes.com/gbfs/en/station_status.json"

    resp_info = requests.get(url_info, timeout=10)
    resp_status = requests.get(url_status, timeout=10)

    resp_info.raise_for_status()
    resp_status.raise_for_status()

    df_info = pd.DataFrame(resp_info.json()["data"]["stations"])
    df_status = pd.DataFrame(resp_status.json()["data"]["stations"])

    tabla_final = pd.merge(
        df_info[["station_id", "name", "lat", "lon", "capacity"]],
        df_status[[
            "station_id",
            "num_bikes_available",
            "num_docks_available",
            "is_renting"
        ]],
        on="station_id",
        how="inner"
    )

    tabla_final.columns = [
        "ID",
        "Nombre",
        "Latitud",
        "Longitud",
        "Capacidad_Total",
        "Bicis_Disponibles",
        "Puertos_Libres",
        "Operativa"
    ]

    tabla_final["Operativa"] = tabla_final["Operativa"].map({
        1: "SÍ",
        0: "NO"
    })

    return tabla_final


st.title("🚲 Dashboard Ecobici CDMX")

try:
    df_ecobici = obtener_datos_ecobici()

    st.subheader("Resumen general")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Estaciones", len(df_ecobici))
    col2.metric("Bicis disponibles", int(df_ecobici["Bicis_Disponibles"].sum()))
    col3.metric("Puertos libres", int(df_ecobici["Puertos_Libres"].sum()))
    col4.metric(
        "Estaciones operativas",
        int((df_ecobici["Operativa"] == "SÍ").sum())
    )

    st.subheader("Tabla de estaciones")
    st.dataframe(df_ecobici, use_container_width=True)

    st.subheader("Mapa de estaciones")

    fig = px.scatter_mapbox(
        df_ecobici,
        lat="Latitud",
        lon="Longitud",
        zoom=10,
        mapbox_style="carto-positron",
        hover_name="Nombre",
        hover_data={
            "Capacidad_Total": True,
            "Bicis_Disponibles": True,
            "Puertos_Libres": True,
            "Operativa": True,
            "Latitud": False,
            "Longitud": False
        },
        color="Operativa",
        size="Bicis_Disponibles",
        title="Mapa de Estaciones Ecobici en la Ciudad de México"
    )

    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        title_x=0.5,
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
