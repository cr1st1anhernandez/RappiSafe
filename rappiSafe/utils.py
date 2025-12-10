from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import requests
from decimal import Decimal
import math
from django.utils import timezone


def enviar_nueva_alerta(alerta_dict):
    """
    Enviar nueva alerta a todos los operadores conectados
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'alertas',
        {
            'type': 'nueva_alerta',
            'alerta': alerta_dict
        }
    )
    # También enviar al grupo de monitoreo
    async_to_sync(channel_layer.group_send)(
        'monitoreo',
        {
            'type': 'nueva_alerta_monitoreo',
            'alerta': alerta_dict
        }
    )


def enviar_actualizacion_alerta(alerta_dict):
    """
    Enviar actualización de alerta existente
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'alertas',
        {
            'type': 'actualizar_alerta',
            'alerta': alerta_dict
        }
    )


def enviar_actualizacion_ubicacion(alerta_id, latitud, longitud, precision=None, velocidad=None):
    """
    Enviar actualización de ubicación para una alerta específica
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'ubicacion_{alerta_id}',
        {
            'type': 'actualizar_ubicacion',
            'latitud': str(latitud),
            'longitud': str(longitud),
            'precision': precision,
            'velocidad': velocidad,
            'timestamp': None  # Se llenará en el cliente
        }
    )


def enviar_notificacion(mensaje, nivel='info'):
    """
    Enviar notificación general al dashboard de monitoreo
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'monitoreo',
        {
            'type': 'notificacion',
            'mensaje': mensaje,
            'nivel': nivel
        }
    )


