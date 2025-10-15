import pandas as pd

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

def consulta(db, query):
    """
    Ejecuta una query en Neo4j y devuelve los resultados como un DataFrame.

    Parámetros:
        db: objeto de conexión a Neo4j (db_neo4j)
        query: string con la consulta Cypher

    Retorna:
        pd.DataFrame con los resultados
    """
    with db.session() as session:
        resultados = session.run(query)
        data = [record.data() for record in resultados]
    return pd.DataFrame(data)


