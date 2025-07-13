import pandas as pd
import folium
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- CONFIGURACIÓN DE LA CONEXIÓN ---
db_user = 'postgres'
db_password = '15243'
db_host = 'localhost'
db_port = '5432'
db_name = 'MiPrimeraDB'

db_connection_str = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(db_connection_str)

def crear_mapa_interactivo():
    """Crea un mapa interactivo con Folium mostrando las rutas de buses"""
    print("Cargando datos desde la base de datos...")
    
    # Consulta para obtener datos con timestamps
    sql_query = """
    SELECT
        placa,
        ST_Y(location) AS latitud,
        ST_X(location) AS longitud,
        velocidad_kmh,
        ts,
        EXTRACT(HOUR FROM ts) AS hora
    FROM bus_locations
    ORDER BY placa, ts
    LIMIT 2000;  -- Limitamos para mejor rendimiento
    """
    
    df = pd.read_sql(sql_query, engine)
    print(f"Se cargaron {len(df)} registros para visualización.")
    
    # Centro del mapa en Arequipa
    centro_lat = df['latitud'].mean()
    centro_lon = df['longitud'].mean()
    
    # Crear mapa base
    mapa = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Agregar capas adicionales de mapas
    folium.TileLayer(
        'Stamen Terrain',
        attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'
    ).add_to(mapa)
    folium.TileLayer(
        'CartoDB positron',
        attr='&copy; OpenStreetMap contributors &copy; CARTO'
    ).add_to(mapa)
    
    # Colores únicos por bus
    colores = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
               'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 
               'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen']
    
    placas_unicas = df['placa'].unique()
    
    for i, placa in enumerate(placas_unicas[:10]):  # Solo primeros 10 buses
        datos_bus = df[df['placa'] == placa].sort_values('ts')
        color = colores[i % len(colores)]
        
        # Crear la ruta del bus
        coordenadas = [[row['latitud'], row['longitud']] for _, row in datos_bus.iterrows()]
        
        # Línea de ruta
        folium.PolyLine(
            coordenadas,
            color=color,
            weight=3,
            opacity=0.8,
            popup=f'Ruta Bus {placa}'
        ).add_to(mapa)
        
        # Punto inicial
        if len(coordenadas) > 0:
            folium.Marker(
                coordenadas[0],
                popup=f'INICIO - {placa}',
                icon=folium.Icon(color=color, icon='play')
            ).add_to(mapa)
            
            # Punto final
            folium.Marker(
                coordenadas[-1],
                popup=f'FIN - {placa}',
                icon=folium.Icon(color=color, icon='stop')
            ).add_to(mapa)
    
    # Agregar puntos de interés de Arequipa
    puntos_interes = [
        {"nombre": "Plaza de Armas", "lat": -16.3989, "lon": -71.5367, "icono": "star"},
        {"nombre": "Mall Plaza Cayma", "lat": -16.3795, "lon": -71.5492, "icono": "shopping-cart"},
        {"nombre": "Óvalo Miraflores", "lat": -16.4113, "lon": -71.5235, "icono": "road"},
        {"nombre": "Estadio Melgar", "lat": -16.4150, "lon": -71.5280, "icono": "futbol-o"},
        {"nombre": "Universidad San Agustín", "lat": -16.4068, "lon": -71.5223, "icono": "graduation-cap"}
    ]
    
    for poi in puntos_interes:
        folium.Marker(
            [poi["lat"], poi["lon"]],
            popup=f'📍 {poi["nombre"]}',
            icon=folium.Icon(color='black', icon=poi["icono"])
        ).add_to(mapa)
    
    # Control de capas
    folium.LayerControl().add_to(mapa)
    
    # Guardar mapa
    archivo_mapa = "mapa_buses_arequipa.html"
    mapa.save(archivo_mapa)
    print(f"✅ Mapa guardado como '{archivo_mapa}'")
    return archivo_mapa

