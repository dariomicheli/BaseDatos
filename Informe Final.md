# Informe final - Sistema de Gestión y Recomendación de Viajes  
**Trabajo Práctico Integrador – Bases de Datos NoSQL**  
**Autores:** Dario Micheli y Pablo Luberriaga 
**Fecha:** Octubre 2025 

## Índice  

1. [Introducción](#introducción)  
2. [Estructura del proyecto](#estructura-del-proyecto)  
3. [Arquitectura de datos](#arquitectura-de-datos)  
4. [Bases de datos y modelado de datos](#bases-de-datos-y-modelado-de-datos)  
   4.1 [MongoDB](#mongodb)  
   4.2 [Neo4j](#neo4j)  
   4.3 [Redis](#redis)  
5. [Proceso de carga](#proceso-de-carga)  
6. [Consultas implementadas](#consultas-implementadas)  
7. [Instrucciones de ejecución](#instrucciones-de-ejecución)  
8. [Análisis detallado por tecnología](#análisis-detallado-por-tecnología)  
   8.1 [MongoDB: Datos transaccionales y descriptivos](#mongodb-datos-transaccionales-y-descriptivos)  
   8.2 [Neo4j: Relaciones y recomendaciones](#neo4j-relaciones-y-recomendaciones)  
   8.3 [Redis: Cache y datos temporales](#redis-cache-y-datos-temporales)  
9. [Conclusiones y aprendizajes](#conclusiones-y-aprendizajes)   

---

## Introducción  

El presente trabajo integra tres tecnologías NoSQL — **MongoDB**, **Neo4j** y **Redis** — para desarrollar un **Sistema de Gestión y Recomendación de Viajes**.  

El objetivo principal fue modelar distintos tipos de información y operaciones que reflejan un entorno real de gestión turística:
- **MongoDB** para almacenar datos descriptivos y persistentes (usuarios, destinos, hoteles, actividades, reservas).  
- **Neo4j** para modelar relaciones y realizar recomendaciones basadas en vínculos entre usuarios y destinos.  
- **Redis** para manejar información temporal en memoria, como usuarios conectados, búsquedas recientes y reservas no confirmadas.  

El desarrollo se realizó en **Python (JupyterLab)**, integrando las tres bases mediante sus respectivos controladores (`pymongo`, `neo4j-driver`, `redis-py`) y visualizando los resultados directemente en las celdas del Notebook y en algunos puntos además con **matplotlib y Seaborn**.

---

## Estructura del proyecto 

```text
viajes-db/
│
├── notebooks/
│   ├── fuentes/
│   │   ├── usuarios.csv
│   │   ├── destinos.csv
│   │   ├── hoteles.csv
│   │   ├── actividades.csv
│   │   ├── reservas.csv
│   │   └── usuarios_relaciones.csv
│   │  
│   ├── src/
│   │   ├── mongo.py
│   │   ├── neo4j.py
│   │   ├── redis.py
│   │   └── utils.py
│   │
│   ├── Carga de Datos.ipynb
│   ├── Consultas.ipynb
│   ├── Informe Final.ipynb
│   ├── db_connections.py
│   └── constants.py
│
├── python/
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
└── README.md

```
## Arquitectura de datos

```text

           ┌──────────┐
           │  Usuario │
           └────┬─────┘
                │
      ┌─────────┴─────────┐
      │     JupyterLab    │
      │ (Capa de lógica)  │
      └───┬─────┬─────┬───┘
          │     │     │
     ┌────┘     │     └───────────┐
┌──────────┐  ┌──────────┐  ┌──────────┐
│ MongoDB  │  │  Neo4j   │  │  Redis   │
│ Document │  │ Graph DB │  │ In-memory│
└──────────┘  └──────────┘  └──────────┘
```

**¿En qué consiste esta arquitectura?**

Consiste en utilizar diferentes tipos de bases de datos dentro de una misma aplicación, eligiendo la tecnología más adecuada según la naturaleza de los datos y las operaciones requeridas. En lugar de depender de una única base para resolver todas las necesidades, se adoptó una combinación que aprovecha las fortalezas de cada modelo.

Esta estrategia refleja una tendencia moderna en el desarrollo de sistemas de información, donde la especialización y la interoperabilidad entre tecnologías generan soluciones más eficientes, escalables y cercanas a los escenarios del mundo real.

## Bases de Datos y Modelado de Datos
Para el funcionamiento del sistema se utilizan tres bases de datos NoSql con fines distintos y complementarios:

| Base de datos | Rol principal | Tipo |
|----------------|---------------|------|
| **MongoDB** | Almacena entidades y registros persistentes | Documental |
| **Neo4j** | Representa relaciones y permite recomendaciones | Grafos |
| **Redis** | Gestiona datos temporales y en caché | Clave-valor |


### MongoDB
Colecciones:
- `usuarios`
``` json
{
  "usuario_id": 1,
  "nombre": "Dario",
  "apellido": "Micheli",
  "email": "email@gmail.com",
  "telefono": "+34843181960"
}
``` 
- `destinos`
``` json
{
  "destino_id": 1,
  "provincia": "Buenos Aires",
  "ciudad": "La Plata",
  "pais": "Argentina",
  "tipo": "cultural",
  "precio_promedio": 50000
}
```
- `actividades`
``` json
{
    "actividad_id": 1,
    "nombre": "Culipatin",
    "tipo": "deportiva",
    "ciudad": "Bariloche",
    "provincia": "Rio Negro",
    "precio": 10000
}
``` 
- `hoteles`
``` json
{
 "hotel_id": 1,
 "nombre": "AMAU",
 "ciudad": "La Plata",
 "provincia": "Buenos Aires",
 "precio": 80000,
 "calificacion": 5,
 "servicios" : ["spa","wifi"]   
}
``` 
- `reservas`
``` json
{
  "reserva_id": 1,
  "usuario_id": 2,
  "destino_id": 1,
  "hotel_id":1,
  "fecha_reserva": "2025-07-01",
  "estado": "Confirmada",
  "precio_total": 90000
}

```

### Neo4j
Nodos:
- `(:Usuario {usuario_id, nombre, apellido})`

- `(:Destino {destino_id, provincia, ciudad})`

Relaciones:
- `(:Usuario)-[:VISITO]->(:Destino)`
- `(:Usuario)-[:AMIGO_DE]->(:Usuario)`

### Redis
Estructuras:
- `STRING usuario:{usuario_id}:sesion`. Ejemplo:
``` bash
Usuario:15:sesion "activa"
``` 
- `STRING busqueda:{tipo}:{parametro de busqueda}`. Ejemplo:
``` bash
busqueda:destinos:ciudad:La Rioja|tipo:Playa {'destino_id': 17, 'provincia': 'La Rioja', 'ciudad': 'La Rioja', 'pais': 'Argentina', 'tipo': 'Playa', 'precio_promedio': 138236}
```
- `HASH reserva_temp:{reserva_id}`. Ejemplo:
``` bash
reserva_temp:960: {'usuario_id': '18', 'destino_id': '17', 'fecha_reserva': '2024-12-02', 'precio_total': '130068'}
```
---

## Proceso de Carga

1. **Lectura de CSVs**  
   - Función: `utils.lectura_csv()`  
   - Descripción: Carga datos desde la carpeta `fuentes/`.

2. **Inserción en MongoDB**  
   - Función: `insertar_en_mongo()`  
   - Descripción: Crea colecciones y carga documentos en la base de datos.

3. **Creación de Nodos en Neo4j**  
   - Función: `crear_nodos_neo4j()`  
   - Descripción: Genera nodos para **usuarios** y **destinos**.

4. **Creación de Relaciones**  
   - `crear_relaciones_visito()`: Analiza reservas **confirmadas/pagadas**.  
   - `crear_relaciones_usuarios()`: Carga **amistades** y **relaciones familiares**.

5. **Carga en Redis**  
   - `guardar_usuarios_conectados()`: Selecciona 15 usuarios aleatorios.  
   - `carga_masiva_reservas_temporales()`: Guarda reservas **sin estado**.




---

## Consultas Implementadas

| N° | Descripción | Base | 
|----------------|---------------|------|
| **1.A** | Usuarios que visitaron “Bariloche” | Neo4j 
| **1.B** | Amigos de Juan que visitaron algún destino que visitó él | Neo4j 
| **1.C** | Sugerir destinos a un usuario que no haya visitado él ni sus amigos | Neo4j 
| **1.D** | Recomendar destinos basados en viajes de amigos | Neo4j 
| **1.E** | Listar los hoteles en los destinos recomendados del punto D| MongoDB 
| **1.F** | Ver las reservas en proceso | Redis 
| **1.G** | Listar los usuarios conectados actualmente | Redis 
| **1.H** | Mostrar los destinos con precio inferior a $100.000 | Redis y MongoDB 
| **1.I** | Mostrar todos los Hoteles de “Jujuy” | Redis y MongoDB 
| **1.J** | Mostrar la cantidad de hoteles de un destino que guste | Redis y MongoDB 
| **1.K** | Mostrar las actividades de “Ushuaia” del tipo “aventura” | Redis y MongoDB 
| **1.L** | reservas concretadas de cada usuario | Redis y MongoDB 
| **2.I** | Destino más visitado | MongoDB 
| **2.II** | Hotel más barato | MongoDB 
| **2.III** | Actividad más popular | MongoDB 
| **3.A** | Incrementar el precio de las actividades de Tucuman en 5% | MongoDB 
| **3.B** | Agregar al hotel id=1 el servicio de SPA | MongoDB 
| **3.C** | Eliminar el destino que desee | MongoDB y Neo4j
| **3.D** | Eliminar un usuario que desee | MongoDB y Neo4j
| **3.E** | Eliminar las relaciones AMIGO_DE para un usuario que quiera. | Neo4j

---

## Instrucciones de ejecución
Para poder ejecutar tanto el proceso de carga como las consultas mencionadas anteriormente, se deben seguir los siguientes pasos:

1. Abrir notebooks/**Carga de Datos.ipynb**
2. Ejecutar todas las celdas en orden
3. Abrir notebooks/**Consultas.ipynb**
4. Ejecutar todas las celdas en orden

---
## Análisis detallado por tecnología

La elección de cada base de datos no fue arbitraria, sino que respondió a la necesidad de resolver problemas específicos de la manera más eficiente posible. A continuación se detalla la razón de uso de cada tecnología.

### MongoDB: Datos Transaccionales y Descriptivos

MongoDB se eligió para manejar datos transaccionales y descriptivos debido a su **flexibilidad y eficiencia** en el tratamiento de documentos complejos:

- **Flexibilidad en la estructura de datos:** Dado que es Ideal para entidades como hoteles, donde los servicios pueden variar (por ejemplo: `"servicios": ["wifi", "spa", "pileta"]`). MongoDB permite que cada documento tenga atributos distintos, por lo que se pueden **agregar nuevos campos o propiedades sin alterar toda la colección**. Esto es especialmente útil cuando la información es **dinámica**, como precios, promociones o servicios que cambian constantemente.  

- **Escalabilidad Horizontal y manejo de información dinámica:** MongoDB permite crecer de manera flexible distribuyendo datos, si la base de datos crece muy rapido, se puede distribuir entre diferentes servidores sin mucho problemas 

- **Alta disponibilidad:** Gracias a su arquitectura, MongoDB garantiza un **alto rendimiento y disponibilidad**, incluso ante un gran volumen de usuarios accediendo simultáneamente a la aplicación.


### Neo4j: Relaciones y Recomendaciones
Neo4j nos permitió modelar usuarios, destinos y sus interacciones (por ejemplo, `AMIGO_DE` y `VISITO`) de manera directa, reflejando fielmente el dominio del problema. Esto nos evitó la complejidad de utilzar la union de multiples tablas si hubieramos usado una base relaciona bases relacionales, sobre todo cuando existe muchas relaciones que cambian todo el tiempo como es el caso de este trabajo. Algunas ventajas que nos dio utilzar Neo4j sobre todo en las consultas  para las relacones entre amigos y destinos fueron:

- **Rendimiento en consultas de grafos:**  
  Las bases de datos de grafos están optimizadas para explorar conexiones. Consultas como “amigos de amigos” o “destinos visitados por usuarios similares” son extremadamente rápidas, ya que Neo4j sigue punteros directos entre nodos en lugar de depender de JOINs complejos.

- **Grafos de propiedad:**  
  Neo4j permite asignar propiedades a nodos y relaciones (por ejemplo, nombre, edad, ciudad, tipo de destino), agregando valor al análisis de datos y permitiendo realizar recomendaciones más precisas y personalizadas.

- **Flexibilidad y escalabilidad:**  
  Los grafos permiten agregar nuevos nodos y relaciones sin afectar la estructura existente, lo que es útil en un sistema donde la información de usuarios, destinos que cambia constantemente.

- **Lenguaje Cypher intuitivo:**  
  Cypher facilita la expresión de patrones complejos de grafos con sintaxis declarativa, lo que simplifica la implementación de consultas como:

```cypher
MATCH (u:Usuario {usuario_id: $id})-[:AMIGO_DE]-(amigo)-[:VISITO]->(d:Destino)
WHERE NOT (u)-[:VISITO]->(d)
RETURN d.ciudad, count(*) AS amigos_visitaron
ORDER BY amigos_visitaron DESC
```

### Redis: Cache y datos temporales

Redis se utilizó principalmente en la aplicación para **gestionar datos temporales y en caché**, tales como búsquedas, usuarios conectados y consultas previamente realizadas, aprovechando su alto desempeño y sus estructuras de datos versátiles.


- **Desempeño extremadamente rápido:** 
   Al almacenar los datos en la memoria principal del servidor, Redis elimina la necesidad de acceder a discos, lo que reduce los tiempos de respuesta. Esto lo hace ideal para la gestión de sesiones de usuario, resultados de búsquedas frecuentes o reservas temporales, donde la velocidad es crítica

- **Estructuras de datos en memoria:**  
  Redis soporta múltiples estructuras como **listas ordenadas**, **sets sin orden**, **sets ordenados**, **hashes** y más. Esto permite almacenar y manipular distintos tipos de datos temporales de manera eficiente, adaptándose a las necesidades de la aplicación, algunos ejemplos son:

  - `STRING usuario:{usuario_id}:sesion` → controla el estado de sesión de los usuarios conectados.
  - `HASH reserva_temp:{reserva_id}` → gestiona reservas sin confirmar.
  - `STRING busqueda:{tipo}:{parametro}` → almacena resultados de consultas frecuentes, como destinos populares.

- **Compatibilidad con múltiples lenguajes:**  
   Redis es compatible con diversos lenguajes de programación, incluido Python, lo que facilita su integración en la aplicación y en distintos módulos de procesamiento de datos.

- **complementa a MongoDB y Neo4j** 
   En este proyecto, Redis se utilizó como un complemento que proporciona acceso rápido a datos temporales y en caché, optimizando el rendimiento sin reemplazar las bases de datos principales.  

---
## Conclusiones y aprendizajes

El desarrollo de este proyecto permitió integrar tres tecnologías NoSQL con propósitos complementarios, demostrando el valor de la arquitectura polyglot persistence. **MongoDB** resultó fundamental para gestionar información estructurada y flexible de usuarios, destinos y reservas; **Neo4j** facilitó representar y consultar relaciones complejas de manera natural, simplificando la generación de recomendaciones basadas en vínculos entre personas y lugares; y **Redis** aportó velocidad y eficiencia para manejar datos temporales como búsquedas, sesiones y reservas en proceso. 

La combinación de estas bases dentro de un mismo entorno de trabajo evidenció cómo cada tecnología resuelve un aspecto diferente del problema: persistencia, conocimiento y tiempo real. En conjunto, el proyecto fortaleció la comprensión sobre cómo elegir la herramienta adecuada según el tipo y comportamiento de los datos, y mostró que la integración inteligente de distintos modelos permite construir soluciones más escalables, dinámicas y cercanas a los escenarios reales del mundo digital actual.
