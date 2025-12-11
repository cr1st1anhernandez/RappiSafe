# -*- coding: utf-8 -*-
"""
Script para probar envio de SMS a numeros especificos
"""
import os
import django
from pathlib import Path

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(Path('.') / '.env', override=True)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from rappiSafe.utils import enviar_sms_mocean

def test_numeros():
    """Probar envio a numeros especificos"""

    # Numeros a probar
    numeros = [
        ("+529515791240", "Yaxche"),
        ("+529512333959", "Miguel"),
        ("+529513927020", "Cris")
    ]

    mensaje_prueba = """PRUEBA - RAPPI SAFE

Este es un mensaje de prueba para verificar que Mocean funciona correctamente.

Si recibes este mensaje, la configuracion esta funcionando."""

    print("\n" + "="*60)
    print("PRUEBA DE ENVIO A NUMEROS ESPECIFICOS")
    print("="*60 + "\n")

    resultados = []

    for numero, nombre in numeros:
        print(f"\n--- Probando {nombre} ({numero}) ---")

        resultado = enviar_sms_mocean(numero, mensaje_prueba)

        resultados.append({
            'nombre': nombre,
            'numero': numero,
            'success': resultado['success'],
            'error': resultado.get('error', 'N/A')
        })

        print()  # Linea en blanco

    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60 + "\n")

    exitosos = 0
    fallidos = 0

    for r in resultados:
        status_icon = "[OK]" if r['success'] else "[X]"
        print(f"{status_icon} {r['nombre']:15} {r['numero']}")
        if not r['success']:
            print(f"     Error: {r['error']}")

        if r['success']:
            exitosos += 1
        else:
            fallidos += 1

    print(f"\n[TOTAL] Exitosos: {exitosos} | Fallidos: {fallidos}")

    # Verificar saldo de Mocean
    print("\n" + "="*60)
    print("RECOMENDACIONES")
    print("="*60)
    print("\n1. Verifica tu saldo en: https://dashboard.moceanapi.com/")
    print("2. Confirma que los numeros esten activos y puedan recibir SMS")
    print("3. Si todos fallan, puede ser problema de creditos o token")
    print("4. Si solo algunos fallan, verifica el formato del numero\n")

if __name__ == '__main__':
    try:
        test_numeros()
    except KeyboardInterrupt:
        print("\n\n[AVISO] Prueba cancelada por el usuario\n")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}\n")
        import traceback
        traceback.print_exc()
