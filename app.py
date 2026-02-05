import streamlit as st
from procesador import procesar_para_plantilla

st.set_page_config(page_title="Nómina Grupo Miraflorez", page_icon="🌱")

st.title("🌱 Grupo Miraflorez")
st.header("Portal de Procesamiento de Nómina")

uploaded_file = st.file_uploader("Cargue el archivo CSV de su software contable", type=["csv"])

if uploaded_file is not None:
    st.success("Archivo cargado.")
    if st.button("Generar Reporte Administrativo"):
        df_final = procesar_para_plantilla(uploaded_file)
        
        st.subheader("Vista Previa")
        st.dataframe(df_final)
        
        # Generar el botón de descarga
        csv_data = df_final.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Descargar Reporte Final (CSV)",
            data=csv_data,
            file_name="Reporte_Miraflorez_Final.csv",
            mime="text/csv"
        )