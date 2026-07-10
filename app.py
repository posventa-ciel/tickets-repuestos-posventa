import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(page_title="Seguimiento de Tickets - Repuestos", layout="wide")

st.title("📦 Tablero de Seguimiento: Tickets de Repuestos")
st.markdown("Resumen general de pedidos, estados y demoras en el sector de repuestos.")

st.divider()

# Conexión con Google Sheets
# Nota: Para que esto funcione, luego configuraremos los "Secrets" en Streamlit
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Reemplazá 'URL_DE_TU_SHEET' por la URL completa de tu Google Sheet
    df = conn.read(spreadsheet="URL_DE_TU_SHEET", usecols=list(range(10))) # Ajustar cantidad de columnas
    st.success("Datos cargados correctamente.")
except Exception as e:
    st.warning("Aún no se ha configurado la conexión con el Google Sheet. Mostrando datos de prueba...")
    # Datos de prueba para ir viendo el diseño mientras tanto
    df = pd.DataFrame({
        "Asesor": ["Juan", "María", "Pedro", "Juan"],
        "Estado": ["Pendiente", "Demorado", "Cerrado", "En Tránsito"],
        "Días Demora": [2, 5, 0, 1],
        "Monto Detenido": [150000, 450000, 0, 320000]
    })

# --- SECCIÓN DE KPIs GENERALES ---
st.subheader("Resumen General")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Tickets Totales", value=len(df))
with col2:
    st.metric(label="Tickets Pendientes", value=len(df[df["Estado"] != "Cerrado"]))
with col3:
    st.metric(label="Demora Promedio (Días)", value=round(df["Días Demora"].mean(), 1))
with col4:
    st.metric(label="Monto Detenido ($)", value=f"${df['Monto Detenido'].sum():,.2f}")

st.divider()

# --- SECCIÓN DE TABLAS Y GRÁFICOS ---
# Acá luego agregaremos los gráficos de tickets por asesor y análisis de demoras
st.subheader("Detalle de Tickets")
st.dataframe(df, use_container_width=True)
