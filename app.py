import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Seguimiento", layout="wide")
st.title("📦 Tickets de Repuestos")

SHEET_URL = "https://docs.google.com/spreadsheets/d/14jP7-5vs_yuK5JqeTlPgF2lFT2eHI1RqQOSqG2_UZRw/export?format=csv&gid=0"

@st.cache_data(ttl=300) 
def cargar():
    df = pd.read_csv(SHEET_URL)
    # Convertimos fecha y año
    df['Fecha de creación'] = pd.to_datetime(df['Fecha de creación'], dayfirst=True, errors='coerce')
    df['Año'] = df['Fecha de creación'].dt.year.fillna(2026).astype(int).astype(str)
    # Limpiamos nombres de asesores
    df['De'] = df['De'].fillna('SIN IDENTIFICAR').str.strip().str.upper()
    return df

df_completo = cargar()
lista_anios = sorted(df_completo['Año'].unique().tolist(), reverse=True)
anio_sel = st.selectbox("Seleccionar Año:", ["TODOS"] + lista_anios)

if anio_sel != "TODOS":
    df = df_completo[df_completo['Año'] == anio_sel].copy()
else:
    df = df_completo.copy()

tab1, tab2 = st.tabs(["📋 Resumen General", "👔 Asesores"])

with tab1:
    st.metric("Total Tickets", len(df))
    # Cambiamos width="stretch" por use_container_width=True que es lo compatible con esta versión
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Selección de Asesor")
    # Filtramos la lista de asesores para que sea dinámica según el año seleccionado
    asesores_disponibles = sorted(df['De'].unique().tolist())
    asesor_sel = st.selectbox("Elegí un asesor:", ["TODOS"] + asesores_disponibles)
    
    if asesor_sel != "TODOS":
        df_asesor = df[df['De'] == asesor_sel]
        st.write(f"Tickets de {asesor_sel}: {len(df_asesor)}")
        st.dataframe(df_asesor, use_container_width=True)
    else:
        st.write("Seleccioná un asesor para ver sus tickets.")
        st.dataframe(df, use_container_width=True)
