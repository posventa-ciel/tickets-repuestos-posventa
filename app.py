import streamlit as st
import pandas as pd
import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Seguimiento de Tickets - Repuestos", layout="wide")
st.title("🚥 Tablero de Seguimiento: Alertas y SLAs")
st.markdown("Control de tiempos de entrega de repuestos y demoras en taller.")
st.divider()

# 2. Leer los datos
SHEET_URL = "https://docs.google.com/spreadsheets/d/14jP7-5vs_yuK5JqeTlPgF2lFT2eHI1RqQOSqG2_UZRw/export?format=csv&gid=0"

@st.cache_data(ttl=600) 
def cargar_datos():
    df = pd.read_csv(SHEET_URL)
    
    # Convertimos las fechas
    df['Fecha de creación'] = pd.to_datetime(df['Fecha de creación'], format='%d/%m/%Y %H:%M', errors='coerce')
    df['Última actualización'] = pd.to_datetime(df['Última actualización'], format='%d/%m/%Y %H:%M', errors='coerce')
    
    hoy = pd.Timestamp.now()
    
    # Cálculo 1: Días desde la creación (Para regla general y regla de repuestos)
    df['Días desde Creación'] = (hoy - df['Fecha de creación']).dt.days
    df['Días desde Creación'] = df['Días desde Creación'].fillna(0).astype(int)
    
    # Cálculo 2: Días en el estado actual (Para medir al taller cuando ya está completo)
    df['Días en Estado Actual'] = (hoy - df['Última actualización']).dt.days
    df['Días en Estado Actual'] = df['Días en Estado Actual'].fillna(0).astype(int)
    
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.stop()

# 3. Lógica de Alertas
# Tickets que no son "Pedido Completo" y llevan más de 15 días (Culpa de origen/fábrica/repuestos)
mas_15_dias_sin_llegar = df[(df["Estado actual"] != "Pedido Completo") & (df["Días desde Creación"] > 15)]

# Tickets generales que superaron los 30 días de vida
mas_30_dias_global = df[df["Días desde Creación"] > 30]

# 4. KPI's (Métricas de Alertas)
st.subheader("Panel de Alertas")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Tickets Abiertos", value=len(df))
with col2:
    st.metric(label="🚨 Demora Repuestos (>15 días sin llegar)", value=len(mas_15_dias_sin_llegar), 
              help="Tickets con más de 15 días desde su creación que aún NO están en 'Pedido Completo'.")
with col3:
    st.metric(label="⚠️ Demora Global (>30 días totales)", value=len(mas_30_dias_global),
              help="Tickets que superaron los 30 días de antigüedad desde su creación, independientemente de su estado.")

st.divider()

# 5. Función de Semáforo (Colores para la tabla)
def aplicar_semaforo(row):
    estado = row['Estado actual']
    dias_creacion = row['Días desde Creación']
    dias_estado = row['Días en Estado Actual']
    
    # Reglas para cuando el repuesto YA LLEGÓ (Evaluamos al taller)
    if estado == "Pedido Completo":
        if dias_estado <= 15:
            return ['background-color: #c3f9c3; color: black'] * len(row) # Verde suave
        elif 15 < dias_estado <= 30:
            return ['background-color: #fcf9a8; color: black'] * len(row) # Amarillo suave
        else:
            return ['background-color: #f9c3c3; color: black'] * len(row) # Rojo suave
            
    # Reglas para cuando el repuesto AÚN NO LLEGÓ (Evaluamos a repuestos)
    else:
        if dias_creacion > 15:
            # Alerta roja clara porque la pieza está demorada
            return ['background-color: #ff9999; color: black; font-weight: bold'] * len(row) 
        else:
            # Sin color, tiempo normal de espera
            return [''] * len(row)

# 6. Mostrar la Tabla con el Semáforo
st.subheader("Detalle de Tickets (Semáforo Inteligente)")
st.markdown("""
**Referencias de color:**
* 🟩 **Verde:** Repuesto llegado ('Pedido Completo'). Taller en plazo ideal (0-15 días).
* 🟨 **Amarillo:** Repuesto llegado. Taller en plazo de advertencia (16-30 días).
* 🟥 **Rojo:** Repuesto llegado pero Taller demorado (>30 días) **Ó** Repuesto no llegó y pasaron >15 días desde la creación.
""")

# Aplicamos el estilo a nuestro DataFrame y lo mostramos
# Ocultamos la columna "Última actualización" para no confundir si sabemos que viene mal de origen por ahora,
# pero el cálculo por detrás se hace igual. Si querés verla, borrala de la lista de abajo.
df_mostrar = df.drop(columns=['De', 'Asunto', 'Prioridad'], errors='ignore') # Limpiamos columnas menos urgentes visualmente

st.dataframe(
    df.style.apply(aplicar_semaforo, axis=1), 
    use_container_width=True,
    hide_index=True
)
