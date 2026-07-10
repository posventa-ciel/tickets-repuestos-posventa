import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Seguimiento Repuestos", layout="wide")
st.title("📦 Tablero de Seguimiento: Tickets de Repuestos")

# --- CARGA Y LIMPIEZA ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/14jP7-5vs_yuK5JqeTlPgF2lFT2eHI1RqQOSqG2_UZRw/export?format=csv&gid=0"

@st.cache_data(ttl=300) 
def cargar_datos():
    df = pd.read_csv(SHEET_URL)
    df['Fecha de creación'] = pd.to_datetime(df['Fecha de creación'], dayfirst=True, errors='coerce')
    df['Última actualización'] = pd.to_datetime(df['Última actualización'], dayfirst=True, errors='coerce')
    df['Año'] = df['Fecha de creación'].dt.year.fillna(2026).astype(int).astype(str)
    df['Días desde Creación'] = (pd.Timestamp.now() - df['Fecha de creación']).dt.days.fillna(0).astype(int)
    return df

try:
    df_full = cargar_datos()
    
    # Filtro de Año
    anios = ["TODOS"] + sorted(df_full['Año'].unique().tolist(), reverse=True)
    anio_sel = st.sidebar.selectbox("Filtrar por Año:", anios)
    
    df = df_full.copy()
    if anio_sel != "TODOS":
        df = df[df['Año'] == anio_sel]

    # --- LÓGICA DE SEMÁFORO (Emojis en texto para no consumir RAM) ---
    def obtener_semaforo(row):
        estado = str(row['Estado actual'])
        dias = row['Días desde Creación']
        if estado == "Pedido Completo": return "✅ Completo"
        if dias > 30: return "🔴 >30 días"
        if dias > 15: return "🟡 15-30 días"
        return "🟢 Normal"

    df['Semaforo'] = df.apply(obtener_semaforo, axis=1)

    # --- PESTAÑAS ---
    tab1, tab2 = st.tabs(["📋 General", "👔 Asesores"])

    with tab1:
        st.metric("Tickets Abiertos", len(df))
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("### Tickets por Asesor")
            fig1 = px.bar(df['De'].value_counts().reset_index(), x='De', y='count')
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            st.write("### Tickets por Estado")
            fig2 = px.bar(df['Estado actual'].value_counts().reset_index(), x='Estado actual', y='count')
            st.plotly_chart(fig2, use_container_width=True)

        st.write("### Detalle")
        st.dataframe(df, use_container_width=True)

    with tab2:
        asesor = st.selectbox("Elegí un Asesor:", sorted(df['De'].unique().tolist()))
        df_as = df[df['De'] == asesor]
        st.metric(f"Tickets de {asesor}", len(df_as))
        st.dataframe(df_as, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
