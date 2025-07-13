import pandas as pd
from sqlalchemy import create_engine
import geopandas as gpd
from shapely.geometry import Point
from geoalchemy2 import Geometry, WKTElement

db_user = 'postgres'
db_password = '15243'
db_host = 'localhost'
db_port = '5432'
db_name = 'MiPrimeraDB'

db_connection_str = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

def cargar_datos_realistas():
    """Carga los datos realistas a la base de datos."""
    print("Cargando datos realistas a la base de datos...")
    
    print("Cargando datos desde CSV...")
    df = pd.read_csv('datos_buses_aqp_realistas.csv')
    df['ts'] = pd.to_datetime(df['timestamp'])
    print(f"Registros cargados: {len(df)}")
    
    print("Convirtiendo a formato geoespacial...")
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitud, df.latitud),
        crs="EPSG:4326"
    ).rename(columns={'geometry': 'location'})
    
    final_gdf = gdf[['placa', 'velocidad_kmh', 'location', 'ts', 'origen', 'destino']].copy()
    final_gdf['location'] = final_gdf['location'].apply(lambda x: WKTElement(x.wkt, srid=4326))
    
    print("Conectando a PostgreSQL...")
    try:
        engine = create_engine(db_connection_str)
        
        tabla_nueva = 'bus_locations_realistas'
        final_gdf.to_sql(
            tabla_nueva,
            con=engine,
            if_exists='replace',
            index=False,
            dtype={'location': Geometry('POINT', srid=4326)}
        )
        
        print(f"Datos cargados exitosamente: {len(final_gdf)} registros en tabla '{tabla_nueva}'.")
        
        verificar_carga(engine, tabla_nueva)
        
    except Exception as e:
        print(f"Error: {e}")

def verificar_carga(engine, tabla):
    """Verifica que los datos se cargaron correctamente."""
    print(f"Verificando carga en tabla '{tabla}'")
    
    sql_verificacion = f"""
    SELECT 
        COUNT(*) as total_registros,
        COUNT(DISTINCT placa) as buses_unicos,
        COUNT(DISTINCT origen) as origenes_unicos,
        COUNT(DISTINCT destino) as destinos_unicos,
        AVG(velocidad_kmh) as velocidad_promedio,
        MIN(ts) as primer_registro,
        MAX(ts) as ultimo_registro
    FROM {tabla};
    """
    
    result = pd.read_sql(sql_verificacion, engine)
    
    print(f"Registros totales: {result['total_registros'].iloc[0]:,}")
    print(f"Buses únicos: {result['buses_unicos'].iloc[0]}")
    print(f"Orígenes únicos: {result['origenes_unicos'].iloc[0]}")
    print(f"Destinos únicos: {result['destinos_unicos'].iloc[0]}")
    print(f"Velocidad promedio: {result['velocidad_promedio'].iloc[0]:.1f} km/h")
    print(f"Período: {result['primer_registro'].iloc[0]} a {result['ultimo_registro'].iloc[0]}")
    
    sql_rutas = f"""
    SELECT origen, destino, COUNT(*) as registros, AVG(velocidad_kmh) as vel_promedio
    FROM {tabla}
    GROUP BY origen, destino
    ORDER BY registros DESC
    LIMIT 5;
    """
    
    rutas = pd.read_sql(sql_rutas, engine)
    print(f"Top 5 rutas con más registros:")
    for _, row in rutas.iterrows():
        print(f"   {row['origen']} -> {row['destino']}: {row['registros']} registros, {row['vel_promedio']:.1f} km/h")

def comparar_tablas():
    """Compara la tabla original vs realista en la BD."""
    print(f"Comparación de tablas en base de datos")
    print("=" * 50)
    
    engine = create_engine(db_connection_str)
    
    # Comparar estadísticas básicas
    tablas = ['bus_locations', 'bus_locations_realistas']
    
    for tabla in tablas:
        try:
            sql = f"""
            SELECT 
                '{tabla}' as tabla,
                COUNT(*) as registros,
                COUNT(DISTINCT placa) as buses,
                AVG(velocidad_kmh) as vel_promedio,
                STDDEV(velocidad_kmh) as vel_desviacion
            FROM {tabla};
            """
            result = pd.read_sql(sql, engine)
            print(f"\n📋 {tabla.upper()}:")
            print(f"   Registros: {result['registros'].iloc[0]:,}")
            print(f"   Buses: {result['buses'].iloc[0]}")
            print(f"   Velocidad: {result['vel_promedio'].iloc[0]:.1f} ± {result['vel_desviacion'].iloc[0]:.1f} km/h")
            
        except Exception as e:
            print(f"   ❌ Error accediendo a {tabla}: {e}")

if __name__ == "__main__":
    cargar_datos_realistas()
    comparar_tablas()
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print("1. Crear visualización de datos realistas")
    print("2. Re-entrenar modelo con nuevos datos")  
    print("3. Comparar predicciones")
