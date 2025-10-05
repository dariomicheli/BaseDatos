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


def crear_relacion(tx, nodo_origen, campo_origen, valor_origen,
                   nodo_destino, campo_destino, valor_destino,
                   tipo_relacion):
    query = f"""
    MATCH (a:{nodo_origen} {{{campo_origen}: $valor_origen}})
    MATCH (b:{nodo_destino} {{{campo_destino}: $valor_destino}})
    MERGE (a)-[r:{tipo_relacion}]->(b)
    RETURN a, b, r
    """
    return tx.run(query, valor_origen=valor_origen, valor_destino=valor_destino).single()
