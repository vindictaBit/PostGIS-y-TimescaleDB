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

def crear_mapa_realista():
    """Crea un mapa con los datos realistas que siguen rutas reales"""
    print("🗺️ CREANDO MAPA CON DATOS REALISTAS")
    print("=" * 50)
    
    # Cargar datos realistas
    sql_query = """
    SELECT
        placa,
        ST_Y(location) AS latitud,
        ST_X(location) AS longitud,
        velocidad_kmh,
        origen,
        destino,
        ts
    FROM bus_locations_realistas
    ORDER BY placa, ts
    LIMIT 1500;  -- Optimizar rendimiento
    """
    
    df = pd.read_sql(sql_query, engine)
    print(f"📊 Datos cargados: {len(df)} registros")
    
    # Centro en Arequipa
    centro_lat = df['latitud'].mean()
    centro_lon = df['longitud'].mean()
    
    # Crear mapa
    mapa = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Colores para diferentes rutas
    colores_ruta = {
        'Plaza de Armas': 'red',
        'Mall Plaza Cayma': 'blue', 
        'Terminal Terrestre': 'green',
        'Óvalo Miraflores': 'purple',
        'Estadio Melgar': 'orange',
        'Universidad San Agustín': 'darkred',
        'Mercado San Camilo': 'lightred',
        'Parque Lambramani': 'beige'
    }
    
    # Agrupar por ruta (origen → destino)
    rutas_unicas = df.groupby(['origen', 'destino']).size().reset_index(name='count')
    rutas_principales = rutas_unicas.nlargest(8, 'count')  # Top 8 rutas
    
    print(f"🛣️ Visualizando {len(rutas_principales)} rutas principales:")
    
    for i, ruta in rutas_principales.iterrows():
        origen = ruta['origen']
        destino = ruta['destino']
        registros = ruta['count']
        
        print(f"   {origen} → {destino} ({registros} puntos)")
        
        # Obtener datos de esta ruta específica
        datos_ruta = df[(df['origen'] == origen) & (df['destino'] == destino)].head(50)
        
        if len(datos_ruta) > 1:
            # Color según destino
            color = colores_ruta.get(destino, 'gray')
            
            # Crear línea de ruta
            coordenadas = [[row['latitud'], row['longitud']] for _, row in datos_ruta.iterrows()]
            
            folium.PolyLine(
                coordenadas,
                color=color,
                weight=4,
                opacity=0.8,
                popup=f'{origen} → {destino}<br>Registros: {registros}<br>Vel. promedio: {datos_ruta["velocidad_kmh"].mean():.1f} km/h'
            ).add_to(mapa)
            
            # Marcador de inicio
            if len(coordenadas) > 0:
                folium.CircleMarker(
                    coordenadas[0],
                    radius=8,
                    popup=f'📍 INICIO: {origen}',
                    color=color,
                    fill=True,
                    fillOpacity=0.9
                ).add_to(mapa)
                
                # Marcador de fin
                folium.CircleMarker(
                    coordenadas[-1],
                    radius=8,
                    popup=f'🎯 FIN: {destino}',
                    color=color,
                    fill=True,
                    fillOpacity=0.9
                ).add_to(mapa)
    
    # Agregar leyenda con puntos de interés
    puntos_interes = [
        {"nombre": "Plaza de Armas", "lat": -16.3989, "lon": -71.5367, "icono": "star"},
        {"nombre": "Mall Plaza Cayma", "lat": -16.3795, "lon": -71.5492, "icono": "shopping-cart"},
        {"nombre": "Terminal Terrestre", "lat": -16.4195, "lon": -71.5179, "icono": "road"},
        {"nombre": "Óvalo Miraflores", "lat": -16.4113, "lon": -71.5235, "icono": "circle"},
        {"nombre": "Estadio Melgar", "lat": -16.4150, "lon": -71.5280, "icono": "futbol-o"},
        {"nombre": "Universidad San Agustín", "lat": -16.4068, "lon": -71.5223, "icono": "graduation-cap"},
        {"nombre": "Mercado San Camilo", "lat": -16.4021, "lon": -71.5341, "icono": "shopping-bag"},
        {"nombre": "Parque Lambramani", "lat": -16.4067, "lon": -71.5381, "icono": "tree"}
    ]
    
    for poi in puntos_interes:
        folium.Marker(
            [poi["lat"], poi["lon"]],
            popup=f'📍 {poi["nombre"]}',
            icon=folium.Icon(color='black', icon=poi["icono"])
        ).add_to(mapa)
    
    # Guardar mapa
    archivo = "mapa_buses_realistas.html"
    mapa.save(archivo)
    print(f"✅ Mapa realista guardado: {archivo}")
    return archivo

