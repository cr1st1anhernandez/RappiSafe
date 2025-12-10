"""
Script para verificar y limpiar alertas activas
Ejecutar con: python manage.py shell < verificar_alertas.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from rappiSafe.models import Alerta, User

print("\n=== VERIFICACIÓN DE ALERTAS ACTIVAS ===\n")

# Buscar todas las alertas activas
alertas_activas = Alerta.objects.filter(estado__in=['pendiente', 'en_atencion'])

if not alertas_activas.exists():
    print("✅ No hay alertas activas en el sistema")
else:
    print(f"⚠️ Encontradas {alertas_activas.count()} alertas activas:\n")

    for alerta in alertas_activas:
        print(f"  - ID: {alerta.id}")
        print(f"    Repartidor: {alerta.repartidor.get_full_name()} ({alerta.repartidor.username})")
        print(f"    Tipo: {alerta.get_tipo_display()}")
        print(f"    Estado: {alerta.get_estado_display()}")
        print(f"    Creada: {alerta.creado_en}")
        print()

    print("Cerrando todas las alertas activas...")

    for alerta in alertas_activas:
        alerta.estado = 'cerrada'
        alerta.save()
        print(f"  ✓ Alerta {alerta.id} cerrada")

    print(f"\n✅ Se cerraron {alertas_activas.count()} alertas")

    # Actualizar estado de repartidores
    repartidores_actualizados = []
    for alerta in alertas_activas:
        if alerta.repartidor.perfil_repartidor.estado == 'emergencia':
            alerta.repartidor.perfil_repartidor.estado = 'offline'
            alerta.repartidor.perfil_repartidor.save()
            repartidores_actualizados.append(alerta.repartidor.username)

    if repartidores_actualizados:
        print(f"✅ Estado de repartidores actualizado: {', '.join(repartidores_actualizados)}")

print("\n=== FIN DE LA VERIFICACIÓN ===\n")
