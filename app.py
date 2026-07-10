import streamlit as st
import pandas as pd
import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Seguimiento de Tickets - Repuestos", layout="wide")
st.title("📦 Tablero de Seguimiento: Tickets de Repuestos")
st.markdown("Resumen general de pedidos, estados y demoras en el sector de repuestos.")
st.divider()

# 2. Leer los datos directamente del Google Sheet Público
# Transformamos tu link para que se descargue como CSV automáticamente
SHEET_URL = "https://docs.google.com/spreadsheets/d/14jP7-5vs_yuK5JqeTlPgF2lFT2eHI1RqQOSqG2_UZRw/export?format=csv&gid=0"

@st.cache_data(ttl=600) # Cacheamos los datos por 10 minutos para que la app sea rápida
def cargar_datos():
    # Leemos el CSV. Como las fechas en Argentina son Día/Mes/Año, usamos dayfirst=True
    df = pd.read_csv(SHEET_URL)
    
    # Convertimos las columnas de fecha a formato datetime de Pandas para poder hacer cálculos
    df['Fecha de creación'] = pd.to_datetime(df['Fecha de creación'], format='%d/%m/%Y %H:%M', errors='coerce')
    df['Última actualización'] = pd.to_datetime(df['Última actualización'], format='%d/%m/%Y %H:%M', errors='coerce')
    
    # Calculamos los "Días de Demora" (desde que se creó hasta hoy)
    hoy = pd.Timestamp.now()
    df['Días Demora'] = (hoy - df['Fecha de creación']).dt.days
    
    # Rellenamos los días nulos con 0 por si hay errores de fecha
    df['Días Demora'] = df['Días Demora'].fillna(0).astype(int)
    
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.stop()

# 3. Lógica de Negocio (Estados)
# ACA DEFINIMOS QUE ESTADOS CIERRAN EL TICKET (Modificar si hay más)
estados_cerrados = ["Pedido Completo"]

# Separamos los tickets activos de los cerrados
df_activos = df[~df["Estado actual"].isin(estados_cerrados)]
df_cerrados = df[df["Estado actual"].isin(estados_cerrados)]

# 4. KPI's (Métricas Generales)
st.subheader("Resumen General (Tickets Activos)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Tickets Activos", value=len(df_activos))
with col2:
    st.metric(label="Tickets Cerrados (Histórico)", value=len(df_cerrados))
with col3:
    # Promedio de demora solo de los tickets que siguen activos
    demora_promedio = df_activos["Días Demora"].mean()
    if pd.isna(demora_promedio): demora_promedio = 0
    st.metric(label="Demora Promedio (Días)", value=round(demora_promedio, 1))
with col4:
    # Como no tenemos columna de monto aún, dejamos un placeholder
    st.metric(label="Monto Detenido ($)", value="Falta Columna", help="No se detectó columna de montos en el Excel.")

st.divider()

# 5. Gráficos y Tablas
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Tickets Activos por Asesor ('De')")
    # Agrupamos por la columna 'De' y contamos los tickets
    tickets_por_asesor = df_activos["De"].value_counts()
    st.bar_chart(tickets_por_asesor)

with col_graf2:
    st.subheader("Tickets Activos por Estado")
    # Agrupamos por estado
    tickets_por_estado = df_activos["Estado actual"].value_counts()
    st.bar_chart(tickets_por_estado)

st.divider()

st.subheader("Detalle de Tickets Activos")
# Mostramos la tabla filtrada (solo activos) ordenados por los que tienen más demora
st.dataframe(
    df_activos.sort_values(by="Días Demora", ascending=False), 
    use_container_width=True,
    hide_index=True
)
