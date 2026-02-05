import csv
import re
import pandas as pd

def limpiar_monto(texto):
    if not texto: return 0.0
    # Quita puntos de miles y cambia coma por punto decimal
    limpio = str(texto).replace('"', '').strip().replace('.', '').replace(',', '.')
    try: return float(limpio)
    except: return 0.0

def procesar_para_plantilla(archivo_bytes):
    contenido = archivo_bytes.read().decode('utf-8-sig', errors='ignore').splitlines()
    lector = csv.reader(contenido)
    
    resultados = {}
    id_actual = None
    todos_los_conceptos = set() # Aquí guardaremos términos nuevos que aparezcan

    # Diccionario para nombres bonitos de códigos conocidos
    nombres_fijos = {
        "5059": "DEDUCIDO SINDICATO",
        "3802": "DEDUCIDO FUNERARIA SAN NICOLAS",
        "3600": "DEDUCIDO CASINO MIRAFLOREZ",
        "5001": "DEDUCIDO CORPODIMA",
        "5033": "PENSION",
        "5057": "SALUD"
    }

    for fila in lector:
        linea_unida = "|".join(fila)
        
        # Identificar Empleado y Limpiar Nombre
        if "Empleado" in linea_unida:
            match_id = re.search(r'(\d{7,12})', linea_unida.replace('|', '').replace('.', ''))
            if match_id:
                id_val = match_id.group(1)
                if id_val not in resultados:
                    texto_nombre = " ".join(fila)
                    nombre_sucio = texto_nombre.replace("Empleado", "").replace(id_val, "")
                    nombre_final = re.sub(r'[^a-zA-Z\s]', '', nombre_sucio).strip()
                    
                    resultados[id_val] = {
                        'N°': len(resultados) + 1,
                        'NOMBRE': nombre_final.upper(),
                        'CEDULA': id_val,
                        'CTA CONSIGNACION': '',
                        'TOTAL DEVENDADO': 0.0,
                        'DEDUCIDO': 0.0, # Este es el total de descuentos
                        'VALOR A PAGAR': 0.0
                    }
                id_actual = id_val

        if not id_actual: continue
        
        # Extraer montos de la fila
        montos = [limpiar_monto(c) for c in fila if "," in c and re.search(r'\d', c)]

        # LÓGICA DE EXTRACCIÓN DINÁMICA DE DESCUENTOS
        # Si la fila tiene un código de 4 dígitos (ej: 5059, 3600, 7000)
        match_codigo = re.search(r'(\d{4})', linea_unida)
        if match_codigo and montos:
            codigo = match_codigo.group(1)
            # Buscamos el nombre del concepto (texto al lado del código)
            nombre_columna = nombres_fijos.get(codigo, f"COD_{codigo}")
            todos_los_conceptos.add(nombre_columna)
            
            # Asignar el valor (usualmente el último monto de la fila es el descuento)
            resultados[id_actual][nombre_columna] = montos[-1]

        # Otros totales fijos
        if "NOMINA" in linea_unida and "+ OTROS" in linea_unida:
            if len(montos) >= 3: resultados[id_actual]['TOTAL DEVENDADO'] = montos[2]
        elif "VALOR TOTAL NETO A PAGAR" in linea_unida:
            if montos: resultados[id_actual]['VALOR A PAGAR'] = montos[0]
        elif "VALOR TOTAL DESCUENTOS" in linea_unida:
            if montos: resultados[id_actual]['DEDUCIDO'] = montos[0]

    # Crear el DataFrame y asegurar que todas las columnas existan
    df = pd.DataFrame(resultados.values())
    
    # Rellenar con 0 los empleados que no tuvieron algún descuento específico
    for col in todos_los_conceptos:
        if col not in df.columns: df[col] = 0.0
    df = df.fillna(0)

    # Reordenar columnas para que los descuentos queden en el medio
    columnas_base = ['N°', 'NOMBRE', 'CEDULA', 'CTA CONSIGNACION', 'TOTAL DEVENDADO', 'DEDUCIDO']
    cols_descuentos = sorted(list(todos_los_conceptos))
    col_final = ['VALOR A PAGAR']
    
    return df[columnas_base + cols_descuentos + col_final]

