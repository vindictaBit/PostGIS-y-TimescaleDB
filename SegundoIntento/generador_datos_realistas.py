import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import osmnx as ox
import networkx as nx
from geopy.distance import geodesic

NUM_BUSES = 15
PUNTOS_POR_BUS = 400
FECHA_INICIO = "2025-07-12 06:00:00"
ARCHIVO_SALIDA = "datos_buses_aqp_realistas.csv"

print("Generador de datos realistas para buses de Arequipa")

def descargar_red_calles_arequipa():
    """Descarga la red de calles de Arequipa desde OpenStreetMap."""
    print("Descargando red de calles...")
    
    area_arequipa = "Arequipa, Peru"
    
    try:
        G = ox.graph_from_place(area_arequipa, network_type='drive')
        print(f"Red descargada: {len(G.nodes)} nodos, {len(G.edges)} calles")
        return G
    except Exception as e:
        print(f"Error descargando red: {e}")
        print("Intentando con coordenadas específicas...")
        
        bbox_arequipa = (-16.45, -16.35, -71.57, -71.50)
        G = ox.graph_from_bbox(bbox=bbox_arequipa, network_type='drive')
        print(f"Red descargada: {len(G.nodes)} nodos, {len(G.edges)} calles")
        return G

def encontrar_nodos_cercanos(G, lat, lon):
    """Encuentra el nodo más cercano en la red de calles."""
    return ox.nearest_nodes(G, lon, lat)

def generar_ruta_realista(G, nodo_inicio, nodo_fin):
    """Genera una ruta siguiendo las calles reales."""
    try:
        ruta = nx.shortest_path(G, nodo_inicio, nodo_fin, weight='length')
        return ruta
    except nx.NetworkXNoPath:
        print("No se encontró ruta directa, usando ruta básica...")
        return [nodo_inicio, nodo_fin]

def get_velocidad_segun_hora_y_calle(hora, tipo_calle="residential"):
    """Calcula velocidad según hora y tipo de calle."""
    velocidades_base = {
        "residential": (15, 35),
        "secondary": (20, 45),
        "primary": (25, 50),
        "trunk": (30, 60),
        "motorway": (50, 80)
    }
    
    vel_min, vel_max = velocidades_base.get(tipo_calle, (15, 35))
    
    if (7 <= hora <= 9) or (13 <= hora <= 14) or (17 <= hora <= 20):
        factor_congestion = np.random.uniform(0.4, 0.6)
    elif (11 <= hora <= 12) or (15 <= hora <= 16):
        factor_congestion = np.random.uniform(0.7, 0.8)
    else:
        factor_congestion = np.random.uniform(0.8, 1.0)
    
    velocidad_final = np.random.uniform(vel_min, vel_max) * factor_congestion
    return max(5, int(velocidad_final))

