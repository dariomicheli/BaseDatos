from db_connections import db_redis as r

def borrar_reservas_temporales():
    claves = list(r.scan_iter("reserva_temp:*"))
    if not claves:
        return "No hay reservas temporales para borrar."

    r.delete(*claves)
    return f"🧹 {len(claves)} reservas temporales eliminadas."

def carga_masiva_reservas_temporales(df):
    """
    Carga masivamente en Redis las reservas temporales
    """

    if df is None or df.empty:
        return None

    borrar_reservas_temporales()
        
    filas = df.to_dict(orient="records")
    
    for fila in filas:
         r.hset(f"reserva_temp:{fila['reserva_id']}", mapping={
                "usuario_id": fila["usuario_id"],
                "destino_id": fila["destino_id"],
                "fecha_reserva": fila["fecha_reserva"],
                "precio_total": fila["precio_total"],
                "estado": fila["estado"]
                })

    return len(filas)

"""
claves = db_redis.keys("reserva_temp:*")

for clave in claves:
    datos = db_redis.hgetall(clave)
    print(f"{clave}: {datos}")
"""
