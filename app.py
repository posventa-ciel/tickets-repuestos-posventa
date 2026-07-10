import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Posventa - Repuestos", layout="wide")

# (Aquí iría todo tu CSS actual que ya tenés definido en tu código base)
st.markdown("""<style>
    .kpi-card { background-color: white; border: 1px solid #e0e0e0; padding: 12px 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 8px; min-height: 120px; display: flex; flex-direction: column; justify-content: space-between; }
    .kpi-card p { font-size: 0.85rem; margin: 0; color: #666; font-weight: 600; }
    .kpi-card h2 { font-size: 1.8rem; margin: 4px 0; color: #00235d; }
</style>""", unsafe_allow_html=True)

# --- CARGA DATOS ---
@st.cache_data(ttl=300) 
def cargar_datos():
    url = "https://docs.google.com/spreadsheets/d/14jP7-5vs_yuK5JqeTlPgF2lFT2eHI1RqQOSqG2_UZRw/export?format=csv&gid=0"
    df = pd.read_csv(url)
    df['Fecha de creación'] = pd.to_datetime(df['Fecha de creación'], dayfirst=True, errors='coerce')
    df['Días desde Creación'] = (pd.Timestamp.now() - df['Fecha de creación']).dt.days.fillna(0).astype(int)
    return df

df = cargar_datos()

# --- PESTAÑAS ---
tab_resumen, tab_asesores = st.tabs(["📋 Resumen General", "👔 Gestión por Asesor"])

with tab_resumen:
    st.title("📦 Resumen General de Repuestos")
    # Tarjetas KPI
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="kpi-card"><p>Total Tickets Activos</p><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><p>Promedio Demora</p><h2>{round(df["Días desde Creación"].mean(), 1)} días</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><p>Tickets > 30 días</p><h2>{len(df[df["Días desde Creación"] > 30])}</h2></div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

with tab_asesores:
    st.title("👔 Gestión por Asesor")
    asesores = sorted(df['De'].dropna().unique().tolist())
    asesor_sel = st.selectbox("Seleccionar Asesor:", asesores)
    
    df_as = df[df['De'] == asesor_sel].copy()
    
    # 1. Resumen inicial del asesor
    k1, k2, k3 = st.columns(3)
    k1.markdown(f'<div class="kpi-card"><p>Tickets Totales</p><h2>{len(df_as)}</h2></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><p>Completos</p><h2>{len(df_as[df_as["Estado actual"] == "Pedido Completo"])}</h2></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card"><p>Antigüedad Máxima</p><h2>{df_as["Días desde Creación"].max()} días</h2></div>', unsafe_allow_html=True)
    
    st.divider()
    
    # 2. Detalle con semáforo y gráfico
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
            st.dataframe(df_estado, use_container_width=True, hide_index=True)
        with c2:
            dist = df_estado['Antigüedad'].value_counts().reindex(orden, fill_value=0).reset_index()
            fig = px.bar(dist, x='count', y='Antigüedad', orientation='h', title="Antigüedad", height=200, category_orders={"Antigüedad": orden})
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)
        st.divider()
