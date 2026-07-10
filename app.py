import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("👨‍🔧 Panel de Control: Gestión de Asesores")

SHEET_URL = "https://docs.google.com/spreadsheets/d/14jP7-5vs_yuK5JqeTlPgF2lFT2eHI1RqQOSqG2_UZRw/export?format=csv&gid=0"

@st.cache_data(ttl=300) 
def cargar_datos():
    df = pd.read_csv(SHEET_URL)
    df['Fecha de creación'] = pd.to_datetime(df['Fecha de creación'], dayfirst=True, errors='coerce')
    hoy = pd.Timestamp.now()
    df['Días desde Creación'] = (hoy - df['Fecha de creación']).dt.days.fillna(0).astype(int)
    return df

df = cargar_datos()

# Selector de Asesor
asesores = sorted(df['De'].dropna().unique().tolist())
asesor_sel = st.selectbox("Seleccionar Asesor para auditoría:", asesores)

if asesor_sel:
    df_as = df[df['De'] == asesor_sel].copy()
    
    # Lógica de Semáforo para la tabla (sin colores pesados)
    def status_label(dias):
        if dias <= 30: return "🟢 < 30 días"
        if dias <= 60: return "🟡 31-60 días"
        if dias <= 120: return "🟠 61-120 días"
        return "🔴 +120 días"

    df_as['Antigüedad'] = df_as['Días desde Creación'].apply(status_label)
    
    # Reordenar columnas para poner lo importante al principio
    cols = ['Días desde Creación', 'Antigüedad', 'Estado actual', 'Número de Ticket', 'Asunto', 'Fecha de creación']
    df_as = df_as[cols + [c for c in df_as.columns if c not in cols]]

    # Paneles por Estado
    estados = df_as['Estado actual'].unique()
    
    for estado in estados:
        st.subheader(f"Estado: {estado}")
        df_estado = df_as[df_as['Estado actual'] == estado]
        
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.dataframe(df_estado, use_container_width=True, hide_index=True)
            
        with c2:
            # Gráfico de barras de antigüedad para este estado
            distribucion = df_estado['Antigüedad'].value_counts().reset_index()
            fig = px.bar(distribucion, x='count', y='Antigüedad', orientation='h', 
                         title=f"Distribución de días en {estado}",
                         color_discrete_sequence=['#636EFA'])
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
