import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

db_user = 'postgres'
db_password = '123' # Contraseña postgresql
db_host = 'localhost'
db_port = '5432'
db_name = 'MiPrimeraDB'

db_connection_str = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(db_connection_str)

print("Cargando datos desde la base de datos...")
sql_query = """
SELECT
    ST_Y(location) AS latitud,
    ST_X(location) AS longitud,
    velocidad_kmh,
    EXTRACT(HOUR FROM ts) AS hora
FROM
    bus_locations;
"""
df = pd.read_sql(sql_query, engine)
print(f"Se cargaron {len(df)} registros.")

feature_names = ['latitud', 'longitud', 'hora']
X = df[feature_names].copy()
y = df['velocidad_kmh'].copy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("Datos preparados para entrenamiento...")

model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)

print("Entrenando modelo...")
model.fit(X_train, y_train)
print("Modelo entrenado exitosamente.")

print("\nEvaluando modelo...")
predictions = model.predict(X_test)
error = mean_absolute_error(y_test, predictions)
print(f"Error Absoluto Medio: {error:.2f} km/h")

print("\nPredicción en punto de interés:")
lat_ov_miraflores = -16.4113
lon_ov_miraflores = -71.5235
hora_punta = 18

punto_df = pd.DataFrame({
    'latitud': [lat_ov_miraflores],
    'longitud': [lon_ov_miraflores], 
    'hora': [hora_punta]
})

velocidad_predicha = model.predict(punto_df)

print(f"Lugar: Óvalo de Miraflores")
print(f"Hora: {hora_punta}:00 h")
print(f"Velocidad Predicha: {velocidad_predicha[0]:.2f} km/h")

if velocidad_predicha[0] < 15:
    print("Resultado: Alta probabilidad de congestión")
else:
    print("Resultado: Tráfico fluido")