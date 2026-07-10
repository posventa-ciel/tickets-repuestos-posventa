import streamlit as st
import pandas as pd
import plotly.express as px

st.set_config(layout="wide")
st.title("📦 Tablero de Gestión de Repuestos")

# --- CARGA Y LIMPIEZA ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/14jP7-5vs_yuK5JqeTlPgF2lFT2eHI1RqQOSqG2_UZRw/export?format=csv&gid=0"

@st.cache_data(ttl=300) 
def cargar_datos():
    df = pd.read_csv(SHEET_URL)
    df['Fecha de creación'] = pd.to_datetime(df['Fecha de creación'], dayfirst=True, errors='coerce')
    hoy = pd.Timestamp.now()
    df['Días desde Creación'] = (hoy - df['Fecha de creación']).dt.days.fillna(0).astype(int)
    df['Año'] = df['Fecha de creación'].dt.year.fillna(2026).astype(int).astype(str)
    return df

df_full = cargar_datos()

# Sidebar: Filtros Globales
st.sidebar.header("Filtros Globales")
anios = ["TODOS"] + sorted(df_full['Año'].unique().tolist(), reverse=True)
anio_sel = st.sidebar.selectbox("Año:", anios)
df = df_full[df_full['Año'] == anio_sel].copy() if anio_sel != "TODOS" else df_full.copy()

tab_resumen, tab_asesores = st.tabs(["📋 Resumen General", "👔 Gestión por Asesor"])

with tab_resumen:
    # 1. Tarjetas de Métricas (KPIs)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tickets", len(df))
    c2.metric("Tickets > 30 días", len(df[df['Días desde Creación'] > 30]))
    c3.metric("Promedio Demora", f"{round(df['Días desde Creación'].mean(), 1)} días")
    c4.metric("Más Antiguo", f"{df['Días desde Creación'].max()} días")
    
    st.divider()
    
    # 2. Gráficos Generales
    g1, g2 = st.columns(2)
    with g1:
        st.write("### Tickets por Estado")
        fig1 = px.pie(df, names='Estado actual', title="Distribución por Estado")
        st.plotly_chart(fig1, use_container_width=True)
    with g2:
        st.write("### Tickets por Asesor")
        fig2 = px.bar(df['De'].value_counts().reset_index(), x='De', y='count', color='De')
        st.plotly_chart(fig2, use_container_width=True)

    st.write("### Tabla Detallada")
    st.dataframe(df, use_container_width=True)

with tab_asesores:
    asesores = sorted(df['De'].dropna().unique().tolist())
    asesor_sel = st.selectbox("Seleccionar Asesor:", asesores)
    
    df_as = df[df['De'] == asesor_sel].copy()
    
    def status_label(dias):
        if dias <= 30: return "🟢 < 30 días"
        if dias <= 60: return "🟡 31-60 días"
        if dias <= 120: return "🟠 61-120 días"
        return "🔴 +120 días"

    df_as['Antigüedad'] = df_as['Días desde Creación'].apply(status_label)
    orden = ["🟢 < 30 días", "🟡 31-60 días", "🟠 61-120 días", "🔴 +120 días"]

    for estado in df_as['Estado actual'].unique():
        st.subheader(f"Estado: {estado}")
        df_estado = df_as[df_as['Estado actual'] == estado]
        
        c1, c2 = st.columns([3, 1])
        with c1:
            st.dataframe(df_estado.drop(columns=['Año']), use_container_width=True, hide_index=True)
        with c2:
            dist = df_estado['Antigüedad'].value_counts().reindex(orden, fill_value=0).reset_index()
            fig = px.bar(dist, x='count', y='Antigüedad', orientation='h', title="Antigüedad", height=250, category_orders={"Antigüedad": orden})
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)
        st.divider()
