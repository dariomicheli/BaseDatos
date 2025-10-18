from db_connections import db_redis as r
import random

def borrar_reservas_temporales():
    claves = list(r.scan_iter("reserva_temp:*"))
    
    if not claves:
        return None
    
    r.delete(*claves)
    
    return len(claves)

def carga_masiva_reservas_temporales(df, ttl=3600):
    """
    Carga masivamente en Redis las reservas temporales
    """
    if df is None or df.empty:
        return None

    borrar_reservas_temporales()    
    filas = df.to_dict(orient="records")
    
    for fila in filas:
        clave = f"reserva_temp:{fila['reserva_id']}"
        r.hset(clave, mapping={
                "usuario_id": fila["usuario_id"],
                "destino_id": fila["destino_id"],
                "fecha_reserva": fila["fecha_reserva"],
                "precio_total": fila["precio_total"]
        })
        r.expire(clave, ttl)

    return len(filas)

def guardar_usuarios_conectados(df, cantidad=10):
    """
    Elige aleatoriamente `cantidad` usuarios del DataFrame
    y los guarda en Redis como conectados.
    """  
    if df is None or df.empty:
        return None

    # Elige aleatoriamente sin repetir
    seleccionados = df.sample(n=min(cantidad, len(df)), random_state=42)
    filas = seleccionados.to_dict(orient="records")

    for fila in filas:
        r.set(f"usuario:{fila['usuario_id']}:sesion", "activa", ex=3600) #Expira en 1hs

    return len(filas)
