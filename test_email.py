"""
Script para probar conexión de email
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 60)
print("🧪 PRUEBA DE CONFIGURACIÓN DE EMAIL")
print("=" * 60)

print(f"\n📧 Configuración actual:")
print(f"   Host: {settings.EMAIL_HOST}")
print(f"   Puerto: {settings.EMAIL_PORT}")
print(f"   Usuario: {settings.EMAIL_HOST_USER}")
print(f"   Contraseña: {'***' + settings.EMAIL_HOST_PASSWORD[-4:] if settings.EMAIL_HOST_PASSWORD else 'NO CONFIGURADA'}")
print(f"   TLS: {settings.EMAIL_USE_TLS}")

if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
    print("\n❌ ERROR: EMAIL_HOST_USER o EMAIL_HOST_PASSWORD no están configurados")
    print("\n✅ Solución:")
    print("   1. Edita el archivo .env")
    print("   2. Agrega:")
    print("      EMAIL_HOST_USER=tu_email@gmail.com")
    print("      EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion")
    sys.exit(1)

print(f"\n📤 Intentando enviar email de prueba a: {settings.EMAIL_HOST_USER}")

try:
    import smtplib
    import ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Crear mensaje
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = settings.EMAIL_HOST_USER
    msg['Subject'] = '🧪 Prueba de RappiSafe'
    msg.attach(MIMEText('Este es un email de prueba del sistema RappiSafe.\n\nSi recibiste este mensaje, la configuración está correcta! ✅', 'plain', 'utf-8'))

    # Crear contexto SSL sin verificar certificados (para desarrollo en Windows)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # Conectar y enviar
    print("   → Conectando al servidor SMTP...")
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
    print("   → Iniciando TLS...")
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    print("   → Autenticando...")
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    print("   → Enviando mensaje...")
    server.send_message(msg)
    server.quit()

    print("\n✅ ¡EMAIL ENVIADO EXITOSAMENTE!")
    print(f"   Revisa tu bandeja de entrada: {settings.EMAIL_HOST_USER}")
    print("\n🎉 La configuración de email funciona correctamente")
except Exception as e:
    print(f"\n❌ ERROR al enviar email:")
    print(f"   {type(e).__name__}: {str(e)}")

    print("\n🔧 Posibles soluciones:")

    if "Authentication failed" in str(e) or "535" in str(e):
        print("\n   1. CONTRASEÑA INCORRECTA:")
        print("      - Ve a: https://myaccount.google.com/apppasswords")
        print("      - Genera una nueva 'Contraseña de aplicación'")
        print("      - Cópiala SIN espacios en EMAIL_HOST_PASSWORD")
        print("      - La contraseña debe tener 16 caracteres")

    elif "10061" in str(e) or "Connection refused" in str(e):
        print("\n   1. FIREWALL/ANTIVIRUS:")
        print("      - Desactiva temporalmente el firewall/antivirus")
        print("      - Permite Python en el firewall")

        print("\n   2. USAR PUERTO ALTERNATIVO:")
        print("      - Cambia en .env:")
        print("        EMAIL_PORT=465")
        print("        EMAIL_USE_TLS=False")
        print("        EMAIL_USE_SSL=True")

    elif "timed out" in str(e):
        print("\n   1. PROBLEMA DE RED:")
        print("      - Verifica tu conexión a internet")
        print("      - Intenta con otra red WiFi")
        print("      - Desactiva VPN si tienes una")

    else:
        print("\n   1. VERIFICA:")
        print("      - Que el email sea correcto")
        print("      - Que la contraseña sea una 'App Password' de Gmail")
        print("      - Que tengas conexión a internet")

print("\n" + "=" * 60)
