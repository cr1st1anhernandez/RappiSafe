"""
Script de prueba para verificar el envío de SMS con MoceanAPI

Uso:
    python test_sms_mocean.py

Requisitos:
    - Tener el archivo .env configurado con MOCEAN_API_TOKEN
    - Tener instalado moceansdk (pip install moceansdk)
"""

import os
import sys
import io
from dotenv import load_dotenv

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Cargar variables de entorno
load_dotenv()

def test_sms_mocean():
    """Probar el envío de SMS con MoceanAPI"""

    # Verificar que el token esté configurado
    api_token = os.environ.get('MOCEAN_API_TOKEN')

    if not api_token:
        print("❌ ERROR: No se encontró MOCEAN_API_TOKEN en el archivo .env")
        print("   Por favor, configura tu token en el archivo .env")
        return False

    print("✅ Token de MoceanAPI encontrado")
    print(f"   Token: {api_token[:10]}...")

    # Solicitar número de teléfono
    print("\n📱 Ingresa el número de teléfono para enviar el SMS de prueba")
    print("   Formato internacional sin +, ejemplo: 60123456789")
    telefono = input("   Número: ").strip()

    if not telefono:
        print("❌ Número de teléfono vacío")
        return False

    # Mensaje de prueba
    mensaje = "ALERTA RAPPI SAFE: Este es un mensaje de prueba del sistema de alertas. Si recibes este mensaje, el sistema esta funcionando correctamente."

    try:
        from moceansdk import Client, Basic

        print(f"\n📤 Enviando SMS de prueba...")
        print(f"   Destinatario: {telefono}")
        print(f"   Mensaje: {mensaje[:50]}...")

        # Limpiar el número de teléfono
        telefono_limpio = ''.join(filter(str.isdigit, str(telefono)))

        # Inicializar cliente
        mocean = Client(Basic(api_token=api_token))

        # Enviar SMS
        res = mocean.sms.create({
            "mocean-from": "RAPPI SAFE",
            "mocean-to": telefono_limpio,
            "mocean-text": mensaje
        }).send()

        # Verificar respuesta
        print("\n📥 Respuesta de MoceanAPI:")
        print(f"   {res}")

        if res and 'messages' in res:
            messages = res['messages']
            if messages and len(messages) > 0:
                status = messages[0].get('status')

                if status == 0:
                    print("\n✅ ¡SMS ENVIADO EXITOSAMENTE!")
                    print(f"   Message ID: {messages[0].get('msgid')}")
                    print(f"   Receptor: {messages[0].get('receiver')}")
                    print("\n🎉 La integración con MoceanAPI está funcionando correctamente")
                    return True
                else:
                    error_msg = messages[0].get('err_msg', 'Error desconocido')
                    print(f"\n❌ ERROR: {error_msg}")
                    return False

        print("\n❌ Respuesta inválida de MoceanAPI")
        return False

    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DE ENVIO DE SMS CON MOCEANAPI")
    print("=" * 60)

    resultado = test_sms_mocean()

    print("\n" + "=" * 60)
    if resultado:
        print("✅ TEST EXITOSO")
        sys.exit(0)
    else:
        print("❌ TEST FALLIDO")
        sys.exit(1)
