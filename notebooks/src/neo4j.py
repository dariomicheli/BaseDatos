import pandas as pd
from pathlib import Path
from db_connections import db_neo4j
from src import utils,neo4j

def nodo_existe(label, driver):
    """
    Verifica si existen nodos de un tipo específico en Neo4j.

    Args:
        label (str): La etiqueta del nodo a verificar (ej. 'Usuario', 'Destino').
        driver: Instancia del driver de Neo4j.

    Returns:
        bool: True si existen nodos de ese tipo, False si no existen.
    """
    query = f"MATCH (n:{label}) RETURN count(n) > 0 AS existe"
    with driver.session() as session:
        resultado = session.run(query)
        return resultado.single()["existe"]

def crear_nodo(tx, nombre_nodo, clave_id, datos):
    """
    Crea un nodo en Neo4j de forma genérica si no existe.

    Parámetros:
    - tx: transacción Neo4j
    - label: etiqueta del nodo (string)
    - clave_id: nombre del campo único (string)
    - datos: diccionario con las propiedades del nodo
    """
    query = f"""
    MERGE (n:{nombre_nodo} {{{clave_id}: $valor_id}})
    ON CREATE SET
        n += $propiedades
    RETURN n
    """
    result = tx.run(
        query,
        valor_id=datos[clave_id],
        propiedades=datos
    )
    return result.single()

def crear_relacion_unidireccional(tx, nodo_origen, campo_origen, valor_origen,
                   nodo_destino, campo_destino, valor_destino,
                   tipo_relacion):
    query = f"""
    MATCH (a:{nodo_origen} {{{campo_origen}: $valor_origen}})
    MATCH (b:{nodo_destino} {{{campo_destino}: $valor_destino}})
    MERGE (a)-[r:{tipo_relacion}]->(b)
    RETURN a, b, r
    """
    return tx.run(query, valor_origen=valor_origen, valor_destino=valor_destino).single()

def crear_relacion_bidireccional(tx, nodo_origen, campo_origen, valor_origen,
                                 nodo_destino, campo_destino, valor_destino,
                                 tipo_relacion):
    query = f"""
    MATCH (a:{nodo_origen} {{{campo_origen}: $valor_origen}})
    MATCH (b:{nodo_destino} {{{campo_destino}: $valor_destino}})
    MERGE (a)-[r1:{tipo_relacion}]->(b)
    MERGE (b)-[r2:{tipo_relacion}]->(a)
    RETURN a, b, r1, r2
    """
    return tx.run(
        query,
        valor_origen=valor_origen,
        valor_destino=valor_destino
    ).single()

def consulta(db, query, parametros=None):
    """
    Ejecuta una query en Neo4j y devuelve los resultados como un DataFrame.

    Parámetros:
        db: objeto de conexión a Neo4j (db_neo4j)
        query: string con la consulta Cypher
        parametros: diccionario con parámetros de la query (opcional)

    Retorna:
        pd.DataFrame con los resultados
    """
    with db.session() as session:
        resultados = session.run(query, parametros)
        data = [record.data() for record in resultados]
    return pd.DataFrame(data)


# -------------------------------------------------------------
# FUNCIONES AUXILIARES
# -------------------------------------------------------------

def crear_nodos_neo4j(nombre_coleccion, df):
    """
    Crea nodos en Neo4j según la colección (usuarios o destinos).
    """
    if nombre_coleccion not in ["usuarios", "destinos"]:
        return

    nombre_nodo = "Usuario" if nombre_coleccion == "usuarios" else "Destino"
    campo_clave = "usuario_id" if nombre_nodo == "Usuario" else "destino_id"

    filas = df.to_dict("records")

    with db_neo4j.session() as session:
        for fila in filas:
            session.execute_write(neo4j.crear_nodo, nombre_nodo, campo_clave, fila)

    print(f"✅ Nodos de {nombre_nodo} creados exitosamente en Neo4j.")


def crear_relaciones_visito(df):
    """
    Crea relaciones VISITO entre Usuario y Destino en Neo4j 
    para reservas Confirmadas o Pagadas hasta la fecha actual.
    """
    if df.empty:
        return

    df["fecha_reserva"] = pd.to_datetime(df["fecha_reserva"], errors="coerce")
    hoy = pd.Timestamp.today().normalize()

    df_validas = df[df["estado"].isin(["Confirmada", "Pagada"]) & (df["fecha_reserva"] <= hoy)]

    if df_validas.empty:
        print("⚠️ No hay reservas confirmadas/pagadas para crear relaciones VISITO.")
        return

    with db_neo4j.session() as session:
        for _, fila in df_validas.iterrows():
            session.execute_write(
                neo4j.crear_relacion_unidireccional,
                "Usuario", "usuario_id", fila["usuario_id"],
                "Destino", "destino_id", fila["destino_id"],
                "VISITO"
            )

    print("✅ Relaciones VISITO creadas exitosamente en Neo4j.")


def crear_relaciones_usuarios():
    """
    Crea relaciones bidireccionales entre usuarios (usuarios_relaciones.csv).
    """
    ruta_relaciones = Path("fuentes") / "usuarios_relaciones.csv"
    df_rel = utils.lectura_csv(ruta_relaciones)

    if df_rel is None or df_rel.empty:
        print("⚠️ No se encontraron relaciones entre usuarios.")
        return

    with db_neo4j.session() as session:
        for _, fila in df_rel.iterrows():
            session.execute_write(
                neo4j.crear_relacion_bidireccional,
                "Usuario", "usuario_id", fila["usuario1"],
                "Usuario", "usuario_id", fila["usuario2"],
                fila["tipo"]
            )

    print("✅ Relaciones entre usuarios creadas exitosamente en Neo4j.")


def eliminar_amigos(usuario_id):
    """
    Elimina las relaciones AMIGO_DE de un usuario id que se pasa como parametro
    """
    
    query = """
    MATCH (u:Usuario {usuario_id: $id})-[r:AMIGO_DE]-()
    WITH count(r) as cantidad, collect(r) as relaciones
    FOREACH (rel IN relaciones | DELETE rel)
    RETURN cantidad
    """
    
    with db_neo4j.session() as session:
        resultado = session.run(query,id=usuario_id)
        cantidad = resultado.single()["cantidad"]
        return cantidad
        