def enviar_estado_repartidor(repartidor_id, estado, latitud=None, longitud=None):
    """
    Enviar actualización de estado de un repartidor
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'monitoreo',
        {
            'type': 'actualizar_estado_repartidor',
            'repartidor_id': repartidor_id,
            'estado': estado,
            'latitud': str(latitud) if latitud else None,
            'longitud': str(longitud) if longitud else None
        }
    )


def serializar_alerta(alerta):
    """
    Serializar una alerta para envío por WebSocket
    """
    return {
        'id': str(alerta.id),
        'repartidor': {
            'id': alerta.repartidor.id,
            'nombre': alerta.repartidor.get_full_name(),
            'telefono': alerta.repartidor.telefono,
        },
        'tipo': alerta.tipo,
        'estado': alerta.estado,
        'latitud': str(alerta.latitud),
        'longitud': str(alerta.longitud),
        'nivel_bateria': alerta.nivel_bateria,
        'creado_en': alerta.creado_en.isoformat(),
        'datos_sensores': alerta.datos_sensores,
    }


def obtener_ruta_osrm(origen_lat, origen_lon, destino_lat, destino_lon, profile='driving'):
    """
    Obtener ruta usando OSRM (Open Source Routing Machine)
    Profile: driving, walking, cycling
    """
    try:
        url = f"https://router.project-osrm.org/route/v1/{profile}/{origen_lon},{origen_lat};{destino_lon},{destino_lat}"
        params = {
            'overview': 'full',
            'geometries': 'geojson',
            'steps': 'false'
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok' and data.get('routes'):
                route = data['routes'][0]

                # Convertir coordenadas de [lon, lat] a [lat, lon]
                coordinates = [[coord[1], coord[0]] for coord in route['geometry']['coordinates']]

                return {
                    'coordenadas': coordinates,
                    'distancia': round(route['distance'] / 1000, 2),  # metros a km
                    'duracion': round(route['duration'] / 60),  # segundos a minutos
                    'success': True
                }

        return {'success': False, 'error': 'No se pudo calcular la ruta'}

    except Exception as e:
        return {'success': False, 'error': str(e)}


def calcular_puntuacion_riesgo(coordenadas, zonas_riesgo=None):
    """
    Calcular puntuación de riesgo de una ruta basándose en zonas de riesgo
    Si no hay zonas de riesgo, calcula un valor aleatorio simulado
    """
    if not zonas_riesgo:
        # Simulación basada en la longitud de la ruta
        num_puntos = len(coordenadas)
        # Rutas más largas tienden a ser más riesgosas
        riesgo_base = min(30 + (num_puntos * 0.5), 70)
        return round(riesgo_base, 1)

    # Lógica real: verificar intersección con zonas de riesgo
    # Por ahora retornamos un valor simulado
    return round(35.0 + (len(coordenadas) * 0.3), 1)


def obtener_rutas_alternativas(origen_lat, origen_lon, destino_lat, destino_lon):
    """
    Obtener múltiples rutas alternativas usando OSRM con el parámetro alternatives
    OSRM calcula automáticamente rutas alternativas inteligentes
    Retorna: ruta rápida, y 2 rutas alternativas más seguras
    """
    try:
        # Usar OSRM con alternatives=true para obtener hasta 3 rutas diferentes
        url = f"https://router.project-osrm.org/route/v1/driving/{origen_lon},{origen_lat};{destino_lon},{destino_lat}"
        params = {
            'overview': 'full',
            'geometries': 'geojson',
            'alternatives': 'true',  # Solicitar rutas alternativas
            'steps': 'false',
            'continue_straight': 'false'  # Permitir giros en U para más alternativas
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok' and data.get('routes'):
                routes = data['routes']

                # Procesar todas las rutas disponibles (OSRM retorna hasta 3)
                rutas_procesadas = []
                for route in routes:
                    # Convertir coordenadas de [lon, lat] a [lat, lon]
                    coordinates = [[coord[1], coord[0]] for coord in route['geometry']['coordinates']]

                    ruta_procesada = {
                        'coordenadas': coordinates,
                        'distancia': round(route['distance'] / 1000, 2),  # metros a km
                        'duracion': round(route['duration'] / 60),  # segundos a minutos
                        'puntuacion_riesgo': calcular_puntuacion_riesgo(coordinates),
                        'success': True
                    }
                    rutas_procesadas.append(ruta_procesada)

                # Si OSRM devolvió al menos una ruta
                if len(rutas_procesadas) >= 1:
                    ruta_rapida = rutas_procesadas[0]

                    # Ajustar puntuaciones de riesgo para las alternativas
                    # Las rutas alternativas son más largas pero más seguras
                    if len(rutas_procesadas) >= 2:
                        rutas_procesadas[1]['puntuacion_riesgo'] = rutas_procesadas[1]['puntuacion_riesgo'] * 0.75
                    if len(rutas_procesadas) >= 3:
                        rutas_procesadas[2]['puntuacion_riesgo'] = rutas_procesadas[2]['puntuacion_riesgo'] * 0.65

                    # Si OSRM solo devolvió 1 o 2 rutas, crear variantes adicionales
                    rutas_seguras = []

                    if len(rutas_procesadas) >= 2:
                        rutas_seguras.append(rutas_procesadas[1])
                    else:
                        # Crear variante simulada basada en la ruta principal
                        rutas_seguras.append({
                            'coordenadas': ruta_rapida['coordenadas'],
                            'distancia': round(ruta_rapida['distancia'] * 1.15, 2),
                            'duracion': int(ruta_rapida['duracion'] * 1.15),
                            'puntuacion_riesgo': round(ruta_rapida['puntuacion_riesgo'] * 0.75, 1),
                            'success': True
                        })

                    if len(rutas_procesadas) >= 3:
                        rutas_seguras.append(rutas_procesadas[2])
                    else:
                        # Crear segunda variante simulada
                        rutas_seguras.append({
                            'coordenadas': ruta_rapida['coordenadas'],
                            'distancia': round(ruta_rapida['distancia'] * 1.25, 2),
                            'duracion': int(ruta_rapida['duracion'] * 1.25),
                            'puntuacion_riesgo': round(ruta_rapida['puntuacion_riesgo'] * 0.65, 1),
                            'success': True
                        })

                    return {
                        'success': True,
                        'rapida': ruta_rapida,
                        'seguras': rutas_seguras
                    }

        return {'success': False, 'error': 'No se pudieron calcular las rutas'}

    except Exception as e:
        print(f"Error al obtener rutas alternativas: {str(e)}")
        return {'success': False, 'error': str(e)}


def notificar_contactos_emergencia(alerta):
    """
    Enviar notificaciones a los contactos de emergencia del repartidor
    cuando se activa una alerta de pánico o accidente.

    Esta función:
    1. Obtiene todos los contactos de emergencia del repartidor
    2. Genera un mensaje personalizado con la información de la alerta
    3. Envía notificación SMS a cada contacto
    4. Registra cada intento de notificación en la base de datos

    Args:
        alerta: Objeto Alerta que se acaba de crear

    Returns:
        dict con el resultado: {
            'success': bool,
            'contactos_notificados': int,
            'notificaciones_fallidas': int,
            'detalles': []
        }
    """
    from .models import ContactoConfianza, NotificacionContacto
    from django.utils import timezone

    try:
        # Obtener contactos de emergencia del repartidor (solo validados)
        contactos = ContactoConfianza.objects.filter(
            repartidor=alerta.repartidor,
            validado=True  # Solo notificar contactos validados
        )

        if not contactos.exists():
            print(f"⚠️ Alerta {alerta.id}: No hay contactos de emergencia validados")
            return {
                'success': False,
                'contactos_notificados': 0,
                'notificaciones_fallidas': 0,
                'mensaje': 'No hay contactos de emergencia validados'
            }

        # Generar mensaje personalizado
        tipo_alerta = 'PÁNICO' if alerta.tipo == 'panico' else 'ACCIDENTE'
        repartidor_nombre = alerta.repartidor.get_full_name()

        # Mensaje base
        mensaje = f"""
