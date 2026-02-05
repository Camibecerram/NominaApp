import csv
import re
import pandas as pd

def limpiar_monto(texto):
    if not texto: return 0.0
    limpio = str(texto).replace('"', '').strip().replace('.', '').replace(',', '.')
    try: return float(limpio)
    except: return 0.0

def procesar_para_plantilla(archivo_bytes, codigos_manuales={}):
    contenido = archivo_bytes.read().decode('utf-8-sig', errors='ignore').splitlines()
    lector = csv.reader(contenido)
    
    resultados = {}
    id_actual = None

    for fila in lector:
        linea_unida = "|".join(fila)
        
        # 1. Identificar Empleado y Limpiar Nombre
        if "Empleado" in linea_unida:
            match_id = re.search(r'(\d{7,12})', linea_unida.replace('|', '').replace('.', ''))
            if match_id:
                id_val = match_id.group(1)
                if id_val not in resultados:
                    texto_nombre = " ".join(fila)
                    nombre_solo_letras = texto_nombre.replace("Empleado", "").replace(id_val, "")
                    nombre_final = re.sub(r'[^a-zA-Z\s]', '', nombre_solo_letras).strip().upper()
                    
                    resultados[id_val] = {
                        'N°': len(resultados) + 1,
                        'NOMBRE': nombre_final,
                        'CEDULA': id_val,
                        'CTA CONSIGNACION': '',
                        'TOTAL DEVENDADO': 0.0,
                        'DEDUCIDO': 0.0,
                        'DEDUCIDO SINDICATO': 0.0,
                        'DEDUCIDO FUNERARIA SAN NICOLAS': 0.0,
                        'DEDUCIDO CORPODIMA': 0.0,
                        'DEDUCIDO CASINO MIRAFLOREZ': 0.0,
                        'TRABAJO OCASIONAL': 0.0 # Nueva columna activa
                    }
                    for nombre_col in codigos_manuales.values():
                        resultados[id_val][nombre_col] = 0.0
                id_actual = id_val

        if not id_actual: continue
        
        montos = [limpiar_monto(c) for c in fila if "," in c and re.search(r'\d', c)]
        
        # --- LÓGICA DE TRABAJO OCASIONAL (Sábados, Domingos, Festivos) ---
        # Si la fila menciona un día de fin de semana o festivo
        dias_ocasionales = ["sábado", "domingo", "festivo", "dominical"]
        if any(dia in linea_unida.lower() for dia in dias_ocasionales):
            # NO tomamos el monto si la descripción es SOLO el nombre del día (ej: "1FESTIVO")
            # Pero SI sumamos los valores de labores realizadas esos días
            if not re.search(r'^\d?(FESTIVO|DOMINICAL|DOMINGO|SABADO)$', linea_unida.strip().upper()):
                if montos:
                    resultados[id_actual]['TRABAJO OCASIONAL'] += montos[-1]

        # --- CONCEPTOS FIJOS Y TOTALES ---
        if "5059" in linea_unida: resultados[id_actual]['DEDUCIDO SINDICATO'] = montos[-1]
        elif "3802" in linea_unida: resultados[id_actual]['DEDUCIDO FUNERARIA SAN NICOLAS'] = montos[-1]
        elif "3600" in linea_unida: resultados[id_actual]['DEDUCIDO CASINO MIRAFLOREZ'] = montos[-1]
        elif "5001" in linea_unida: resultados[id_actual]['DEDUCIDO CORPODIMA'] = montos[1] if len(montos) >= 2 else 0
        elif "NOMINA" in linea_unida and "+ OTROS" in linea_unida and len(montos) >= 3:
            resultados[id_actual]['TOTAL DEVENDADO'] = montos[2]
        elif "VALOR TOTAL NETO A PAGAR" in linea_unida and montos:
            resultados[id_actual]['VALOR A PAGAR'] = montos[0]
        elif "VALOR TOTAL DESCUENTOS" in linea_unida and montos:
            resultados[id_actual]['DEDUCIDO'] = montos[0]

        # Conceptos manuales desde la interfaz
        for cod, nombre_col in codigos_manuales.items():
            if cod in linea_unida and montos:
                resultados[id_actual][nombre_col] = montos[-1]

    return pd.DataFrame(resultados.values())

