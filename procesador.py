import csv
import re
import pandas as pd

def limpiar_monto(texto):
    if not texto: return 0.0
    limpio = str(texto).replace('"', '').strip().replace('.', '').replace(',', '.')
    try: return float(limpio)
    except: return 0.0

def procesar_para_plantilla(archivo_bytes):
    # Decodificar el archivo subido
    contenido = archivo_bytes.read().decode('utf-8-sig', errors='ignore').splitlines()
    lector = csv.reader(contenido)
    
    resultados = {}
    id_actual = None

    for fila in lector:
        linea_unida = "|".join(fila)
        
        if "Empleado" in linea_unida:
            # 1. Extraer la Cédula (buscamos solo números largos)
            match_id = re.search(r'(\d{7,12})', linea_unida.replace('|', '').replace('.', ''))
            if match_id:
                id_val = match_id.group(1)
                if id_val not in resultados:
                    # 2. LIMPIEZA DE NOMBRE:
                    # Tomamos toda la fila donde dice "Empleado"
                    texto_nombre = " ".join(fila)
                    # Quitamos la palabra 'Empleado', la cédula y cualquier número o signo
                    nombre_solo_letras = texto_nombre.replace("Empleado", "").replace(id_val, "")
                    # Borramos cualquier dígito, punto o guion que haya quedado
                    nombre_final = re.sub(r'[^a-zA-Z\s]', '', nombre_solo_letras).strip()
                    
                    # Si por algún motivo queda vacío, buscamos la celda de texto más larga
                    if len(nombre_final) < 3:
                        nombre_final = next((c.strip() for c in fila if len(re.sub(r'[^a-zA-Z]', '', c)) > 10), "Desconocido")

                    resultados[id_val] = {
                        'N°': len(resultados) + 1,
                        'NOMBRE': nombre_final.upper(), # Todo en mayúsculas para que se vea ordenado
                        'CEDULA ': id_val,
                        'CTA CONSIGNACION': '',
                        'TOTAL DEVENDADO': 0.0,
                        'TOTAL DEDUCCIONES': 0.0,
                        'DEDUCIDO': 0.0,
                        'DEDUCIDO SINDICATO': 0.0,
                        'DEDUCIDO FUNERARIA SAN NICOLAS': 0.0,
                        'DEDUCIDO CORPODIMA': 0.0,
                        'DEDUCIDO CASINO MIRAFLOREZ': 0.0,
                        'VALOR A PAGAR': 0.0
                    }
                id_actual = id_val

        if not id_actual: continue
        
        # El resto del código de montos se mantiene igual...
        montos = [limpiar_monto(c) for c in fila if "," in c and re.search(r'\d', c)]
        if "5059" in linea_unida: resultados[id_actual]['DEDUCIDO SINDICATO'] = montos[-1]
        elif "3802" in linea_unida: resultados[id_actual]['DEDUCIDO FUNERARIA SAN NICOLAS'] = montos[-1]
        elif "3600" in linea_unida: resultados[id_actual]['DEDUCIDO CASINO MIRAFLOREZ'] = montos[-1]
        elif "5001" in linea_unida: resultados[id_actual]['DEDUCIDO CORPODIMA'] = montos[1] if len(montos) >= 2 else 0
        elif "NOMINA" in linea_unida and "+ OTROS" in linea_unida:
            if len(montos) >= 3: resultados[id_actual]['TOTAL DEVENDADO'] = montos[2]
        elif "VALOR TOTAL NETO A PAGAR" in linea_unida:
            if montos: resultados[id_actual]['VALOR A PAGAR'] = montos[0]
        elif "VALOR TOTAL DESCUENTOS" in linea_unida:
            if montos: resultados[id_actual]['DEDUCIDO'] = montos[0]

    return pd.DataFrame(resultados.values())


    return pd.DataFrame(resultados.values())
