import pandas as pd
import random
from faker import Faker
import os
from collections import defaultdict

# -----------------------------
# Configuración
# -----------------------------
fake = Faker('es_ES')
Faker.seed(42)
random.seed(42)

provincias_arg = ["Buenos Aires", "Córdoba", "Santa Fe", "Mendoza", "Tucumán", "Salta", "Neuquén", "Chubut"]
ciudades_arg = {
    "Buenos Aires": ["La Plata"],
    "Córdoba": ["Córdoba"],
    "Santa Fe": ["Rosario"],
    "Mendoza": ["Mendoza"],
    "Tucumán": ["San Miguel de Tucumán"],
    "Salta": ["Salta"],
    "Neuquén": ["Neuquén"],
    "Chubut": ["Puerto Madryn"]
}

tipos_destino = ["Cultural", "Playa", "Montaña", "Aventura", "Relax"]
tipos_actividad = ["aventura", "cultural", "gastronómica", "relax", "deportiva"]
servicios_posibles = ["wifi", "spa", "pileta", "desayuno", "gimnasio", "restaurant"]
estados_reserva = ["Confirmada", "Pagada", "Pendiente", "Cancelada",""]

# Cantidades
n_usuarios = 50
n_destinos = 20
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
usuario_ids = [u["usuario_id"] for u in usuarios]

# -----------------------------
# Generar Destinos
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
destino_ids = [d["destino_id"] for d in destinos]

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

# Asegurar al menos una reserva por usuario
for usuario_id in usuario_ids:
    destino_id = random.choice(destino_ids)
    destino_precio = next(d["precio_promedio"] for d in destinos if d["destino_id"] == destino_id)
    reservas.append({
        "reserva_id": len(reservas)+1,
        "usuario_id": usuario_id,
        "destino_id": destino_id,
        "fecha_reserva": fake.date_between(start_date="-1y", end_date="+6m").isoformat(),
        "estado": random.choice(estados_reserva),
        "precio_total": destino_precio
    })

# Agregar reservas adicionales hasta n_reservas
while len(reservas) < n_reservas:
    usuario_id = random.choice(usuario_ids)
    destino_id = random.choice(destino_ids)
    destino_precio = next(d["precio_promedio"] for d in destinos if d["destino_id"] == destino_id)
    reservas.append({
        "reserva_id": len(reservas)+1,
        "usuario_id": usuario_id,
        "destino_id": destino_id,
        "fecha_reserva": fake.date_between(start_date="-1y", end_date="+6m").isoformat(),
        "estado": random.choice(estados_reserva),
        "precio_total": destino_precio
    })

# -----------------------------
# Generar Relaciones
# -----------------------------
max_amigos = 5
max_familiares = 2
relaciones = []
amigos_count = defaultdict(int)
familiares_count = defaultdict(int)
pares_existentes = set()

while len(relaciones) < 300:
    usuario1, usuario2 = random.sample(usuario_ids, 2)
    par = tuple(sorted((usuario1, usuario2)))
    if par in pares_existentes:
        continue

    tipo_relacion = random.choice(["AMIGO_DE", "FAMILIAR_DE"])

    if tipo_relacion == "AMIGO_DE":
        if amigos_count[usuario1] >= max_amigos or amigos_count[usuario2] >= max_amigos:
            continue
        amigos_count[usuario1] += 1
        amigos_count[usuario2] += 1
    else:
        if familiares_count[usuario1] >= max_familiares or familiares_count[usuario2] >= max_familiares:
            continue
        familiares_count[usuario1] += 1
        familiares_count[usuario2] += 1

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

pd.DataFrame(usuarios).to_csv(f"{carpeta_destino}/usuarios.csv", index=False, encoding="utf-8")
pd.DataFrame(destinos).to_csv(f"{carpeta_destino}/destinos.csv", index=False, encoding="utf-8")
pd.DataFrame(hoteles).to_csv(f"{carpeta_destino}/hoteles.csv", index=False, encoding="utf-8")
pd.DataFrame(actividades).to_csv(f"{carpeta_destino}/actividades.csv", index=False, encoding="utf-8")
pd.DataFrame(reservas).to_csv(f"{carpeta_destino}/reservas.csv", index=False, encoding="utf-8")
pd.DataFrame(relaciones).to_csv(f"{carpeta_destino}/usuarios_relaciones.csv", index=False, encoding="utf-8")