def crear_dashboard_velocidades():
    """Crea un dashboard interactivo con análisis de velocidades"""
    print("Creando dashboard de velocidades...")
    
    sql_query = """
    SELECT
        placa,
        ST_Y(location) AS latitud,
        ST_X(location) AS longitud,
        velocidad_kmh,
        EXTRACT(HOUR FROM ts) AS hora,
        EXTRACT(DOW FROM ts) AS dia_semana,
        ts
    FROM bus_locations;
    """
    
    df = pd.read_sql(sql_query, engine)
    
    # Crear subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Velocidad por Hora del Día', 'Distribución de Velocidades',
                       'Velocidad por Ubicación', 'Velocidad por Bus'),
        specs=[[{"type": "scatter"}, {"type": "histogram"}],
               [{"type": "scatter"}, {"type": "bar"}]]
    )
    
    # 1. Velocidad promedio por hora
    vel_por_hora = df.groupby('hora')['velocidad_kmh'].mean().reset_index()
    fig.add_trace(
        go.Scatter(x=vel_por_hora['hora'], y=vel_por_hora['velocidad_kmh'],
                  mode='lines+markers', name='Vel. Promedio'),
        row=1, col=1
    )
    
    # 2. Histograma de velocidades
    fig.add_trace(
        go.Histogram(x=df['velocidad_kmh'], nbinsx=20, name='Distribución'),
        row=1, col=2
    )
    
    # 3. Scatter plot de velocidad por ubicación
    fig.add_trace(
        go.Scatter(x=df['longitud'], y=df['latitud'], 
                  mode='markers', marker=dict(color=df['velocidad_kmh'], 
                  colorscale='RdYlGn', size=5), name='Vel. por Ubicación'),
        row=2, col=1
    )
    
    # 4. Velocidad promedio por bus
    vel_por_bus = df.groupby('placa')['velocidad_kmh'].mean().reset_index()
    fig.add_trace(
        go.Bar(x=vel_por_bus['placa'], y=vel_por_bus['velocidad_kmh'],
               name='Vel. por Bus'),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, 
                     title_text="Dashboard de Análisis de Velocidades - Buses Arequipa")
    
    archivo_dashboard = "dashboard_velocidades.html"
    fig.write_html(archivo_dashboard)
    print(f"✅ Dashboard guardado como '{archivo_dashboard}'")
    return archivo_dashboard

def generar_reporte_estadisticas():
    """Genera un reporte estadístico completo"""
    print("Generando reporte estadístico...")
    
    sql_query = """
    SELECT
        COUNT(*) as total_registros,
        COUNT(DISTINCT placa) as total_buses,
        AVG(velocidad_kmh) as velocidad_promedio,
        MIN(velocidad_kmh) as velocidad_minima,
        MAX(velocidad_kmh) as velocidad_maxima,
        STDDEV(velocidad_kmh) as desviacion_velocidad,
        MIN(ts) as primer_registro,
        MAX(ts) as ultimo_registro
    FROM bus_locations;
    """
    
    stats = pd.read_sql(sql_query, engine)
    
    print("\n" + "="*50)
    print("📊 REPORTE ESTADÍSTICO - PROYECTO BUSES AREQUIPA")
    print("="*50)
    print(f"📈 Total de registros: {stats['total_registros'].iloc[0]:,}")
    print(f"🚌 Total de buses: {stats['total_buses'].iloc[0]}")
    print(f"⚡ Velocidad promedio: {stats['velocidad_promedio'].iloc[0]:.2f} km/h")
    print(f"🐌 Velocidad mínima: {stats['velocidad_minima'].iloc[0]} km/h")
    print(f"🏃 Velocidad máxima: {stats['velocidad_maxima'].iloc[0]} km/h")
    print(f"📊 Desviación estándar: {stats['desviacion_velocidad'].iloc[0]:.2f} km/h")
    print(f"📅 Período de datos: {stats['primer_registro'].iloc[0]} a {stats['ultimo_registro'].iloc[0]}")
    print("="*50)

if __name__ == "__main__":
    print("🗺️ VISUALIZADOR DE BUSES AREQUIPA")
    print("=" * 40)
    
    try:
        # 1. Crear mapa interactivo
        archivo_mapa = crear_mapa_interactivo()
        
        # 2. Crear dashboard
        archivo_dashboard = crear_dashboard_velocidades()
        
        # 3. Generar estadísticas
        generar_reporte_estadisticas()
        
        print(f"\n🎉 ¡Visualización completada!")
        print(f"📁 Archivos generados:")
        print(f"   • {archivo_mapa}")
        print(f"   • {archivo_dashboard}")
        print(f"\n💡 Abre estos archivos en tu navegador para ver las visualizaciones.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Verificaciones:")
        print("   • ¿Está PostgreSQL corriendo?")
        print("   • ¿Las credenciales son correctas?")
        print("   • ¿Tienes instalado: pip install folium plotly")
