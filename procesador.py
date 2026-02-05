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
        
        # Identificar Colaborador
        if "Empleado" in linea_unida:
            match_id = re.search(r'(\d{7,12})', linea_unida.replace('|', '').replace('.', ''))
            if match_id:
                id_val = match_id.group(1)
                if id_val not in resultados:
                    nombre_sucio = " ".join(fila).replace("Empleado", "").replace(id_val, "")
                    nombre_limpio = re.sub(r'[^a-zA-Z\s]', '', nombre_sucio).strip().upper()
                    
                    resultados[id_val] = {
                        'N°': len(resultados) + 1, 'NOMBRE': nombre_limpio, 'CEDULA ': id_val,
                        'CTA CONSIGNACION': '', 'BRUTO_TOTAL': 0.0, 'DEDUCIDO': 0.0,
                        'DEDUCIDO SINDICATO': 0.0, 'DEDUCIDO FUNERARIA SAN NICOLAS': 0.0,
                        'DEDUCIDO CORPODIMA': 0.0, 'DEDUCIDO CASINO MIRAFLOREZ': 0.0,
                        'TRABAJO OCASIONAL': 0.0
                    }
                    for n in codigos_manuales.values(): resultados[id_val][n] = 0.0
                id_actual = id_val

        if not id_actual: continue
        montos = [limpiar_monto(c) for c in fila if "," in c and re.search(r'\d', c)]

        # --- LÓGICA DE TRABAJO OCASIONAL ---
        dias_esp = ["SÁBADO", "DOMINGO", "FESTIVO", "DOMINICAL"]
        if any(d in linea_unida.upper() for d in dias_esp):
            # Si NO es solo la etiqueta del día, sumamos el valor a Ocasional
            desc = linea_unida.upper()
            if not re.search(r'^\d?(FESTIVO|DOMINICAL|DOMINGO|SABADO)$', desc.strip()):
                if montos: resultados[id_actual]['TRABAJO OCASIONAL'] += montos[-1]

        # Conceptos fijos y manuales
        if "5059" in linea_unida: resultados[id_actual]['DEDUCIDO SINDICATO'] = montos[-1]
        elif "3802" in linea_unida: resultados[id_actual]['DEDUCIDO FUNERARIA SAN NICOLAS'] = montos[-1]
        elif "3600" in linea_unida: resultados[id_actual]['DEDUCIDO CASINO MIRAFLOREZ'] = montos[-1]
        elif "5001" in linea_unida: resultados[id_actual]['DEDUCIDO CORPODIMA'] = montos[1] if len(montos) >= 2 else 0
        elif "NOMINA" in linea_unida and "+ OTROS" in linea_unida:
             if len(montos) >= 3: resultados[id_actual]['BRUTO_TOTAL'] = montos[2]
        elif "VALOR TOTAL DESCUENTOS" in linea_unida:
            if montos: resultados[id_actual]['DEDUCIDO'] = montos[0]
        
        for cod, nom in codigos_manuales.items():
            if cod in linea_unida and montos: resultados[id_actual][nom] = montos[-1]

    # Post-procesamiento para que coincida con la estructura solicitada
    df = pd.DataFrame(resultados.values()).fillna(0)
    
    # TOTAL DEVENGADO (Para el Excel) = Bruto Total - Trabajo Ocasional
    df['TOTAL DEVENGADO'] = df['BRUTO_TOTAL'] - df['TRABAJO OCASIONAL']
    
    # Deducidos Adicionales (Sindicato, etc.) no restan de NOMINA CAT si ya están en DEDUCIDO
    # Según tu Excel: NOMINA CAT = TOTAL DEVENGADO - DEDUCIDO_TOTAL
    df['NOMINA CAT '] = df['TOTAL DEVENGADO'] - df['DEDUCIDO']
    df['VALOR A PAGAR'] = df['NOMINA CAT '] + df['TRABAJO OCASIONAL']

    cols_finales = ['N°', 'NOMBRE', 'CEDULA ', 'CTA CONSIGNACION', 'TOTAL DEVENGADO', 'DEDUCIDO', 
                    'DEDUCIDO SINDICATO', 'DEDUCIDO FUNERARIA SAN NICOLAS', 'DEDUCIDO CORPODIMA', 
                    'DEDUCIDO CASINO MIRAFLOREZ'] + list(codigos_manuales.values()) + \
                   ['NOMINA CAT ', 'TRABAJO OCASIONAL', 'VALOR A PAGAR']
    
    return df.reindex(columns=cols_finales).fillna(0)
