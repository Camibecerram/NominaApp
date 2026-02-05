import streamlit as st
from procesador import procesar_para_plantilla

# Configuración de la página con estilo Miraflorez
st.set_page_config(page_title="Nómina Grupo Miraflorez", page_icon="🌱", layout="wide")

# Diseño estético (Título y Negrillas)
st.markdown("# 🌱 Sistema de Gestión de Nómina")
st.markdown("## **Grupo Miraflorez**")
st.divider()

st.markdown("""
### **Instrucciones de uso:**
1. **Cargue** el archivo CSV exportado de su software contable.
2. El sistema extraerá automáticamente: **TOTAL DEVENGADO, DEDUCIDOS y NETOS**.
3. **Descargue** el reporte final listo para su relación de pagos.
""")

archivo_subido = st.file_uploader("📂 Seleccione el archivo de la catorcena", type=["csv"])

if archivo_subido is not None:
    st.success("✅ Archivo cargado correctamente")
    
    if st.button("🚀 **Generar Reporte Administrativo**"):
        with st.spinner('Procesando datos...'):
            df_resultado = procesar_para_plantilla(archivo_subido)
            
            st.divider()
            st.markdown("### **Vista Previa del Reporte Organizado**")
            st.dataframe(df_resultado)
            
            # Botón de descarga
            csv_data = df_resultado.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 **Descargar Relación de Pagos (CSV)**",
                data=csv_data,
                file_name="Relacion_Pagos_Miraflorez.csv",
                mime="text/csv"
            )
