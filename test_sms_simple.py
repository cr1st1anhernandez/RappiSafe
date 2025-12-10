# -*- coding: utf-8 -*-
"""Script simple de prueba para MoceanAPI"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_sms():
    api_token = os.environ.get('MOCEAN_API_TOKEN')

    if not api_token:
        print("ERROR: No se encontro MOCEAN_API_TOKEN en .env")
        return False

    print("Token encontrado:", api_token[:15] + "...")

    telefono = input("Ingresa el numero de telefono (formato: 60123456789): ").strip()

    if not telefono:
        print("Numero vacio")
        return False

    try:
        from moceansdk import Client, Basic

        print("Enviando SMS a:", telefono)

        mensaje = "ALERTA RAPPI SAFE: Mensaje de prueba del sistema."

        mocean = Client(Basic(api_token=api_token))

        res = mocean.sms.create({
            "mocean-from": "RAPPI SAFE",
            "mocean-to": telefono,
            "mocean-text": mensaje
        }).send()

        print("Respuesta:", res)

        if res and 'messages' in res:
            messages = res['messages']
            if messages and len(messages) > 0:
                status = messages[0].get('status')

                if status == 0:
                    print("EXITO! SMS enviado")
                    print("Message ID:", messages[0].get('msgid'))
                    print("Receptor:", messages[0].get('receiver'))
                    return True
                else:
                    print("ERROR:", messages[0].get('err_msg'))
                    return False

        print("Respuesta invalida")
        return False

    except Exception as e:
        print("EXCEPCION:", str(e))
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TEST DE SMS CON MOCEANAPI")
    print("=" * 50)
    resultado = test_sms()
    print("=" * 50)
    print("RESULTADO:", "EXITOSO" if resultado else "FALLIDO")
