import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import warnings

# Suprimir el warning específico que viste
warnings.filterwarnings("ignore", message="X does not have valid feature names")

# --- CONFIGURACIÓN DE LA CONEXIÓN ---
db_user = 'postgres'
db_password = '123' # Contraseña postgresql
db_host = 'localhost'
db_port = '5432'
db_name = 'MiPrimeraDB'

db_connection_str = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(db_connection_str)

def cargar_datos_mejorados():
    """Carga datos con más features para mejor predicción"""
    print("Cargando datos desde la base de datos...")
    
    sql_query = """
    SELECT
        ST_Y(location) AS latitud,
        ST_X(location) AS longitud,
        velocidad_kmh,
        EXTRACT(HOUR FROM ts) AS hora,
        EXTRACT(DOW FROM ts) AS dia_semana,
        EXTRACT(MINUTE FROM ts) AS minuto,
        -- Calcular distancia al centro (Plaza de Armas)
        ST_Distance(location, ST_SetSRID(ST_Point(-71.5367, -16.3989), 4326)) AS distancia_centro,
        -- Identificar si es fin de semana
        CASE WHEN EXTRACT(DOW FROM ts) IN (0, 6) THEN 1 ELSE 0 END AS es_fin_semana,
        -- Identificar horas punta
        CASE 
            WHEN EXTRACT(HOUR FROM ts) BETWEEN 7 AND 9 THEN 1
            WHEN EXTRACT(HOUR FROM ts) BETWEEN 13 AND 14 THEN 1  
            WHEN EXTRACT(HOUR FROM ts) BETWEEN 17 AND 20 THEN 1
            ELSE 0 
        END AS es_hora_punta
    FROM bus_locations;
    """
    
    df = pd.read_sql(sql_query, engine)
    print(f"Se cargaron {len(df)} registros con features mejoradas.")
    return df

def crear_features_adicionales(df):
    """Crea features adicionales para mejorar el modelo"""
    print("Creando features adicionales...")
    
    # Features trigonométricas para capturar patrones cíclicos
    df['hora_sin'] = np.sin(2 * np.pi * df['hora'] / 24)
    df['hora_cos'] = np.cos(2 * np.pi * df['hora'] / 24)
    df['minuto_sin'] = np.sin(2 * np.pi * df['minuto'] / 60)
    df['minuto_cos'] = np.cos(2 * np.pi * df['minuto'] / 60)
    
    # Interaction features
    df['lat_hora'] = df['latitud'] * df['hora']
    df['lon_hora'] = df['longitud'] * df['hora']
    df['distancia_hora'] = df['distancia_centro'] * df['hora']
    
    # Categorizar zonas de la ciudad
    df['zona'] = 'centro'
    df.loc[df['latitud'] < -16.41, 'zona'] = 'sur'
    df.loc[df['latitud'] > -16.39, 'zona'] = 'norte'
    df.loc[df['longitud'] < -71.54, 'zona'] = 'este'
    df.loc[df['longitud'] > -71.53, 'zona'] = 'oeste'
    
    # One-hot encoding para zona
    zona_dummies = pd.get_dummies(df['zona'], prefix='zona')
    df = pd.concat([df, zona_dummies], axis=1)
    
    print(f"Features creadas. Total de columnas: {len(df.columns)}")
    return df

def entrenar_modelo_mejorado(df):
    """Entrena un modelo más sofisticado"""
    print("Preparando modelo de Machine Learning mejorado...")
    
    # Seleccionar features para el modelo
    feature_columns = [
        'latitud', 'longitud', 'hora', 'dia_semana', 'minuto',
        'distancia_centro', 'es_fin_semana', 'es_hora_punta',
        'hora_sin', 'hora_cos', 'minuto_sin', 'minuto_cos',
        'lat_hora', 'lon_hora', 'distancia_hora'
    ]
    
    # Agregar columnas de zona si existen
    zona_cols = [col for col in df.columns if col.startswith('zona_')]
    feature_columns.extend(zona_cols)
    
    # Filtrar solo las columnas que existen
    feature_columns = [col for col in feature_columns if col in df.columns]
    
    X = df[feature_columns]
    y = df['velocidad_kmh']
    
    print(f"Features utilizadas: {len(feature_columns)}")
    print(f"   {', '.join(feature_columns)}")
    
    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=None
    )
    
    # Escalar features (importante para algunos modelos)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Entrenar Random Forest con mejores parámetros
    model = RandomForestRegressor(
        n_estimators=200,           # Más árboles para mejor precisión
        max_depth=15,               # Limitar profundidad para evitar overfitting
        min_samples_split=5,        # Mínimo de muestras para dividir nodo
        min_samples_leaf=2,         # Mínimo de muestras en hoja
        random_state=42,
        n_jobs=-1                   # Usar todos los procesadores
    )
    
    print("Entrenando modelo... (esto puede tardar un momento)")
    model.fit(X_train_scaled, y_train)
    print("¡Modelo entrenado!")
    
    # Evaluar modelo
    print("\nEvaluando rendimiento del modelo...")
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    mae_train = mean_absolute_error(y_train, y_pred_train)
    mae_test = mean_absolute_error(y_test, y_pred_test)
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)
    
    print(f" Resultados del modelo:")
    print(f"   • Error Absoluto Medio (entrenamiento): {mae_train:.2f} km/h")
    print(f"   • Error Absoluto Medio (prueba): {mae_test:.2f} km/h")
    print(f"   • R² Score (entrenamiento): {r2_train:.3f}")
    print(f"   • R² Score (prueba): {r2_test:.3f}")
    
    if mae_test > mae_train * 1.5:
        print("Posible overfitting detectado")
    else:
        print("Modelo generaliza bien")
    
    # Importancia de features
    print(f"\nFeatures más importantes:")
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for i, row in feature_importance.head(10).iterrows():
        print(f"   {row['feature']}: {row['importance']:.3f}")
    
    # Guardar modelo y scaler
    joblib.dump(model, 'modelo_velocidad_buses.pkl')
    joblib.dump(scaler, 'scaler_velocidad_buses.pkl')
    joblib.dump(feature_columns, 'feature_columns.pkl')
    print(f"\nModelo guardado como 'modelo_velocidad_buses.pkl'")
    
    return model, scaler, feature_columns

