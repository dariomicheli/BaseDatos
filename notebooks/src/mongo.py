from db_connections import client
from src.utils import lectura_csv
from pprint import pprint
import pandas as pd


def coleccion_existe(db, nombre_coleccion):
    """
    Verifica si una colección existe en la base de datos.

    Parámetros:
    - db: objeto pymongo.database.Database
    - nombre_coleccion: nombre de la colección a verificar (string)

    Retorna:
    - True si existe, False si no
    """
    return nombre_coleccion in db.list_collection_names()  


def obtener_coleccion(nombre_base, nombre_coleccion):
    """
    Devuelve el objeto Collection.
    """
    db = client[nombre_base]
    if not coleccion_existe(db, nombre_coleccion):
        raise KeyError(
            f"La colección '{nombre_coleccion}' no existe en la base '{nombre_base}'.")
    return db[nombre_coleccion]


def crear_coleccion(nombre_base, nombre_coleccion, recrear=False):
    """
    Crea una colección dentro de la base de datos especificada. Si la misma ya existe, la elimina.

    Parametros:
        nombre_base:nombre de la base de datos dentro de mongoDB
        nombre_coleccion: nombre de la colección a crear
        recrear: si es True, borra la coleccion. 
    Retorna:
        coleccion: 
    """
    db = client[nombre_base]

    if coleccion_existe(db, nombre_coleccion):
        if recrear:
            db.drop_collection(nombre_coleccion)
        else:
            return db[nombre_coleccion]

    coleccion = db.create_collection(nombre_coleccion)
    return coleccion


def insertar_muchos_coleccion(nombre_base, nombre_coleccion, datos, ordenado=False):
    """
    Inserta varios datos en una colección.

    Parametros:
        nombre_coleccion: nombre de la colección a ingresar los datos.
        datos: diccionario con las datos que se quieren incluir.
    """

    if datos is None:
        raise ValueError("El parámetro 'datos' no puede ser None.")
    lista_datos = list(datos)
    if not lista_datos:
        print("⚠️ El DataFrame está vacío, no se insertaron datos.")
        return None

    db = client[nombre_base]
    coleccion = db[nombre_coleccion]

    try:
        resultado = coleccion.insert_many(lista_datos, ordered=ordenado)
        print(
            f"✅ Se insertaron {len(resultado.inserted_ids)} documentos en '{coleccion.name}'.")
        return resultado
    except Exception as e:
        print(f"❌ Error inesperado: {type(e).__name__} - {e}")


def obtener_cursor(nombre_base, nombre_coleccion, limite=None, filtro=None, proyeccion=None):
    """
    Retorna un cursor para la consulta.

    Parametros:
        nombre_base:
        nombre_colección: colección de la cual se quieren obtener datos
        limite (opcional): limite de registros que desean obtener.
        filtro (opcional):
        proyeccion (opcional):
    Retorna
        cursor: datos de la consulta a la colección
    """
    db = client[nombre_base]
    if not coleccion_existe(db, nombre_coleccion):
        raise KeyError(
            f"La colección '{nombre_coleccion}' no existe en la base '{nombre_base}'.")

    coleccion = db[nombre_coleccion]
    cursor = coleccion.find(filter=filtro or {}, projection=proyeccion)
    if limite is not None:
        cursor = cursor.limit(limite)
    return cursor


def imprimir_cursor(cursor, campos=None, maximo=None):
    """
    Imprime documentos de un cursor MongoDB con campos opcionales.

    Parámetros:
    - cursor: objeto pymongo.cursor.Cursor
    - campos (opcional): lista de campos a mostrar (opcional)
    - maximo (opcional): 
    """
    contar=0
    for doc in cursor:
        if campos:
            doc_filtrado= {k: doc.get(k) for k in campos}
            pprint(doc_filtrado)
        else:
            pprint(doc)
        contar+=1
        if maximo is not None and contar>=maximo:
            break
    if contar==0:
        print("⚠️ No se encontraron documentos.")       

def contar_documentos(nombre_base, nombre_coleccion):
    """
    Devuelve la cantidad de documentos de una coleccion
    """
    db = client[nombre_base]
    coleccion = db[nombre_coleccion]
    
    if not coleccion_existe(db, nombre_coleccion):
        raise KeyError(
            f"La colección '{nombre_coleccion}' no existe en la base '{nombre_base}'.")
    
    return coleccion.count_documents({})

def cargar_df_a_coleccion(df, nombre_base, nombre_coleccion,ordenado=False):
    """
    Lee CSV usando lectura_csv y lo inserta en la colección.
    Devuelve el InsertManyResult o None si no se insertó nada.

    Parametros:
        ruta: dirección del archivo csv.
        nombre_coleccion: nombre de la colección a guardar
        ordenado (opcional):
    """ 
    if df is None or df.empty:
        return None

    # Convertir a diccionario
    datos = df.to_dict(orient="records")

    return insertar_muchos_coleccion(nombre_base, nombre_coleccion, datos, ordenado)