def generar_datos_realistas():
    """Genera datos siguiendo calles reales."""
    
    G = descargar_red_calles_arequipa()
    
    puntos_interes = [
        {"nombre": "Plaza de Armas", "lat": -16.3989, "lon": -71.5367},
        {"nombre": "Mall Plaza Cayma", "lat": -16.3795, "lon": -71.5492},
        {"nombre": "Terminal Terrestre", "lat": -16.4195, "lon": -71.5179},
        {"nombre": "Óvalo Miraflores", "lat": -16.4113, "lon": -71.5235},
        {"nombre": "Estadio Melgar", "lat": -16.4150, "lon": -71.5280},
        {"nombre": "Universidad San Agustín", "lat": -16.4068, "lon": -71.5223},
        {"nombre": "Mercado San Camilo", "lat": -16.4021, "lon": -71.5341},
        {"nombre": "Parque Lambramani", "lat": -16.4067, "lon": -71.5381}
    ]
    
    datos_generados = []
    print(f"Generando datos para {NUM_BUSES} buses...")
    
    for i in range(NUM_BUSES):
        print(f"Procesando bus {i+1}/{NUM_BUSES}")
        
        placa = f"V{np.random.randint(100, 999)}-{chr(np.random.randint(65, 91))}{chr(np.random.randint(65, 91))}"
        
        origen = np.random.choice(puntos_interes)
        destino = np.random.choice([p for p in puntos_interes if p != origen])
        
        print(f"   Ruta: {origen['nombre']} -> {destino['nombre']}")
        
        nodo_origen = encontrar_nodos_cercanos(G, origen['lat'], origen['lon'])
        nodo_destino = encontrar_nodos_cercanos(G, destino['lat'], destino['lon'])
        
        ruta_nodos = generar_ruta_realista(G, nodo_origen, nodo_destino)
        
        coordenadas_ruta = []
        for nodo in ruta_nodos:
            lat = G.nodes[nodo]['y']
            lon = G.nodes[nodo]['x']
            coordenadas_ruta.append((lat, lon))
        
        puntos_interpolados = interpolar_ruta(coordenadas_ruta, PUNTOS_POR_BUS)
        
        timestamp_actual = datetime.fromisoformat(FECHA_INICIO) + timedelta(minutes=np.random.randint(0, 60))
        
        for j, (lat, lon) in enumerate(puntos_interpolados):
            intervalo_segundos = np.random.randint(30, 60)
            timestamp_actual += timedelta(seconds=intervalo_segundos)
            
            velocidad = get_velocidad_segun_hora_y_calle(timestamp_actual.hour)
            
            datos_generados.append({
                "placa": placa,
                "latitud": round(lat, 6),
                "longitud": round(lon, 6),
                "velocidad_kmh": velocidad,
                "timestamp": timestamp_actual.strftime("%Y-%m-%d %H:%M:%S"),
                "origen": origen['nombre'],
                "destino": destino['nombre']
            })
    
    return datos_generados

def interpolar_ruta(coordenadas, num_puntos_deseados):
    """Interpola puntos entre coordenadas para crear una ruta más densa"""
    if len(coordenadas) < 2:
        return coordenadas
    
def interpolar_ruta(coordenadas, num_puntos_deseados):
    """Interpola puntos entre coordenadas para crear una ruta más densa."""
    if len(coordenadas) < 2:
        return coordenadas
    
    puntos_interpolados = []
    puntos_por_segmento = max(1, num_puntos_deseados // (len(coordenadas) - 1))
    
    for i in range(len(coordenadas) - 1):
        lat1, lon1 = coordenadas[i]
        lat2, lon2 = coordenadas[i + 1]
        
        for j in range(puntos_por_segmento):
            factor = j / puntos_por_segmento
            lat_interp = lat1 + (lat2 - lat1) * factor
            lon_interp = lon1 + (lon2 - lon1) * factor
            
            lat_interp += np.random.normal(0, 0.0001)
            lon_interp += np.random.normal(0, 0.0001)
            
            puntos_interpolados.append((lat_interp, lon_interp))
    
    puntos_interpolados.append(coordenadas[-1])
    
    return puntos_interpolados[:num_puntos_deseados]

if __name__ == "__main__":
    try:
        print("Iniciando generación de datos realistas...")
        
        datos = generar_datos_realistas()
        
        df_final = pd.DataFrame(datos)
        df_final.to_csv(ARCHIVO_SALIDA, index=False)
        
        print(f"Archivo generado: {ARCHIVO_SALIDA} con {len(df_final)} registros")
        print(f"Resumen:")
        print(f"  - {df_final['placa'].nunique()} buses únicos")
        print(f"  - {df_final['origen'].nunique()} puntos de origen")
        print(f"  - {df_final['destino'].nunique()} puntos de destino")
        print(f"  - Velocidad promedio: {df_final['velocidad_kmh'].mean():.1f} km/h")
        
        print("Primeros registros:")
        print(df_final.head())
        
    except Exception as e:
        print(f"Error: {e}")
        print("Verificar conexión a internet para descargar mapas")
        print("Instalar dependencias: pip install osmnx networkx geopy")
