import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Seguimiento", layout="wide")
st.title("📦 Tickets de Repuestos")

SHEET_URL = "https://docs.google.com/spreadsheets/d/14jP7-5vs_yuK5JqeTlPgF2lFT2eHI1RqQOSqG2_UZRw/export?format=csv&gid=0"

@st.cache_data(ttl=300) 
def cargar():
    df = pd.read_csv(SHEET_URL)
    df['Fecha de creación'] = pd.to_datetime(df['Fecha de creación'], dayfirst=True, errors='coerce')
    df['Año'] = df['Fecha de creación'].dt.year.fillna(2026).astype(int).astype(str)
    return df

df_completo = cargar()
lista_anios = sorted(df_completo['Año'].unique().tolist(), reverse=True)
anio_sel = st.selectbox("Año:", ["TODOS"] + lista_anios)

if anio_sel != "TODOS":
    df = df_completo[df_completo['Año'] == anio_sel].copy()
else:
    df = df_completo.copy()

st.metric("Total Tickets", len(df))

# Tabla simple, sin colores complejos para evitar el crash
st.dataframe(df, use_container_width=True)
