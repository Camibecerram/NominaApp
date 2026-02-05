import streamlit as st
import pandas as pd
from procesador import procesar_para_plantilla

st.set_page_config(page_title="Nómina Grupo Miraflorez", page_icon="🌱", layout="wide")

st.markdown("# 🌱 Gestión de Nómina - Grupo Miraflorez")
st.divider()

# --- BARRA LATERAL PARA NUEVOS CÓDIGOS ---
st.sidebar.header("⚙️ Conceptos Adicionales")
st.sidebar.write("Si hay códigos nuevos en esta catorcena, añádalos aquí:")

# Tabla para ingresar Código y Nombre
if 'filas_extras' not in st.session_state:
    st.session_state.filas_extras = pd.DataFrame([{"Código": "", "Nombre Columna": ""}])

editor_codigos = st.sidebar.data_editor(
    st.session_state.filas_extras,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Código": st.column_config.TextColumn("Código (ej: 7088)", help="Código numérico del software"),
        "Nombre Columna": st.column_config.TextColumn("Nombre en Excel", help="Cómo se llamará la columna")
    }
)

# Convertir la tabla en un diccionario de búsqueda
codigos_manuales = {row["Código"]: row["Nombre Columna"] for _, row in editor_codigos.iterrows() if row["Código"] and row["Nombre Columna"]}

# --- CARGA DE ARCHIVO ---
archivo_subido = st.file_uploader("📂 Subir archivo de la catorcena (CSV)", type=["csv"])

if archivo_subido:
    if st.button("🚀 GENERAR REPORTE"):
        with st.spinner('Procesando...'):
            # Enviamos el archivo y tus códigos manuales al procesador
            df_final = procesar_para_plantilla(archivo_subido, codigos_manuales)
            
            st.markdown("### **Vista Previa del Reporte**")
            st.dataframe(df_final)
            
            csv_data = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 DESCARGAR REPORTE",
                data=csv_data,
                file_name="Nomina_Miraflorez_Final.csv",
                mime="text/csv"
            )
