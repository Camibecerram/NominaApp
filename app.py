import streamlit as st
import pandas as pd
from procesador import procesar_para_plantilla

# Configuración visual
st.set_page_config(page_title="Nómina Grupo Miraflorez", page_icon="🌱", layout="wide")

# --- DISEÑO DE INTERFAZ LINDA ---
st.markdown("# 🌱 Sistema de Gestión de Nómina")
st.markdown("## **Grupo Miraflorez**")
st.divider()

st.markdown("""
### **Instrucciones de uso:**
1. **Configuración:** Si existen códigos nuevos en esta catorcena, añádalos en la tabla de la izquierda.
2. **Carga:** Suba el archivo CSV exportado de su software contable.
3. **Procesamiento:** El sistema generará la relación de pagos con el formato oficial.
""")

# --- BARRA LATERAL PARA NUEVOS CÓDIGOS ---
st.sidebar.header("⚙️ Conceptos Adicionales")
st.sidebar.write("Añada aquí descuentos nuevos (Ej: Préstamos, Seguros):")

if 'filas_extras' not in st.session_state:
    st.session_state.filas_extras = pd.DataFrame([{"Código": "", "Nombre Columna": ""}])

editor_codigos = st.sidebar.data_editor(
    st.session_state.filas_extras,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Código": st.column_config.TextColumn("Código Software"),
        "Nombre Columna": st.column_config.TextColumn("Nombre en Excel")
    }
)

codigos_manuales = {row["Código"]: row["Nombre Columna"].upper() for _, row in editor_codigos.iterrows() if row["Código"] and row["Nombre Columna"]}

# --- CARGA Y ACCIÓN ---
archivo_subido = st.file_uploader("📂 Seleccione el archivo de la catorcena", type=["csv"])

if archivo_subido:
    st.success("✅ Archivo listo para procesar")
    if st.button("🚀 **GENERAR REPORTE ADMINISTRATIVO**"):
        with st.spinner('Organizando datos del Grupo Miraflorez...'):
            df_final = procesar_para_plantilla(archivo_subido, codigos_manuales)
            
            st.divider()
            st.markdown("### **Vista Previa: Relación de Pagos Organizada**")
            st.dataframe(df_final)
            
            csv_data = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 **DESCARGAR RELACIÓN DE PAGOS (CSV)**",
                data=csv_data,
                file_name="Relacion_Pagos_Miraflorez.csv",
                mime="text/csv"
            )

