import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Posventa - Pro", layout="wide")

# CSS Profesional
st.markdown("""<style>
    .kpi-card { background-color: white; border: 1px solid #e0e0e0; padding: 12px 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 8px; }
    .kpi-card p { font-size: 0.8rem; margin: 0; color: #666; font-weight: 600; }
    .kpi-card h2 { font-size: 1.6rem; margin: 4px 0; color: #00235d; }
</style>""", unsafe_allow_html=True)

# --- CARGA DATOS ---
@st.cache_data(ttl=300)
def cargar_datos():
    url = "https://docs.google.com/spreadsheets/d/14jP7-5vs_yuK5JqeTlPgF2lFT2eHI1RqQOSqG2_UZRw/export?format=csv&gid=0"
    df = pd.read_csv(url)
    df['Fecha de creación'] = pd.to_datetime(df['Fecha de creación'], dayfirst=True, errors='coerce')
    df['Año'] = df['Fecha de creación'].dt.year
    df['Días desde Creación'] = (pd.Timestamp.now() - df['Fecha de creación']).dt.days.fillna(0).astype(int)
    return df

df = cargar_datos()

# --- PESTAÑAS ---
tab_resumen, tab_asesores = st.tabs(["📋 Resumen General", "👔 Gestión por Asesor"])

with tab_resumen:
    st.title("📊 Dashboard Ejecutivo")
    
    # Filtro Año
    años = sorted(df['Año'].dropna().unique().astype(int).tolist())
    año_sel = st.multiselect("Filtrar por año:", años, default=años[-1:])
    df_filtrado = df[df['Año'].isin(año_sel)]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="kpi-card"><p>Total Tickets</p><h2>{len(df_filtrado)}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><p>Promedio Días</p><h2>{round(df_filtrado["Días desde Creación"].mean(), 1)}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><p>Tickets > 30 días</p><h2>{len(df_filtrado[df_filtrado["Días desde Creación"] > 30])}</h2></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card"><p>Completados</p><h2>{len(df_filtrado[df_filtrado["Estado actual"] == "Pedido Completo"])}</h2></div>', unsafe_allow_html=True)

    # Gráficos
    g1, g2 = st.columns(2)
    with g1:
        fig_estado = px.pie(df_filtrado, names='Estado actual', title="Distribución por Estado")
        st.plotly_chart(fig_estado, use_container_width=True)
    with g2:
        fig_evol = px.histogram(df_filtrado, x='Fecha de creación', title="Volumen de Ingreso de Tickets")
        st.plotly_chart(fig_evol, use_container_width=True)

with tab_asesores:
    st.title("👔 Análisis de Asesores")
    asesores = sorted(df['De'].dropna().unique().tolist())
    asesor_sel = st.selectbox("Seleccionar Asesor:", asesores)
    
    # Filtro año aplicado también al asesor
    df_as = df[(df['De'] == asesor_sel) & (df['Año'].isin(año_sel))].copy()
    
    # Tarjetas del asesor
    k1, k2, k3 = st.columns(3)
    k1.markdown(f'<div class="kpi-card"><p>Tickets Asignados</p><h2>{len(df_as)}</h2></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><p>Eficiencia (Completos)</p><h2>{len(df_as[df_as["Estado actual"] == "Pedido Completo"])}</h2></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card"><p>Antigüedad Max</p><h2>{df_as["Días desde Creación"].max()} días</h2></div>', unsafe_allow_html=True)
    
    # Gráfico de barras específico del asesor
    fig_as = px.bar(df_as, x='Estado actual', title=f"Tickets de {asesor_sel} por Estado")
    st.plotly_chart(fig_as, use_container_width=True)
    
    st.dataframe(df_as, use_container_width=True)
