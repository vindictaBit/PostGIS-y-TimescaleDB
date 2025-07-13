import pandas as pd
import numpy as np
from datetime import datetime, timedelta

NUM_BUSES = 15
PUNTOS_POR_BUS = 400
FECHA_INICIO = "2025-07-12 06:00:00"
ARCHIVO_SALIDA = "datos_buses_aqp.csv"

RUTA_AQP = {
    "start_lat": -16.3795, "start_lon": -71.5492,
    "end_lat": -16.3989, "end_lon": -71.5367
}

def get_velocidad_segun_hora(hora):
    """Calcula velocidad según hora del día considerando tráfico."""
    if (7 <= hora <= 9) or (13 <= hora <= 14) or (17 <= hora <= 20):
        return np.random.uniform(8, 22)
    else:
        return np.random.uniform(25, 45)

datos_generados = []
print("Generando datos de buses...")

for i in range(NUM_BUSES):
    placa = f"V{np.random.randint(100, 999)}-{chr(np.random.randint(65, 91))}{chr(np.random.randint(65, 91))}"
    
    lat_actual = RUTA_AQP["start_lat"] + np.random.normal(0, 0.005)
    lon_actual = RUTA_AQP["start_lon"] + np.random.normal(0, 0.005)
    timestamp_actual = datetime.fromisoformat(FECHA_INICIO) + timedelta(minutes=np.random.randint(0, 50))
    
    dir_lat = (RUTA_AQP["end_lat"] - lat_actual) / PUNTOS_POR_BUS
    dir_lon = (RUTA_AQP["end_lon"] - lon_actual) / PUNTOS_POR_BUS

    for _ in range(PUNTOS_POR_BUS):
        intervalo_segundos = np.random.randint(25, 50)
        timestamp_actual += timedelta(seconds=intervalo_segundos)
        
        velocidad_kmh = get_velocidad_segun_hora(timestamp_actual.hour)
        
        lat_actual += dir_lat + np.random.normal(0, 0.0001)
        lon_actual += dir_lon + np.random.normal(0, 0.0001)

        datos_generados.append({
            "placa": placa,
            "latitud": round(lat_actual, 6),
            "longitud": round(lon_actual, 6),
            "velocidad_kmh": int(velocidad_kmh),
            "timestamp": timestamp_actual.strftime("%Y-%m-%d %H:%M:%S")
        })

df_final = pd.DataFrame(datos_generados)
df_final.to_csv(ARCHIVO_SALIDA, index=False)

print(f"Archivo generado: {ARCHIVO_SALIDA} con {len(df_final)} registros.")
print(df_final.head())