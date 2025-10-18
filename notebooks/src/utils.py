import pandas as pd
from pathlib import Path

def lectura_csv(ruta):
    """Lee un CSV desde la ruta dada y devuelve un DataFrame, o None si no existe."""
    if ruta.exists():
        df = pd.read_csv(ruta)
        return df
    else:
        print("⚠️ No se encontró el archivo en:", ruta)
        return None

def procesar_csv(nombre_archivo):
    """Lee un CSV desde la carpeta 'fuentes' y devuelve un DataFrame si tiene datos."""
    ruta = Path("fuentes") / nombre_archivo
    df = lectura_csv(ruta)
    if df is None or df.empty:
        print(f"⚠️ Archivo {nombre_archivo} vacío o no encontrado.")
        return None
    return df
