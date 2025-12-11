# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el envio de SMS con Mocean API
Ejecutar con: python test_sms_mocean.py
"""
import os
import django
from pathlib import Path

# Cargar variables de entorno
from dotenv import load_dotenv
# override=True hace que el .env tenga prioridad sobre variables del sistema
load_dotenv(Path('.') / '.env', override=True)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from rappiSafe.utils import enviar_sms_mocean

def test_configuracion():
    """Verificar que la configuracion este correcta"""
    print("\n" + "="*60)
    print("TEST DE CONFIGURACION MOCEAN API")
    print("="*60 + "\n")

    # 1. Verificar token
    token = os.environ.get('MOCEAN_API_TOKEN')
    if token:
        print(f"[OK] Token configurado: {token[:30]}...")
        print(f"     Longitud: {len(token)} caracteres")
    else:
        print("[ERROR] Token NO configurado")
        print("        Configura MOCEAN_API_TOKEN en el archivo .env")
        return False

    # 2. Verificar SDK
    try:
        from moceansdk import Client, Basic
        print("[OK] SDK de Mocean instalado correctamente")
    except ImportError:
        print("[ERROR] SDK de Mocean NO instalado")
        print("        Instala con: pip install moceansdk")
        return False

    # 3. Verificar dotenv
    try:
        import dotenv
        print("[OK] python-dotenv instalado correctamente")
    except ImportError:
        print("[AVISO] python-dotenv no instalado")
        print("        Instala con: pip install python-dotenv")

    print("\n" + "="*60)
    print("CONFIGURACION CORRECTA [OK]")
    print("="*60 + "\n")
    return True

def test_envio_sms():
    """Probar envio de SMS de prueba"""
    print("\n" + "="*60)
    print("TEST DE ENVIO DE SMS")
    print("="*60 + "\n")

    print("[INFO] Para probar el envio de SMS real:")
    print("       1. Ingresa un numero de telefono con codigo de pais")
    print("       2. Ejemplo: +521234567890 (Mexico)")
    print("       3. El SMS se enviara usando tu cuenta de Mocean\n")

    telefono = input("Ingresa numero de telefono (o 'skip' para saltar): ").strip()

    if telefono.lower() == 'skip' or not telefono:
        print("\n[INFO] Prueba de envio omitida\n")
        return

    from datetime import datetime
    mensaje = f"""ALERTA PRUEBA - RAPPI SAFE

Este es un mensaje de prueba del sistema de alertas.

Si recibes este SMS, tu configuracion de Mocean esta funcionando correctamente.

Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"""

    print(f"\n[INFO] Enviando SMS de prueba a {telefono}...")
    print(f"       Mensaje: {mensaje[:50]}...\n")

    resultado = enviar_sms_mocean(telefono, mensaje)

    if resultado['success']:
        print("\n[OK] SMS ENVIADO EXITOSAMENTE!")
        print(f"     Message ID: {resultado['respuesta'].get('msgid')}")
        print(f"     Receptor: {resultado['respuesta'].get('receiver')}")
    else:
        print("\n[ERROR] ERROR AL ENVIAR SMS:")
        print(f"        {resultado['error']}")

    print()

def mostrar_info_integracion():
    """Mostrar informacion sobre como funciona la integracion"""
    print("\n" + "="*60)
    print("INFORMACION DE INTEGRACION")
    print("="*60 + "\n")

    print("[INFO] Flujo de envio de notificaciones:\n")
    print("  1. Repartidor activa alerta de panico/accidente")
    print("  2. Sistema obtiene contactos de emergencia del repartidor")
    print("  3. Se envian SMS automaticamente via Mocean API\n")

    print("[INFO] Archivos importantes:\n")
    print("  * rappiSafe/utils.py (linea 494): enviar_sms_mocean()")
    print("  * rappiSafe/utils.py (linea 363): notificar_contactos_emergencia()")
    print("  * rappiSafe/utils.py (linea 590): enviar_notificacion_contacto()")
    print("  * .env: MOCEAN_API_TOKEN=tu_token_aqui\n")

    print("[INFO] Configuracion actual:\n")
    token = os.environ.get('MOCEAN_API_TOKEN', 'NO CONFIGURADO')
    print(f"  Token Mocean: {token[:30]}...")
    print(f"  Metodo de envio: SMS via Mocean API\n")

    print("[INFO] Recomendaciones:\n")
    print("  * Usa numeros con codigo de pais (+521234567890)")
    print("  * Verifica que los contactos esten validados en la BD")
    print("  * Revisa logs en consola al activar alertas")
    print("  * Mocean cobra por SMS enviado, monitorea tu cuenta\n")

def main():
    """Funcion principal del test"""
    print("\n" + "="*60)
    print("RAPPI SAFE - TEST DE MOCEAN API")
    print("="*60 + "\n")

    # 1. Verificar configuracion
    if not test_configuracion():
        print("\n[ERROR] Hay problemas con la configuracion. Revisa los errores arriba.\n")
        return

    # 2. Mostrar informacion
    mostrar_info_integracion()

    # 3. Opcion de prueba de envio
    respuesta = input("Deseas probar el envio de un SMS real? (s/n): ").strip().lower()
    if respuesta == 's':
        test_envio_sms()

    print("\n" + "="*60)
    print("TEST COMPLETADO")
    print("="*60 + "\n")
    print("[OK] Todo listo para usar Mocean API")
    print("[INFO] Los SMS se enviaran automaticamente cuando se activen alertas\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[AVISO] Test cancelado por el usuario\n")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}\n")
