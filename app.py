import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Seguimiento de Tickets - Repuestos", layout="wide")

# --- ESTILOS CSS INYECTADOS (Estilo unificado con tu app de Chapa) ---
st.markdown("""<style>
    .metric-card { 
        background-color: white; 
        border: 1px solid #dee2e6; 
        padding: 15px; 
        border-radius: 8px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        text-align: center; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        min-height: 110px; 
        margin-bottom: 15px;
    }
    .metric-title { color: #666; font-size: 0.85rem; font-weight: 600; margin-bottom: 5px; text-transform: uppercase; }
    .metric-value-number { color: #00235d; font-size: 1.8rem; font-weight: bold; margin: 0; }
    .metric-subtitle-red { color: #dc3545; font-size: 0.95rem; font-weight: bold; margin-top: 5px; }
    .metric-subtitle-green { color: #28a745; font-size: 0.95rem; font-weight: bold; margin-top: 5px; }
    .metric-subtitle-blue { color: #17a2b8; font-size: 0.95rem; font-weight: bold; margin-top: 5px; }
</style>""", unsafe_allow_html=True)

st.title("📦 Tablero Avanzado: Tickets de Repuestos")
st.markdown("Plataforma de visualización, trazabilidad y control de SLAs.")
st.divider()

# --- CARGA Y LIMPIEZA DE DATOS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/14jP7-5vs_yuK5JqeTlPgF2lFT2eHI1RqQOSqG2_UZRw/export?format=csv&gid=0"

@st.cache_data(ttl=300) 
def cargar_y_limpiar_datos():
    df = pd.read_csv(SHEET_URL)
    
    # Parseo estricto de fechas (Formato de osTicket)
    df['Fecha de creación'] = pd.to_datetime(df['Fecha de creación'], format='%d/%m/%Y %H:%M', errors='coerce')
    df['Última actualización'] = pd.to_datetime(df['Última actualización'], format='%d/%m/%Y %H:%M', errors='coerce')
    
    hoy = pd.Timestamp.now()
    
    # Extraer el Año para el análisis temporal que pediste
    df['Año'] = df['Fecha de creación'].dt.year.fillna(hoy.year).astype(int).astype(str)
    
    # Cálculos de envejecimiento y SLAs
    df['Días desde Creación'] = (hoy - df['Fecha de creación']).dt.days.fillna(0).astype(int)
    df['Días en Estado Actual'] = (hoy - df['Última actualización']).dt.days.fillna(0).astype(int)
    
    # Limpieza de nombres de asesores para evitar duplicados por espacios
    df['De'] = df['De'].fillna('SIN IDENTIFICAR').str.strip().str.upper()
    df['Estado actual'] = df['Estado actual'].fillna('SIN ESTADO').str.strip()
    
    return df

try:
    df = cargar_y_limpiar_datos()
except Exception as e:
    st.error(f"Error procesando el Google Sheet: {e}")
    st.stop()

# --- DEFINICIÓN DE PESTAÑAS (TABS) ---
tab_general, tab_asesores = st.tabs(["📋 Control General y Alertas", "Asesores en Detalle"])

# ==========================================
# PESTAÑA 1: CONTROL GENERAL Y ALERTAS
# ==========================================
with tab_general:
    
    # KPIs con diseño Metric Card de Chapa
    mas_15_dias_sin_llegar = df[(df["Estado actual"] != "Pedido Completo") & (df["Días desde Creación"] > 15)]
    mas_30_dias_global = df[df["Días desde Creación"] > 30]
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="metric-card"><div class="metric-title">Total Abiertos</div><div class="metric-value-number">{len(df)}</div><div class="metric-subtitle-blue">En proceso activo</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card" style="border-left: 5px solid #dc3545;"><div class="metric-title">🚨 Alerta Repuestos</div><div class="metric-value-number" style="color:#dc3545;">{len(mas_15_dias_sin_llegar)}</div><div class="metric-subtitle-red">> 15 días sin ser "Completo"</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card" style="border-left: 5px solid #ffc107;"><div class="metric-title">⚠️ Alerta Taller / Global</div><div class="metric-value-number" style="color:#856404;">{len(mas_30_dias_global)}</div><div class="metric-subtitle-green">> 30 días totales de vida</div></div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Sección de Gráficos de la Pestaña General
    cg1, cg2 = st.columns(2)
    
    with cg1:
        st.markdown("#### 📅 Historial: Tickets Abiertos por Año de Creación")
        df_anio = df['Año'].value_counts().reset_index()
        df_anio.columns = ['Año', 'Tickets']
        df_anio = df_anio.sort_values(by='Año')
        
        fig_anio = px.bar(df_anio, x='Año', y='Tickets', text_auto=True,
                          color_discrete_sequence=['#00235d'], template="plotly_white")
        fig_anio.update_layout(xaxis_title="Año de Apertura", yaxis_title="Cantidad", margin=dict(t=10, b=10))
        st.plotly_chart(fig_anio, use_container_width=True)
        
    with cg2:
        st.markdown("#### 📊 Estado de la Carga de Trabajo Global")
        df_estado = df['Estado actual'].value_counts().reset_index()
        df_estado.columns = ['Estado', 'Tickets']
        
        fig_estado = px.bar(df_estado, x='Tickets', y='Estado', orientation='h', text_auto=True,
                             color_discrete_sequence=['#17a2b8'], template="plotly_white")
        fig_estado.update_layout(xaxis_title="Cantidad de Tickets", yaxis_title="", margin=dict(t=10, b=10))
        st.plotly_chart(fig_estado, use_container_width=True)
        
    st.divider()
    
    # Tabla General de Semáforos
    st.markdown("#### 🚥 Monitor de Tickets Activos y Semáforo de Tiempos")
    
    def aplicar_semaforo(row):
        estado = row['Estado actual']
        dias_creacion = row['Días desde Creación']
        dias_estado = row['Días en Estado Actual']
        
        if estado == "Pedido Completo":
            if dias_estado <= 15: return ['background-color: #c3f9c3; color: black'] * len(row)
            elif 15 < dias_estado <= 30: return ['background-color: #fcf9a8; color: black'] * len(row)
            else: return ['background-color: #f9c3c3; color: black'] * len(row)
        else:
            if dias_creacion > 15: return ['background-color: #ff9999; color: black; font-weight: bold'] * len(row)
            else: return [''] * len(row)

    # Quitamos columnas secundarias para visualización compacta
    df_visible = df.drop(columns=['Año'], errors='ignore')
    st.dataframe(df_visible.style.apply(aplicar_semaforo, axis=1), use_container_width=True, hide_index=True)