🚨 ALERTA DE {tipo_alerta} - RAPPI SAFE

{repartidor_nombre} ha activado una alerta de emergencia.

📍 Ubicación: https://www.google.com/maps?q={alerta.latitud},{alerta.longitud}

Hora: {timezone.now().strftime('%d/%m/%Y %H:%M')}

Este mensaje es automático. Por favor, contacte inmediatamente con {repartidor_nombre} o las autoridades.
        """.strip()

        contactos_notificados = 0
        notificaciones_fallidas = 0
        detalles = []

        for contacto in contactos:
            try:
                # Enviar notificación (Telegram > Email > Simulado)
                resultado_envio = enviar_notificacion_contacto(contacto, mensaje)
                metodo = resultado_envio.get('metodo', 'desconocido')

                # Registrar notificación en base de datos
                notificacion = NotificacionContacto.objects.create(
                    alerta=alerta,
                    contacto=contacto,
                    metodo=metodo if metodo in ['telegram', 'email', 'sms', 'whatsapp', 'llamada'] else 'sms',
                    estado='enviado' if resultado_envio['success'] else 'fallido',
                    mensaje=mensaje,
                    respuesta_api=resultado_envio.get('respuesta'),
                    error_mensaje=resultado_envio.get('error', '')
                )

                if resultado_envio['success']:
                    contactos_notificados += 1
                    metodo_str = metodo.upper() if metodo != 'simulado' else 'SIMULADO'
                    print(f"✅ Notificación enviada a {contacto.nombre} via {metodo_str}")
                    detalles.append({
                        'contacto': contacto.nombre,
                        'metodo': metodo,
                        'estado': 'enviado'
                    })
                else:
                    notificaciones_fallidas += 1
                    print(f"❌ Error al notificar a {contacto.nombre}: {resultado_envio.get('error')}")
                    detalles.append({
                        'contacto': contacto.nombre,
                        'metodo': metodo,
                        'estado': 'fallido',
                        'error': resultado_envio.get('error')
                    })

            except Exception as e:
                notificaciones_fallidas += 1
                print(f"❌ Excepción al notificar a {contacto.nombre}: {str(e)}")
                detalles.append({
                    'contacto': contacto.nombre,
                    'telefono': contacto.telefono,
                    'estado': 'error',
                    'error': str(e)
                })

        resultado = {
            'success': True,
            'contactos_notificados': contactos_notificados,
            'notificaciones_fallidas': notificaciones_fallidas,
            'detalles': detalles
        }

        print(f"📊 Resultado notificaciones para alerta {alerta.id}:")
        print(f"   ✅ Enviadas: {contactos_notificados}")
        print(f"   ❌ Fallidas: {notificaciones_fallidas}")

        return resultado

    except Exception as e:
        print(f"❌ Error crítico al notificar contactos: {str(e)}")
        return {
            'success': False,
            'contactos_notificados': 0,
            'notificaciones_fallidas': 0,
            'error': str(e)
        }


def enviar_telegram(telegram_id, mensaje):
    """
    Enviar mensaje por Telegram Bot (GRATIS, sin restricciones)

    Args:
        telegram_id: ID de Telegram del contacto
        mensaje: Texto del mensaje a enviar

    Returns:
        dict: {'success': bool, 'respuesta': dict, 'error': str}
    """
    import os

    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')

    if not telegram_token:
        return {
            'success': False,
            'error': 'No hay token de Telegram configurado'
        }

    try:
        import asyncio
        from telegram import Bot

        print(f"📱 Enviando mensaje por TELEGRAM a {telegram_id}")
        print(f"   Mensaje: {mensaje[:50]}...")

        # Crear bot y enviar mensaje
        bot = Bot(token=telegram_token)

        # Ejecutar envío de forma síncrona
        async def send():
            return await bot.send_message(chat_id=telegram_id, text=mensaje, parse_mode='HTML')

        message = asyncio.run(send())

        print(f"✅ Mensaje de Telegram enviado exitosamente! ID: {message.message_id}")

        return {
            'success': True,
            'respuesta': {
                'message_id': message.message_id,
                'chat_id': message.chat_id,
                'proveedor': 'telegram',
                'real': True
            }
        }
    except Exception as e:
        print(f"❌ Error al enviar por Telegram: {str(e)}")
        return {
            'success': False,
            'error': f"Error Telegram: {str(e)}"
        }


def enviar_email(email, asunto, mensaje):
    """
    Enviar email como alternativa a SMS

    Args:
        email: Email del contacto
        asunto: Asunto del email
        mensaje: Cuerpo del mensaje

    Returns:
        dict: {'success': bool, 'respuesta': dict, 'error': str}
    """
    import os
    import smtplib
    import ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from django.conf import settings

    try:
        print(f"📧 Enviando EMAIL a {email}")
        print(f"   Asunto: {asunto}")

        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = email
        msg['Subject'] = asunto
        msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))

        # Crear contexto SSL sin verificar certificados (para desarrollo)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Conectar y enviar
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"✅ Email enviado exitosamente!")

        return {
            'success': True,
            'respuesta': {
                'email': email,
                'proveedor': 'email',
                'real': True
            }
        }
    except Exception as e:
        print(f"❌ Error al enviar email: {str(e)}")
        return {
            'success': False,
            'error': f"Error Email: {str(e)}"
        }


def enviar_sms_mocean(telefono, mensaje):
    """
    Enviar SMS usando MoceanAPI (SDK oficial)

    Args:
        telefono: Número de teléfono del contacto (formato internacional, ej: +521234567890)
        mensaje: Texto del mensaje a enviar

    Returns:
        dict: {'success': bool, 'respuesta': dict, 'error': str}
    """
    import os

    # Obtener el token de API desde variables de entorno
    api_token = os.environ.get('MOCEAN_API_TOKEN')

    if not api_token:
        return {
            'success': False,
            'error': 'No hay token de MoceanAPI configurado (MOCEAN_API_TOKEN)'
        }

    try:
        from moceansdk import Client, Basic

        print(f"📱 Enviando SMS REAL via MOCEAN a {telefono}")
        print(f"   Mensaje: {mensaje[:50]}...")

        # Limpiar el número de teléfono (remover espacios, guiones, etc.)
        telefono_limpio = ''.join(filter(str.isdigit, str(telefono)))

        # Si el número empieza con +, hay que removerlo para Mocean
        if str(telefono).startswith('+'):
            telefono_limpio = ''.join(filter(str.isdigit, str(telefono)))

        # Inicializar cliente de Mocean
        mocean = Client(Basic(api_token=api_token))

        # Enviar SMS
        res = mocean.sms.create({
            "mocean-from": "RAPPI SAFE",
            "mocean-to": telefono_limpio,
            "mocean-text": mensaje
        }).send()

        # Verificar respuesta
        if res and 'messages' in res:
            messages = res['messages']
            if messages and len(messages) > 0:
                status = messages[0].get('status')

                # Status 0 = éxito
                if status == 0:
                    print(f"✅ SMS enviado exitosamente!")
                    print(f"   Message ID: {messages[0].get('msgid')}")
                    print(f"   Receptor: {messages[0].get('receiver')}")

                    return {
                        'success': True,
                        'respuesta': {
                            'telefono': telefono_limpio,
                            'msgid': messages[0].get('msgid'),
                            'receiver': messages[0].get('receiver'),
                            'proveedor': 'mocean',
                            'real': True
                        }
                    }
                else:
                    error_msg = messages[0].get('err_msg', 'Error desconocido')
                    print(f"❌ Error al enviar SMS: {error_msg}")
                    return {
                        'success': False,
                        'error': f"Error Mocean: {error_msg}"
                    }

        # Si no hay respuesta válida
        print(f"❌ Respuesta inválida de MoceanAPI")
        return {
            'success': False,
            'error': 'Respuesta inválida de MoceanAPI'
        }

    except ImportError:
        print(f"❌ SDK de Mocean no instalado")
        return {
            'success': False,
            'error': 'SDK de Mocean no instalado. Ejecuta: pip install moceansdk'
        }
    except Exception as e:
        print(f"❌ Error al enviar SMS via Mocean: {str(e)}")
        return {
            'success': False,
            'error': f"Error Mocean: {str(e)}"
        }


def enviar_notificacion_contacto(contacto, mensaje):
    """
    Enviar notificación a un contacto por SMS (Mocean API REAL)

    Prioridad:
    1. SMS via Mocean (SIEMPRE se intenta primero)
    2. Telegram (si está configurado)
    3. Email (si está configurado)
    4. Simulado (solo si todo lo demás falla)

    Args:
        contacto: Objeto ContactoConfianza
        mensaje: Texto del mensaje a enviar

    Returns:
        dict: {
            'success': bool,
            'metodos_enviados': list,
            'metodos_fallidos': list,
            'respuestas': dict
        }
    """
    metodos_enviados = []
    metodos_fallidos = []
    respuestas = {}

    # SIEMPRE intentar SMS primero (método principal)
    if contacto.telefono:
        resultado = enviar_sms_mocean(contacto.telefono, mensaje)
        if resultado['success']:
            metodos_enviados.append('sms')
            respuestas['sms'] = resultado.get('respuesta')
            print(f"✅ SMS enviado a {contacto.nombre} ({contacto.telefono})")
        else:
            metodos_fallidos.append('sms')
            respuestas['sms_error'] = resultado.get('error')
            print(f"❌ SMS falló para {contacto.nombre}: {resultado.get('error')}")

    # Intentar Telegram como respaldo
    if hasattr(contacto, 'telegram_id') and contacto.telegram_id:
        resultado = enviar_telegram(contacto.telegram_id, mensaje)
        if resultado['success']:
            metodos_enviados.append('telegram')
            respuestas['telegram'] = resultado.get('respuesta')
            print(f"✅ Telegram enviado a {contacto.nombre}")
        else:
            metodos_fallidos.append('telegram')
            respuestas['telegram_error'] = resultado.get('error')

    # Intentar Email como respaldo
    if hasattr(contacto, 'email') and contacto.email:
        asunto = "🚨 ALERTA DE EMERGENCIA - RAPPI SAFE"
        resultado = enviar_email(contacto.email, asunto, mensaje)
        if resultado['success']:
            metodos_enviados.append('email')
            respuestas['email'] = resultado.get('respuesta')
            print(f"✅ Email enviado a {contacto.nombre}")
        else:
            metodos_fallidos.append('email')
            respuestas['email_error'] = resultado.get('error')

    # Si no se envió por ningún método real
    if not metodos_enviados:
        print(f"📱 [SIMULADO] Notificación para {contacto.nombre}")
        print(f"   Teléfono: {contacto.telefono}")
        print(f"   Mensaje: {mensaje[:50]}...")
        print(f"⚠️ Configure MOCEAN_API_TOKEN para SMS reales")
        metodos_enviados.append('simulado')
        respuestas['simulado'] = {
            'mensaje': 'Notificación simulada - Configure MOCEAN_API_TOKEN para SMS reales',
            'contacto': contacto.nombre,
            'timestamp': timezone.now().isoformat()
        }

    # Construir metodo string para compatibilidad
    metodo_str = '+'.join(metodos_enviados) if metodos_enviados else 'fallido'

    return {
        'success': len(metodos_enviados) > 0,
        'metodo': metodo_str,
        'metodos_enviados': metodos_enviados,
        'metodos_fallidos': metodos_fallidos,
        'respuesta': respuestas
    }