def hacer_predicciones_multiples(model, scaler, feature_columns):
    """Hace predicciones para múltiples puntos de interés"""
    print("\nPREDICCIONES PARA PUNTOS DE INTERÉS")
    print("=" * 50)
    
    # Puntos de interés en Arequipa
    puntos_interes = [
        {"nombre": "Plaza de Armas", "lat": -16.3989, "lon": -71.5367},
        {"nombre": "Mall Plaza Cayma", "lat": -16.3795, "lon": -71.5492},
        {"nombre": "Terminal Terrestre", "lat": -16.4195, "lon": -71.5179},
        {"nombre": "Óvalo Miraflores", "lat": -16.4113, "lon": -71.5235},
        {"nombre": "Universidad San Agustín", "lat": -16.4068, "lon": -71.5223}
    ]
    
    # Horas de interés
    horas_interes = [8, 13, 18, 22]  # 8 AM, 1 PM, 6 PM, 10 PM
    
    for punto in puntos_interes:
        print(f"\n{punto['nombre']}")
        print("-" * 30)
        
        for hora in horas_interes:
            # Crear features para predicción
            datos_pred = crear_features_para_prediccion(
                punto['lat'], punto['lon'], hora, feature_columns
            )
            
            # Escalar y predecir
            datos_pred_scaled = scaler.transform([datos_pred])
            velocidad_pred = model.predict(datos_pred_scaled)[0]
            
            # Interpretación
            if velocidad_pred < 15:
                estado = "Congestión severa"
            elif velocidad_pred < 25:
                estado = "Tráfico lento"
            elif velocidad_pred < 35:
                estado = "Tráfico moderado"
            else:
                estado = "Tráfico fluido"
            
            print(f"   {hora:2d}:00h → {velocidad_pred:5.1f} km/h {estado}")

def crear_features_para_prediccion(lat, lon, hora, feature_columns):
    """Crea el vector de features para una predicción específica"""
    # Valores base
    datos = {
        'latitud': lat,
        'longitud': lon,
        'hora': hora,
        'dia_semana': 1,  # Lunes por defecto
        'minuto': 0,
        'distancia_centro': np.sqrt((lat - (-16.3989))**2 + (lon - (-71.5367))**2),
        'es_fin_semana': 0,
        'es_hora_punta': 1 if hora in [7,8,9,13,14,17,18,19,20] else 0,
        'hora_sin': np.sin(2 * np.pi * hora / 24),
        'hora_cos': np.cos(2 * np.pi * hora / 24),
        'minuto_sin': 0,
        'minuto_cos': 1,
        'lat_hora': lat * hora,
        'lon_hora': lon * hora,
        'distancia_hora': np.sqrt((lat - (-16.3989))**2 + (lon - (-71.5367))**2) * hora
    }
    
    # Zona (simplificado)
    if lat < -16.41:
        zona = 'sur'
    elif lat > -16.39:
        zona = 'norte'
    elif lon < -71.54:
        zona = 'este'
    elif lon > -71.53:
        zona = 'oeste'
    else:
        zona = 'centro'
    
    # One-hot encoding para zona
    for z in ['centro', 'este', 'norte', 'oeste', 'sur']:
        datos[f'zona_{z}'] = 1 if zona == z else 0
    
    # Retornar solo las features que el modelo espera
    return [datos.get(col, 0) for col in feature_columns]

def main():
    """Función principal mejorada"""
    print("ANÁLISIS PREDICTIVO MEJORADO - BUSES AREQUIPA")
    print("=" * 60)
    
    try:
        # 1. Cargar y preparar datos
        df = cargar_datos_mejorados()
        df = crear_features_adicionales(df)
        
        # 2. Entrenar modelo
        model, scaler, feature_columns = entrenar_modelo_mejorado(df)
        
        # 3. Hacer predicciones múltiples
        hacer_predicciones_multiples(model, scaler, feature_columns)
        
        print(f"\n¡Análisis completado!")
        print(f"El modelo mejorado está listo para usar.")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nVerificaciones:")
        print("   • ¿PostgreSQL está corriendo?")
        print("   • ¿Los datos están cargados en 'bus_locations'?")
        print("   • ¿Las credenciales de BD son correctas?")

if __name__ == "__main__":
    main()