# ==========================================
# PESTAÑA 2: ASESORES EN DETALLE
# ==========================================
with tab_asesores:
    st.markdown("### 👔 Análisis de Trazabilidad por Asesor")
    
    # Selector de Asesor dinámico
    lista_asesores = sorted(df['De'].unique().tolist())
    asesor_sel = st.selectbox("Seleccionar un Asesor para ver su radiografía:", ["VER GRÁFICO COMPARATIVO"] + lista_asesores)
    
    st.divider()
    
    if asesor_sel == "VER GRÁFICO COMPARATIVO":
        st.markdown("#### Comparativa Global: Cantidad de Tickets por Asesor")
        df_ranking = df['De'].value_counts().reset_index()
        df_ranking.columns = ['Asesor', 'Tickets Abiertos']
        
        fig_rank = px.bar(df_ranking, x='Asesor', y='Tickets Abiertos', text_auto=True,
                           color_discrete_sequence=['#28a745'], template="plotly_white")
        fig_rank.update_layout(xaxis_tickangle=-45, xaxis_title="", yaxis_title="Tickets")
        st.plotly_chart(fig_rank, use_container_width=True)
        
        st.markdown("#### ⏳ Los 5 Tickets más antiguos del Taller (Urgentes de destrabar)")
        top_atrasados = df.sort_values(by='Días desde Creación', ascending=False).head(5)
        st.dataframe(top_atrasados[['Número de Ticket', 'Fecha de creación', 'De', 'Estado actual', 'Días desde Creación', 'Asunto']], 
                     use_container_width=True, hide_index=True)
        
    else:
        # Filtrado de datos exclusivo para el asesor seleccionado
        df_as = df[df['De'] == asesor_sel]
        
        # Tarjetas de rendimiento individuales del Asesor
        ca1, ca2, ca3, ca4 = st.columns(4)
        
        cant_tickets_as = len(df_as)
        prom_demora_as = df_as['Días desde Creación'].mean()
        max_demora_as = df_as['Días desde Creación'].max()
        criticos_as = len(df_as[df_as['Días desde Creación'] > 30])
        
        ca1.markdown(f'<div class="metric-card"><div class="metric-title">Tickets Pendientes</div><div class="metric-value-number">{cant_tickets_as}</div></div>', unsafe_allow_html=True)
        ca2.markdown(f'<div class="metric-card"><div class="metric-title">Demora Promedio</div><div class="metric-value-number" style="color:#17a2b8;">{round(prom_demora_as, 1)} <span style="font-size:1rem;">Días</span></div></div>', unsafe_allow_html=True)
        ca3.markdown(f'<div class="metric-card"><div class="metric-title">Ticket Más Viejo</div><div class="metric-value-number" style="color:#dc3545;">{max_demora_as} <span style="font-size:1rem;">Días</span></div></div>', unsafe_allow_html=True)
        ca4.markdown(f'<div class="metric-card"><div class="metric-title">Tickets Fuera de SLA</div><div class="metric-value-number" style="color:#6f42c1;">{criticos_as}</div><div class="metric-subtitle-red">> 30 días totales</div></div>', unsafe_allow_html=True)
        
        st.markdown(f"#### 📋 Listado Completo de Pedidos de: {asesor_sel}")
        
        # Tabla filtrada y ordenada por antigüedad del asesor elegido
        df_as_display = df_as.sort_values(by='Días desde Creación', ascending=False).drop(columns=['De', 'Año'], errors='ignore')
        st.dataframe(df_as_display, use_container_width=True, hide_index=True)
