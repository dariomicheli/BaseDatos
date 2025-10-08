import pandas as pd
import random
from faker import Faker
import os

fake = Faker('es_ES')
Faker.seed(42)
random.seed(42)

# -----------------------------
# Configuración de datos Argentina
# -----------------------------
provincias_arg = ["Buenos Aires", "Córdoba", "Santa Fe", "Mendoza", "Tucumán", "Salta", "Neuquén", "Chubut"]
ciudades_arg = {
    "Buenos Aires": ["La Plata", "Mar del Plata", "Bahía Blanca"],
    "Córdoba": ["Córdoba", "Villa Carlos Paz", "Río Cuarto"],
    "Santa Fe": ["Rosario", "Santa Fe", "Rafaela"],
    "Mendoza": ["Mendoza", "San Rafael"],
    "Tucumán": ["San Miguel de Tucumán", "Tafí del Valle"],
    "Salta": ["Salta", "Cafayate"],
    "Neuquén": ["Neuquén", "San Martín de los Andes"],
    "Chubut": ["Puerto Madryn", "Trelew"]
}

tipos_destino = ["Cultural", "Playa", "Montaña", "Aventura", "Relax"]
tipos_actividad = ["aventura", "cultural", "gastronómica", "relax", "deportiva"]
servicios_posibles = ["wifi", "spa", "pileta", "desayuno", "gimnasio", "restaurant"]
estados_reserva = ["Confirmada", "Pagada", "Pendiente", "Cancelada",""]

# Cantidades
n_usuarios = 500
n_destinos = 50
n_hoteles = 100
n_actividades = 120
n_reservas = 200

# -----------------------------
# Generar Usuarios
# -----------------------------
usuarios = []
for i in range(1, n_usuarios+1):
    usuarios.append({
        "usuario_id": i,
        "nombre": fake.first_name(),
        "apellido": fake.last_name(),
        "email": fake.unique.email(),
        "telefono": fake.phone_number()
    })

# -----------------------------
# Generar Destinos (Argentina)
# -----------------------------
destinos = []
for i in range(1, n_destinos+1):
    provincia = random.choice(provincias_arg)
    ciudad = random.choice(ciudades_arg[provincia])
    destinos.append({
        "destino_id": i,
        "ciudad": ciudad,
        "pais": "Argentina",
        "tipo": random.choice(tipos_destino),
        "precio_promedio": random.randint(50000, 200000)
    })

# -----------------------------
# Generar Hoteles
# -----------------------------
hoteles = []
for i in range(1, n_hoteles+1):
    destino = random.choice(destinos)
    hoteles.append({
        "hotel_id": i,
        "nombre": f"{fake.company()} Hotel",
        "ciudad": destino["ciudad"],
        "precio": random.randint(40000, 250000),
        "calificacion": random.randint(1,5),
        "servicios": ";".join(random.sample(servicios_posibles, random.randint(2,4)))
    })

# -----------------------------
# Generar Actividades
# -----------------------------
actividades = []
for i in range(1, n_actividades+1):
    destino = random.choice(destinos)
    actividades.append({
        "actividad_id": i,
        "nombre": fake.catch_phrase(),
        "tipo": random.choice(tipos_actividad),
        "ciudad": destino["ciudad"],
        "precio": random.randint(20000, 80000)
    })

# -----------------------------
# Generar Reservas
# -----------------------------
reservas = []
for i in range(1, n_reservas+1):
    usuario = random.choice(usuarios)
    destino = random.choice(destinos)
    reservas.append({
        "reserva_id": i,
        "usuario_id": usuario["usuario_id"],
        "destino_id": destino["destino_id"],
        "fecha_reserva": fake.date_between(start_date="-1y", end_date="+6m").isoformat(),
        "estado": random.choice(estados_reserva),
        "precio_total": destino["precio_promedio"]
    })

# -----------------------------
# Generar Relaciones entre Usuarios con límites
# -----------------------------
from collections import defaultdict

max_amigos = 3
max_familiares = 2
n_usuarios = 500

relaciones = []
amigos_count = defaultdict(int)
familiares_count = defaultdict(int)
pares_existentes = set()  # para evitar duplicados

while len(relaciones) < 300:  # intentamos generar 300 relaciones
    usuario1 = random.randint(1, n_usuarios)
    usuario2 = random.randint(1, n_usuarios)
    
    if usuario1 == usuario2:
        continue
    
    # Crear un identificador único para el par (sin importar el orden)
    par = tuple(sorted((usuario1, usuario2)))
    if par in pares_existentes:
        continue

    # Elegir tipo de relación al azar
    tipo_relacion = random.choice(["amigo_de", "familiar_de"])
    
    # Validar límites
    if tipo_relacion == "amigo_de":
        if amigos_count[usuario1] >= max_amigos or amigos_count[usuario2] >= max_amigos:
            continue
        # Validar que no sean familiares
        if familiares_count[usuario1] > 0 and familiares_count[usuario2] > 0:
            continue
        amigos_count[usuario1] += 1
        amigos_count[usuario2] += 1
    else:  # familiar_de
        if familiares_count[usuario1] >= max_familiares or familiares_count[usuario2] >= max_familiares:
            continue
        # Validar que no sean amigos
        if amigos_count[usuario1] > 0 and amigos_count[usuario2] > 0:
            continue
        familiares_count[usuario1] += 1
        familiares_count[usuario2] += 1

    # Agregar relación
    relaciones.append({
        "usuario1": usuario1,
        "usuario2": usuario2,
        "tipo": tipo_relacion
    })
    pares_existentes.add(par)

# -----------------------------
# Guardar CSV
# -----------------------------
carpeta_destino = "notebooks/fuentes"
os.makedirs(carpeta_destino, exist_ok=True) 



# -----------------------------
# Guardar CSV en notebooks/fuentes
# -----------------------------
pd.DataFrame(usuarios).to_csv(f"{carpeta_destino}/usuarios.csv", index=False, encoding="utf-8")
pd.DataFrame(destinos).to_csv(f"{carpeta_destino}/destinos.csv", index=False, encoding="utf-8")
pd.DataFrame(hoteles).to_csv(f"{carpeta_destino}/hoteles.csv", index=False, encoding="utf-8")
pd.DataFrame(actividades).to_csv(f"{carpeta_destino}/actividades.csv", index=False, encoding="utf-8")
pd.DataFrame(reservas).to_csv(f"{carpeta_destino}/reservas.csv", index=False, encoding="utf-8")
pd.DataFrame(relaciones).to_csv(f"{carpeta_destino}/usuarios_relaciones.csv", index=False, encoding="utf-8")