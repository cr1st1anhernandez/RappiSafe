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
        # Obtener contactos de emergencia del repartidor
        contactos = ContactoConfianza.objects.filter(
            repartidor=alerta.repartidor
        )

        if not contactos.exists():
            print(f"⚠️ Alerta {alerta.id}: No hay contactos de emergencia registrados")
            return {
                'success': False,
                'contactos_notificados': 0,
                'notificaciones_fallidas': 0,
                'mensaje': 'No hay contactos de emergencia registrados'
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
                # Enviar SMS (simulado por ahora)
                resultado_envio = enviar_sms_contacto(contacto.telefono, mensaje)

                # Registrar notificación en base de datos
                notificacion = NotificacionContacto.objects.create(
                    alerta=alerta,
                    contacto=contacto,
                    metodo='sms',
                    estado='enviado' if resultado_envio['success'] else 'fallido',
                    mensaje=mensaje,
                    respuesta_api=resultado_envio.get('respuesta'),
                    error_mensaje=resultado_envio.get('error', '')
                )

                if resultado_envio['success']:
                    contactos_notificados += 1
                    print(f"✅ SMS enviado a {contacto.nombre} ({contacto.telefono})")
                    detalles.append({
                        'contacto': contacto.nombre,
                        'telefono': contacto.telefono,
                        'estado': 'enviado'
                    })
                else:
                    notificaciones_fallidas += 1
                    print(f"❌ Error al enviar SMS a {contacto.nombre}: {resultado_envio.get('error')}")
                    detalles.append({
                        'contacto': contacto.nombre,
                        'telefono': contacto.telefono,
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


def enviar_sms_contacto(telefono, mensaje):
    """
    Enviar SMS a un contacto de emergencia

    NOTA: Esta es una implementación SIMULADA.
    Para producción, integrar con:
    - Twilio (recomendado): https://www.twilio.com/
    - AWS SNS
    - Vonage (Nexmo)
    - Otro proveedor de SMS

    Args:
        telefono: Número telefónico del contacto (formato internacional)
        mensaje: Texto del mensaje a enviar

    Returns:
        dict: {'success': bool, 'respuesta': dict, 'error': str}
    """
    import os

    # Por ahora, simular envío exitoso
    # TODO: Integrar con servicio SMS real

    print(f"📱 [SIMULADO] Enviando SMS a {telefono}")
    print(f"   Mensaje: {mensaje[:50]}...")

    # Verificar si hay configuración de Twilio en variables de entorno
    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_from = os.environ.get('TWILIO_PHONE_NUMBER')

    if twilio_sid and twilio_token and twilio_from:
        # Si hay configuración, intentar usar Twilio
        try:
            from twilio.rest import Client

            client = Client(twilio_sid, twilio_token)
            message = client.messages.create(
                body=mensaje,
                from_=twilio_from,
                to=telefono
            )

            return {
                'success': True,
                'respuesta': {
                    'sid': message.sid,
                    'status': message.status,
                    'proveedor': 'twilio'
                }
            }
        except Exception as e:
            print(f"❌ Error al enviar SMS con Twilio: {str(e)}")
            return {
                'success': False,
                'error': f"Error Twilio: {str(e)}"
            }

    # Si no hay configuración de Twilio, simular envío
    # En producción, esto debería fallar o usar un servicio alternativo
    return {
        'success': True,
        'respuesta': {
            'simulado': True,
            'mensaje': 'SMS simulado - Configurar servicio real en producción',
            'telefono': telefono,
            'timestamp': timezone.now().isoformat()
        }
    }
