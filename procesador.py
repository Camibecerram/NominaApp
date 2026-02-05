import csv
import re
import pandas as pd

def limpiar_monto(texto):
    if not texto: return 0.0
    limpio = str(texto).replace('"', '').strip().replace('.', '').replace(',', '.')
    try: return float(limpio)
    except: return 0.0

def procesar_para_plantilla(archivo_bytes):
    # Streamlit pasa el archivo como bytes, lo decodificamos
    contenido = archivo_bytes.read().decode('utf-8-sig').splitlines()
    lector = csv.reader(contenido)
    
    resultados = {}
    id_actual = None

    for fila in lector:
        linea_unida = "|".join(fila)
        if "Empleado" in linea_unida:
            match_id = re.search(r'(\d{7,12})', linea_unida.replace('|', '').replace('.', ''))
            if match_id:
                id_val = match_id.group(1)
                if id_val not in resultados:
                    nombre = next((c.strip() for c in fila if len(c.strip()) > 10 and "Empleado" not in c), "Desconocido")
                    resultados[id_val] = {
                        'N°': len(resultados) + 1, 'NOMBRE': nombre, 'CEDULA ': id_val,
                        'CTA CONSIGNACION': '', 'TOTAL DEVENDADO': 0.0, 'TOTAL DEDUCCIONES': 0.0,
                        'DEDUCIDO': 0.0, 'DEDUCIDO SINDICATO': 0.0, 'DEDUCIDO FUNERARIA SAN NICOLAS': 0.0,
                        'DEDUCIDO CORPODIMA': 0.0, 'DEDUCIDO CASINO MIRAFLOREZ': 0.0,
                        'VALOR A PAGAR': 0.0
                    }
                id_actual = id_val

        if not id_actual: continue
        montos = [limpiar_monto(c) for c in fila if "," in c and re.search(r'\d', c)]
        
        # Mapeo de conceptos (Sindicato, Corpodima, etc.)
        if "5059" in linea_unida: resultados[id_actual]['DEDUCIDO SINDICATO'] = montos[-1]
        elif "3802" in linea_unida: resultados[id_actual]['DEDUCIDO FUNERARIA SAN NICOLAS'] = montos[-1]
        elif "5001" in linea_unida: resultados[id_actual]['DEDUCIDO CORPODIMA'] = montos[1] if len(montos) >= 2 else 0
        elif "NOMINA" in linea_unida and "+ OTROS" in linea_unida:
            if len(montos) >= 3: resultados[id_actual]['TOTAL DEVENDADO'] = montos[2]
        elif "VALOR TOTAL NETO A PAGAR" in linea_unida:
            if montos: resultados[id_actual]['VALOR A PAGAR'] = montos[0]

    return pd.DataFrame(resultados.values())