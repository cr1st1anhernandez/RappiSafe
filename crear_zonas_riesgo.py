"""
Script para crear datos de ejemplo de zonas de riesgo
Ejecutar con: python manage.py shell < crear_zonas_riesgo.py
"""

import os
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from rappiSafe.models import EstadisticaRiesgo

# Limpiar datos anteriores
EstadisticaRiesgo.objects.all().delete()
print("OK - Datos anteriores eliminados")

# Definir zonas de riesgo con coordenadas de ejemplo (Ciudad de México)
zonas = [
    {
        'nombre_zona': 'Tepito',
        'coordenadas_zona': {
            'center': {
                'lat': 19.4497,
                'lng': -99.1247
            }
        },
        'puntuacion_riesgo': 8.5,
        'total_alertas': 45,
        'alertas_panico': 28,
        'alertas_accidente': 17,
    },
    {
        'nombre_zona': 'Doctores',
        'coordenadas_zona': {
            'center': {
                'lat': 19.4242,
                'lng': -99.1456
            }
        },
        'puntuacion_riesgo': 7.2,
        'total_alertas': 32,
        'alertas_panico': 20,
        'alertas_accidente': 12,
    },
    {
        'nombre_zona': 'La Merced',
        'coordenadas_zona': {
            'center': {
                'lat': 19.4258,
                'lng': -99.1250
            }
        },
        'puntuacion_riesgo': 7.8,
        'total_alertas': 38,
        'alertas_panico': 24,
        'alertas_accidente': 14,
    },
    {
        'nombre_zona': 'Iztapalapa Centro',
        'coordenadas_zona': {
            'center': {
                'lat': 19.3467,
                'lng': -99.0550
            }
        },
        'puntuacion_riesgo': 6.5,
        'total_alertas': 28,
        'alertas_panico': 16,
        'alertas_accidente': 12,
    },
    {
        'nombre_zona': 'Ecatepec Norte',
        'coordenadas_zona': {
            'center': {
                'lat': 19.6177,
                'lng': -99.0536
            }
        },
        'puntuacion_riesgo': 8.0,
        'total_alertas': 42,
        'alertas_panico': 26,
        'alertas_accidente': 16,
    },
    {
        'nombre_zona': 'Neza Centro',
        'coordenadas_zona': {
            'center': {
                'lat': 19.4008,
                'lng': -99.0144
            }
        },
        'puntuacion_riesgo': 7.5,
        'total_alertas': 35,
        'alertas_panico': 22,
        'alertas_accidente': 13,
    },
    {
        'nombre_zona': 'Polanco',
        'coordenadas_zona': {
            'center': {
                'lat': 19.4331,
                'lng': -99.1936
            }
        },
        'puntuacion_riesgo': 3.2,
        'total_alertas': 8,
        'alertas_panico': 3,
        'alertas_accidente': 5,
    },
    {
        'nombre_zona': 'Santa Fe',
        'coordenadas_zona': {
            'center': {
                'lat': 19.3602,
                'lng': -99.2675
            }
        },
        'puntuacion_riesgo': 2.8,
        'total_alertas': 6,
        'alertas_panico': 2,
        'alertas_accidente': 4,
    },
    {
        'nombre_zona': 'Gustavo A. Madero',
        'coordenadas_zona': {
            'center': {
                'lat': 19.4906,
                'lng': -99.1167
            }
        },
        'puntuacion_riesgo': 6.8,
        'total_alertas': 30,
        'alertas_panico': 18,
        'alertas_accidente': 12,
    },
    {
        'nombre_zona': 'Xochimilco',
        'coordenadas_zona': {
            'center': {
                'lat': 19.2544,
                'lng': -99.1036
            }
        },
        'puntuacion_riesgo': 5.5,
        'total_alertas': 22,
        'alertas_panico': 12,
        'alertas_accidente': 10,
    },
]

# Crear zonas de riesgo
fecha_inicio = date.today() - timedelta(days=30)
fecha_fin = date.today()

for zona_data in zonas:
    zona = EstadisticaRiesgo.objects.create(
        nombre_zona=zona_data['nombre_zona'],
        coordenadas_zona=zona_data['coordenadas_zona'],
        puntuacion_riesgo=zona_data['puntuacion_riesgo'],
        total_alertas=zona_data['total_alertas'],
        alertas_panico=zona_data['alertas_panico'],
        alertas_accidente=zona_data['alertas_accidente'],
        periodo_inicio=fecha_inicio,
        periodo_fin=fecha_fin
    )
    print(f"OK - Zona creada: {zona.nombre_zona} (Riesgo: {zona.puntuacion_riesgo})")

print(f"\nOK - Se crearon {len(zonas)} zonas de riesgo")
print("OK - Las zonas se mostrarán en la vista del repartidor según su ubicación")
