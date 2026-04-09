import pandas as pd
import re
import json
import os
import traceback  # <-- Para ver el error exacto en la terminal
from tkinter import Tk, Button, filedialog, messagebox

def limpiar_e_identificar(nombre_sucio):
    nombre = str(nombre_sucio).strip().upper()
    patron_medida = r'(\d+/\d+|\d+\s?LT|\d+\s?GL|\d+\s?MT|\d+\s?MM|\d+\s?PULG|XL|GRANDE|PEQUEÑO)'
    medida_encontrada = re.search(patron_medida, nombre)
    
    if medida_encontrada:
        medida = medida_encontrada.group(0)
        nombre_base = nombre.replace(medida, "").replace("  ", " ").strip()
    else:
        medida = "UNICA"
        nombre_base = nombre.replace("  ", " ").strip()

    palabras = nombre_base.split()
    categoria = palabras[0] if len(palabras) > 0 else "VARIOS"
    
    return nombre_base, medida, categoria

def procesar_archivo():
    print("\n" + "="*40)
    print("--- INICIANDO NUEVO PROCESO ---")
    ruta = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")])
    
    if not ruta: 
        print("Cancelado: No se seleccionó ningún archivo.")
        return

    print(f"Archivo seleccionado: {ruta}")

    try:
        # 1. LECTURA (Corregido a sep=';' para leer tu nuevo archivo)
        print("Paso 1: Intentando leer el archivo CSV...")
        try:
            df = pd.read_csv(ruta, skiprows=3, header=None, encoding='utf-8-sig', sep=';', engine='python')
            print(" -> Leído con éxito usando UTF-8")
        except Exception:
            print(" -> Falló UTF-8, intentando con LATIN1...")
            df = pd.read_csv(ruta, skiprows=3, header=None, encoding='latin1', sep=';', engine='python')
            print(" -> Leído con éxito usando LATIN1")
        
        # 2. PROCESAMIENTO
        print("Paso 2: Procesando filas y estructurando datos...")
        productos_agrupados = {}
        contador_filas = 0

        for i, fila in df.iterrows():
            try:
                # Verificamos que tenga las 8 columnas (para llegar al índice 7)
                if len(fila) < 8 or pd.isna(fila[0]) or pd.isna(fila[2]):
                    continue
                
                nombre_raw = str(fila[0]).strip()
                id_producto = str(fila[2]).strip()  # Columna C (Código de barra)
                precio_raw = fila[7]                # Columna H (Precio P5)

                if nombre_raw.lower() == 'nan' or id_producto.lower() == 'nan':
                    continue

                # Limpieza de precio (cambiando coma por punto decimal)
                try:
                    precio_limpio = round(float(str(precio_raw).replace(',', '.')), 2)
                except Exception:
                    precio_limpio = 0.0

                nombre_base, medida, categoria = limpiar_e_identificar(nombre_raw)

                if nombre_base not in productos_agrupados:
                    productos_agrupados[nombre_base] = {
                        "nombre_principal": nombre_base,
                        "categoria": categoria,
                        "variantes": []
                    }
                
                productos_agrupados[nombre_base]["variantes"].append({
                    "sku": id_producto,
                    "medida": medida,
                    "precio": precio_limpio
                })
                contador_filas += 1
            except Exception:
                continue

        print(f" -> Se procesaron {contador_filas} productos válidos.")
        print(f" -> Se crearon {len(productos_agrupados)} grupos únicos.")

        # 3. GUARDADO AUTOMÁTICO EN LA MISMA CARPETA
        carpeta_origen = os.path.dirname(ruta)
        ruta_json = os.path.join(carpeta_origen, 'productosExcel.json')
        print(f"Paso 3: Intentando guardar JSON en la misma carpeta...")
        print(f"Ruta exacta: {ruta_json}")

        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(list(productos_agrupados.values()), f, indent=4, ensure_ascii=False)
        
        print("¡PROCESO TERMINADO CON ÉXITO!")
        print("="*40 + "\n")
        messagebox.showinfo("Éxito", f"¡Limpieza completada!\n\nProductos leídos: {contador_filas}\n\nEl JSON se guardó en:\n{ruta_json}")

    except Exception as e:
        print("\n" + "!"*50)
        print("❌ ERROR CRÍTICO DETECTADO ❌")
        traceback.print_exc()
        print("!"*50 + "\n")
        messagebox.showerror("Error Crítico", f"Falló el proceso.\nMira la terminal de VS Code para más detalles.\n\nError: {str(e)}")

# INTERFAZ GRÁFICA
root = Tk()
root.title("IA Limpiadora Lozada")
root.geometry("350x200")
root.configure(bg="#1e1e1e")

btn = Button(root, text="SELECCIONAR MATRIZ CSV", command=procesar_archivo, 
             bg="#FF5722", fg="white", font=("Arial", 11, "bold"), padx=20, pady=10, cursor="hand2")
btn.pack(expand=True)

print("Programa iniciado. Esperando a que selecciones el archivo CSV...")
root.mainloop() 