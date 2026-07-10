import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📦 Tickets de Repuestos")

SHEET_URL = "https://docs.google.com/spreadsheets/d/14jP7-5vs_yuK5JqeTlPgF2lFT2eHI1RqQOSqG2_UZRw/export?format=csv&gid=0"

@st.cache_data(ttl=300) 
def cargar():
    # Forzamos a leer como csv simple
    return pd.read_csv(SHEET_URL)

try:
    df = cargar()
    # Limpieza básica
    df['Fecha de creación'] = pd.to_datetime(df['Fecha de creación'], errors='coerce')
    df['Año'] = df['Fecha de creación'].dt.year.fillna(2026).astype(int).astype(str)
    
    anio_sel = st.selectbox("Seleccionar Año:", ["TODOS"] + sorted(df['Año'].unique().tolist(), reverse=True))

    if anio_sel != "TODOS":
        df = df[df['Año'] == anio_sel]

    st.dataframe(df) # <-- Quitamos todos los parámetros de ancho para que no falle

except Exception as e:
    st.error(f"Error: {e}")
