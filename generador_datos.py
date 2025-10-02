import pandas as pd
import random
from faker import Faker

fake = Faker('es_ES')

# Cantidades de registros
n_destinos = 50
n_hoteles = 100
n_actividades = 120
n_reservas = 200

# -----------------------------
# Generar Destinos
# -----------------------------
tipos_destino = ["Cultural", "Playa", "Montaña", "Aventura", "Relax"]
paises = ["Argentina", "España", "Italia",
          "México", "Chile", "Brasil", "Francia"]

destinos = []
for i in range(1, n_destinos+1):
    ciudad = fake.city()
    destinos.append({
        "destino_id": i,
        "ciudad": ciudad,
        "pais": random.choice(paises),
        "tipo": random.choice(tipos_destino),
        "precio_promedio": random.randint(50000, 200000)
    })

# -----------------------------
# Generar Hoteles
# -----------------------------
servicios_posibles = ["wifi", "spa", "pileta",
                      "desayuno", "gimnasio", "restaurant"]
hoteles = []
for i in range(1, n_hoteles+1):
    ciudad = random.choice(destinos)["ciudad"]
    hoteles.append({
        "hotel_id": i,
        "nombre": fake.company(),
        "ciudad": ciudad,
        "precio": random.randint(40000, 250000),
        "calificacion": random.randint(1, 5),
        # separado por ;
        "servicios": ";".join(random.sample(servicios_posibles, random.randint(2, 4)))
    })

# -----------------------------
# Generar Actividades
# -----------------------------
tipos_actividad = ["aventura", "cultural",
                   "gastronómica", "relax", "deportiva"]
actividades = []
for i in range(1, n_actividades+1):
    ciudad = random.choice(destinos)["ciudad"]
    actividades.append({
        "actividad_id": i,
        "nombre": fake.catch_phrase(),
        "tipo": random.choice(tipos_actividad),
        "ciudad": ciudad,
        "precio": random.randint(20000, 80000)
    })

# -----------------------------
# Generar Reservas
# -----------------------------
estados_reserva = ["Confirmada", "Pagada", "Pendiente", "Cancelada"]
reservas = []
for i in range(1, n_reservas+1):
    destino = random.choice(destinos)
    reservas.append({
        "reserva_id": i,
        "usuario_id": random.randint(1, 500),
        "destino_id": destino["destino_id"],
        "fecha_reserva": fake.date_between(start_date="-1y", end_date="+6m").isoformat(),
        "estado": random.choice(estados_reserva),
        "precio_total": destino["precio_promedio"]
    })

# -----------------------------
# Guardar en CSV
# -----------------------------
pd.DataFrame(destinos).to_csv("destinos.csv", index=False, encoding="utf-8")
pd.DataFrame(hoteles).to_csv("hoteles.csv", index=False, encoding="utf-8")
pd.DataFrame(actividades).to_csv(
    "actividades.csv", index=False, encoding="utf-8")
pd.DataFrame(reservas).to_csv("reservas.csv", index=False, encoding="utf-8")

print("Archivos generados: destinos.csv, hoteles.csv, actividades.csv, reservas.csv")
