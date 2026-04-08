import pandas as pd
import re
import json
from tkinter import Tk, Button, filedialog, messagebox

def limpiar_e_identificar(nombre_sucio):
    nombre = str(nombre_sucio).strip().upper()
    # Inteligencia de Derivados: Buscamos 1/2, 3/4, LT, GL, MM, MT, etc.
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

def corregir_precio(valor):
    # Esta función convierte "0,45" en 0.45 para que Python lo entienda
    try:
        if pd.isna(valor): return 0.0
        s_valor = str(valor).replace(',', '.')
        return round(float(s_valor), 2)
    except:
        return 0.0

def procesar_archivo():
    ruta = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")])
    if not ruta: return

    try:
        # Cargamos el CSV con el separador ";" que detectamos en tu archivo
        df = pd.read_csv(ruta, skiprows=3, header=None, encoding='latin1', sep=';', engine='python')
        
        productos_agrupados = {}
        contador_filas = 0

        for i, fila in df.iterrows():
            try:
                # El archivo tiene: [0]Nombre, [1]Código, [2]PrecioSinIva, [3]IVA, [4]PrecioFinal
                if len(fila) < 5 or pd.isna(fila[0]) or pd.isna(fila[1]):
                    continue
                
                nombre_raw = str(fila[0])
                codigo = str(fila[1])
                precio_final = corregir_precio(fila[4])

                nombre_base, medida, categoria = limpiar_e_identificar(nombre_raw)

                if nombre_base not in productos_agrupados:
                    productos_agrupados[nombre_base] = {
                        "nombre_principal": nombre_base,
                        "categoria": categoria,
                        "variantes": []
                    }
                
                productos_agrupados[nombre_base]["variantes"].append({
                    "sku": codigo,
                    "medida": medida,
                    "precio": precio_final
                })
                contador_filas += 1
            except:
                continue

        # Guardar el JSON limpio
        with open('productosExcel.json', 'w', encoding='utf-8') as f:
            json.dump(list(productos_agrupados.values()), f, indent=4, ensure_ascii=False)
        
        messagebox.showinfo("Éxito", f"¡Inventario procesado!\n\nSe leyeron {contador_filas} filas.\nSe crearon {len(productos_agrupados)} grupos de productos.")

    except Exception as e:
        messagebox.showerror("Error Crítico", f"No se pudo leer el archivo.\nDetalle: {str(e)}")

# INTERFAZ
root = Tk()
root.title("IA Limpiadora Lozada")
root.geometry("350x200")
root.configure(bg="#1e1e1e")

btn = Button(root, text="SELECCIONAR INVENTARIO", command=procesar_archivo, 
             bg="#FF5722", fg="white", font=("Arial", 11, "bold"), padx=20, pady=10)
btn.pack(expand=True)

root.mainloop()