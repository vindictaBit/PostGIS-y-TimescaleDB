# Análisis Predictivo de Buses - Arequipa

Simulación y análisis de tráfico de buses en Arequipa usando Machine Learning y datos GPS.

## Requisitos

1. **PostgreSQL 12+** con extensiones:
   - PostGIS
   - TimescaleDB

2. **Python 3.8+** con entorno virtual

3. **Base de datos incluida**: `MiPrimeraDB.backup`

## Instalación Rápida

```bash
# 1. Restaurar base de datos PostgreSQL
psql -U postgres -c "CREATE DATABASE MiPrimeraDB;"
pg_restore -U postgres -d MiPrimeraDB MiPrimeraDB.backup

# 2. Configurar entorno Python
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Configuración BD
```
Usuario: postgres
Contraseña: 123123
Host: localhost
Puerto: 5432
Base de datos: MiPrimeraDB
```

## Ejecución

### PrimerIntento (Datos Básicos)
```bash
cd PrimerIntento
python generador_datos.py      # Genera CSV con datos sintéticos
python cargar_datos.py         # Carga a PostgreSQL
python analisis_predictivo.py  # Entrena modelo ML
```

**Características:**
- Datos sintéticos simples (6,000 registros)
- Ruta lineal Mall Cayma → Plaza de Armas
- Modelo Random Forest
- Error: ~4.34 km/h

### SegundoIntento (Datos Realistas)
```bash
cd SegundoIntento
python generador_datos_realistas.py    # Datos siguiendo calles reales
python cargar_datos_realistas.py       # Carga a BD
python analisis_predictivo_mejorado.py # Modelo mejorado
python visualizador_realista.py        # Mapas interactivos
```

**Características:**
- Rutas 'reales' usando OpenStreetMap (aunque no funciona bien)
- 8 puntos de interés en Arequipa
- Mapas interactivos (Folium)
- Modelo ML con más features
- Error mejorado y velocidades (~15.7 km/h)

## Archivos Generados
- `datos_buses_aqp.csv` - Dataset básico
- `datos_buses_aqp_realistas.csv` - Dataset más completo
- `mapa_buses_*.html` - Mapas interactivos
- `dashboard_velocidades.html` - Dashboard analítico
