import pandas as pd

def lectura_csv(ruta):
    if ruta.exists():
        df = pd.read_csv(ruta)
        return df
    else:
        print("⚠️ No se encontró el archivo en:", ruta)
        return None