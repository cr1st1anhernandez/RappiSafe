"""
Script de prueba para verificar que Mocean API funciona correctamente
"""
import os
import django
from pathlib import Path

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(Path('.') / '.env')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from rappiSafe.utils import enviar_sms_mocean

def test_mocean():
    print("\n=== TEST DE MOCEAN API ===\n")

    # Verificar que el token esté configurado
    token = os.environ.get('MOCEAN_API_TOKEN')
    if token:
        print(f"OK - Token de Mocean configurado: {token[:20]}...")
    else:
        print("ERROR - Token de Mocean NO configurado")
        print("Configura MOCEAN_API_TOKEN en el archivo .env")
        return

    # Verificar que el SDK esté instalado
    try:
        from moceansdk import Client
        print("OK - SDK de Mocean instalado correctamente")
    except ImportError:
        print("ERROR - SDK de Mocean NO instalado")
        print("Instala con: pip install moceansdk")
        return

    print("\n" + "="*50)
    print("CONFIGURACION CORRECTA")
    print("="*50)
    print("\nPara probar el envio de SMS:")
    print("1. Activa una alerta de panico desde la app")
    print("2. Asegurate de tener contactos de emergencia registrados")
    print("3. Los SMS se enviaran automaticamente via Mocean")
    print("\nFormato de telefono requerido: +521234567890 (con codigo de pais)")
    print("\n")

if __name__ == '__main__':
    test_mocean()