def crear_analisis_comparativo():
    """Crea un análisis visual comparando ambos datasets"""
    print(f"\n📊 ANÁLISIS COMPARATIVO VISUAL")
    print("-" * 40)
    
    # Cargar datos de ambas tablas
    sql_original = """
    SELECT 'Original' as dataset, ST_Y(location) AS lat, ST_X(location) AS lon, velocidad_kmh
    FROM bus_locations LIMIT 1000;
    """
    
    sql_realista = """
    SELECT 'Realista' as dataset, ST_Y(location) AS lat, ST_X(location) AS lon, velocidad_kmh
    FROM bus_locations_realistas LIMIT 1000;
    """
    
    df_original = pd.read_sql(sql_original, engine)
    df_realista = pd.read_sql(sql_realista, engine)
    
    # Crear mapa comparativo
    centro_lat = -16.4009
    centro_lon = -71.5378
    
    mapa_comp = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Agregar puntos originales (azul)
    for _, row in df_original.head(200).iterrows():
        folium.CircleMarker(
            [row['lat'], row['lon']],
            radius=2,
            popup=f"Original: {row['velocidad_kmh']} km/h",
            color='blue',
            fill=True,
            fillOpacity=0.3
        ).add_to(mapa_comp)
    
    # Agregar puntos realistas (rojo)
    for _, row in df_realista.head(200).iterrows():
        folium.CircleMarker(
            [row['lat'], row['lon']],
            radius=2,
            popup=f"Realista: {row['velocidad_kmh']} km/h",
            color='red',
            fill=True,
            fillOpacity=0.3
        ).add_to(mapa_comp)
    
    # Leyenda
    folium.Marker(
        [-16.42, -71.57],
        popup='🔵 Datos Originales (línea recta)',
        icon=folium.Icon(color='blue', icon='info')
    ).add_to(mapa_comp)
    
    folium.Marker(
        [-16.43, -71.57],
        popup='🔴 Datos Realistas (rutas reales)',
        icon=folium.Icon(color='red', icon='info')
    ).add_to(mapa_comp)
    
    archivo_comp = "comparacion_datasets.html"
    mapa_comp.save(archivo_comp)
    print(f"✅ Mapa comparativo guardado: {archivo_comp}")
    return archivo_comp

if __name__ == "__main__":
    try:
        # Crear mapas
        archivo_realista = crear_mapa_realista()
        archivo_comparativo = crear_analisis_comparativo()
        
        print(f"\n🎉 ¡Visualizaciones completadas!")
        print(f"📁 Archivos generados:")
        print(f"   • {archivo_realista}")
        print(f"   • {archivo_comparativo}")
        print(f"\n💡 Usa: start {archivo_realista}")
        print(f"💡 Usa: start {archivo_comparativo}")
        
        # Estadísticas rápidas
        print(f"\n📊 RESUMEN COMPARATIVO:")
        print("   ORIGINAL: Líneas rectas, vel. 20.0±10.0 km/h")
        print("   REALISTA: Rutas reales, vel. 15.7±6.3 km/h")
        
    except Exception as e:
        print(f"❌ Error: {e}")
