import pandas as pd

def comparar_datasets():
    """Compara los datasets original y realista"""
    print("🔍 COMPARACIÓN DE DATASETS")
    print("=" * 50)
    
    # Cargar ambos datasets
    df_original = pd.read_csv('datos_buses_aqp.csv')
    df_realista = pd.read_csv('datos_buses_aqp_realistas.csv')
    
    print(f"📊 DATASET ORIGINAL:")
    print(f"   • Registros: {len(df_original):,}")
    print(f"   • Buses únicos: {df_original['placa'].nunique()}")
    print(f"   • Velocidad promedio: {df_original['velocidad_kmh'].mean():.1f} km/h")
    print(f"   • Velocidad min/max: {df_original['velocidad_kmh'].min()}/{df_original['velocidad_kmh'].max()} km/h")
    print(f"   • Rango lat: {df_original['latitud'].min():.4f} a {df_original['latitud'].max():.4f}")
    print(f"   • Rango lon: {df_original['longitud'].min():.4f} a {df_original['longitud'].max():.4f}")
    
    print(f"\n📊 DATASET REALISTA:")
    print(f"   • Registros: {len(df_realista):,}")
    print(f"   • Buses únicos: {df_realista['placa'].nunique()}")
    print(f"   • Velocidad promedio: {df_realista['velocidad_kmh'].mean():.1f} km/h")
    print(f"   • Velocidad min/max: {df_realista['velocidad_kmh'].min()}/{df_realista['velocidad_kmh'].max()} km/h")
    print(f"   • Rango lat: {df_realista['latitud'].min():.4f} a {df_realista['latitud'].max():.4f}")
    print(f"   • Rango lon: {df_realista['longitud'].min():.4f} a {df_realista['longitud'].max():.4f}")
    
    if 'origen' in df_realista.columns:
        print(f"   • Rutas origen: {df_realista['origen'].unique()}")
        print(f"   • Rutas destino: {df_realista['destino'].unique()}")
    
    print(f"\n🎯 DIFERENCIAS CLAVE:")
    cobertura_original = (df_original['latitud'].max() - df_original['latitud'].min()) * \
                        (df_original['longitud'].max() - df_original['longitud'].min())
    cobertura_realista = (df_realista['latitud'].max() - df_realista['latitud'].min()) * \
                        (df_realista['longitud'].max() - df_realista['longitud'].min())
    
    print(f"   • Cobertura geográfica original: {cobertura_original:.6f}°²")
    print(f"   • Cobertura geográfica realista: {cobertura_realista:.6f}°²")
    print(f"   • Factor de mejora en cobertura: {cobertura_realista/cobertura_original:.1f}x")
    
    # Análisis de distribución de velocidades
    print(f"\n📈 DISTRIBUCIÓN DE VELOCIDADES:")
    for dataset, df, nombre in [('Original', df_original, 'original'), 
                               ('Realista', df_realista, 'realista')]:
        velocidades_bajas = (df['velocidad_kmh'] < 15).sum()
        velocidades_medias = ((df['velocidad_kmh'] >= 15) & (df['velocidad_kmh'] < 30)).sum()
        velocidades_altas = (df['velocidad_kmh'] >= 30).sum()
        
        print(f"   {dataset}:")
        print(f"     • Velocidades bajas (<15 km/h): {velocidades_bajas} ({velocidades_bajas/len(df)*100:.1f}%)")
        print(f"     • Velocidades medias (15-30 km/h): {velocidades_medias} ({velocidades_medias/len(df)*100:.1f}%)")
        print(f"     • Velocidades altas (>30 km/h): {velocidades_altas} ({velocidades_altas/len(df)*100:.1f}%)")

def mostrar_rutas_realistas():
    """Muestra las rutas específicas del dataset realista"""
    df = pd.read_csv('datos_buses_aqp_realistas.csv')
    
    if 'origen' in df.columns and 'destino' in df.columns:
        print(f"\n🛣️ RUTAS IDENTIFICADAS EN DATASET REALISTA:")
        print("=" * 50)
        
        rutas = df.groupby(['origen', 'destino']).agg({
            'placa': 'nunique',
            'velocidad_kmh': 'mean'
        }).round(1)
        
        rutas.columns = ['Buses', 'Vel_Promedio']
        print(rutas)
        
        print(f"\n📍 PUNTOS DE INTERÉS UTILIZADOS:")
        puntos = set(df['origen'].unique()) | set(df['destino'].unique())
        for i, punto in enumerate(sorted(puntos), 1):
            print(f"   {i}. {punto}")

if __name__ == "__main__":
    try:
        comparar_datasets()
        mostrar_rutas_realistas()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de que ambos archivos CSV existan")
