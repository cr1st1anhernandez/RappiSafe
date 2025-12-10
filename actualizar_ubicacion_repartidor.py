"""
Script para actualizar ubicación de un repartidor de prueba
Ejecutar con: python manage.py shell < actualizar_ubicacion_repartidor.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from rappiSafe.models import User, RepartidorProfile
from django.utils import timezone

# Buscar repartidores
repartidores = User.objects.filter(rol='repartidor')

if not repartidores.exists():
    print("ERROR - No hay repartidores en el sistema")
else:
    # Actualizar el primer repartidor con una ubicación cerca del Centro de CDMX
    repartidor = repartidores.first()
    perfil = repartidor.perfil_repartidor

    # Coordenadas del Zócalo de CDMX (para que haya zonas de riesgo cercanas)
    perfil.ultima_latitud = 19.4326  # Zócalo CDMX
    perfil.ultima_longitud = -99.1332
    perfil.ultima_actualizacion_ubicacion = timezone.now()
    perfil.save()

    print(f"OK - Ubicación actualizada para: {repartidor.get_full_name()} ({repartidor.username})")
    print(f"     Latitud: {perfil.ultima_latitud}")
    print(f"     Longitud: {perfil.ultima_longitud}")
    print("\nOK - Ahora puedes iniciar sesión como este repartidor para ver las zonas de riesgo cercanas")
    print("     Las zonas más cercanas deberían ser: Tepito, Doctores, La Merced")
