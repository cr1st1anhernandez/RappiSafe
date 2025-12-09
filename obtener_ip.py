# -*- coding: utf-8 -*-
"""
Script para obtener la IP local de la computadora
"""
import socket

def obtener_ip_local():
    try:
        # Crear un socket UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Conectar a una direccion externa (no envia datos)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "No se pudo obtener la IP"

print("=" * 60)
print("ACCEDER A RAPPISAFE DESDE TU TELEFONO")
print("=" * 60)

ip = obtener_ip_local()

print(f"\nTu IP local es: {ip}")
print(f"\nEn tu telefono, abre el navegador y ve a:")
print(f"\n   http://{ip}:8001")
print(f"\n   o tambien:")
print(f"\n   http://{ip}:8001/login/")

print("\nIMPORTANTE:")
print("   1. Tu telefono debe estar en la MISMA red WiFi que tu computadora")
print("   2. El servidor debe estar corriendo (daphne -b 0.0.0.0 -p 8001 mysite.asgi:application)")
print("   3. Si no funciona, desactiva el firewall temporalmente")

print("\nPRUEBA:")
print("   - Notificaciones de ubicacion GPS")
print("   - Deteccion de agitacion del telefono")
print("   - Boton SOS")
print("   - Alertas por Telegram y Email")

print("\n" + "=" * 60)
