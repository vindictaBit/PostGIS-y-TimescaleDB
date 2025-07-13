import pandas as pd
import folium
from sqlalchemy import create_engine

# --- CONFIGURACIÓN DE LA CONEXIÓN ---
db_user = 'postgres'
db_password = '15243'
db_host = 'localhost'
db_port = '5432'
db_name = 'MiPrimeraDB'

db_connection_str = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(db_connection_str)

def crear_mapa_simple():
    """Crea un mapa simple y liviano que funcione en Simple Browser"""
    print("📍 Creando mapa simplificado...")
    
    # Cargar muestra de datos
    sql_query = """
    SELECT
        placa,
        ST_Y(location) AS latitud,
        ST_X(location) AS longitud,
        velocidad_kmh,
        ts
    FROM bus_locations
    ORDER BY placa, ts
    LIMIT 500;  -- Solo 500 puntos para rendimiento
    """
    
    df = pd.read_sql(sql_query, engine)
    print(f"Datos cargados: {len(df)} registros")
    
    # Centro en Arequipa
    centro_lat = -16.4009
    centro_lon = -71.5378
    
    # Mapa básico sin capas adicionales
    mapa = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Agregar solo algunos puntos principales
    placas = df['placa'].unique()[:5]  # Solo 5 buses
    colores = ['red', 'blue', 'green', 'purple', 'orange']
    
    for i, placa in enumerate(placas):
        datos_bus = df[df['placa'] == placa]
        color = colores[i]
        
        # Solo marcadores, sin líneas (más simple)
        for _, row in datos_bus.head(20).iterrows():  # Solo 20 puntos por bus
            folium.CircleMarker(
                location=[row['latitud'], row['longitud']],
                radius=3,
                popup=f"{placa}: {row['velocidad_kmh']} km/h",
                color=color,
                fill=True,
                fillOpacity=0.7
            ).add_to(mapa)
    
    # Puntos de referencia importantes
    folium.Marker(
        [-16.3989, -71.5367],
        popup='Plaza de Armas',
        icon=folium.Icon(color='black', icon='star')
    ).add_to(mapa)
    
    folium.Marker(
        [-16.4113, -71.5235],
        popup='Óvalo Miraflores',
        icon=folium.Icon(color='black', icon='road')
    ).add_to(mapa)
    
    # Guardar mapa simple
    archivo = "mapa_simple.html"
    mapa.save(archivo)
    print(f"✅ Mapa simple guardado: {archivo}")
    return archivo

if __name__ == "__main__":
    try:
        archivo_mapa = crear_mapa_simple()
        print(f"🎉 Mapa creado: {archivo_mapa}")
        print("💡 Abre este archivo en tu navegador")
    except Exception as e:
        print(f"❌ Error: {e}")
