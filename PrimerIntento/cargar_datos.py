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

df = pd.read_csv('datos_buses_aqp.csv')
df['ts'] = pd.to_datetime(df['timestamp'])
print("Cargando datos desde CSV...")

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.longitud, df.latitud),
    crs="EPSG:4326"
).rename(columns={'geometry': 'location'})

final_gdf = gdf[['placa', 'velocidad_kmh', 'location', 'ts']].copy()
final_gdf['location'] = final_gdf['location'].apply(lambda x: WKTElement(x.wkt, srid=4326))
print("Datos convertidos a formato geoespacial...")

try:
    engine = create_engine(db_connection_str)
    final_gdf.to_sql(
        'bus_locations',
        con=engine,
        if_exists='append',
        index=False,
        dtype={'location': Geometry('POINT', srid=4326)}
    )
    print(f"Datos cargados exitosamente: {len(final_gdf)} registros en tabla 'bus_locations'.")
except Exception as e:
    print(f"Error al cargar datos: {e}")