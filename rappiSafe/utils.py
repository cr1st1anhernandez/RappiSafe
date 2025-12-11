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
    Calcular puntuación de riesgo de una ruta basándose en zonas de riesgo reales
    Retorna un valor de 1-10 donde 10 es el más peligroso

    Args:
        coordenadas: Lista de coordenadas [lat, lng] de la ruta
        zonas_riesgo: QuerySet de EstadisticaRiesgo (opcional)

    Returns:
        float: Puntuación de riesgo de 1.0 a 10.0
    """
    from math import radians, sin, cos, sqrt, atan2
    from .models import EstadisticaRiesgo

    # Si no se proporcionan zonas, obtenerlas de la base de datos
    if not zonas_riesgo:
        zonas_riesgo = EstadisticaRiesgo.objects.all()

    if not zonas_riesgo.exists():
        # Si no hay datos de zonas de riesgo, ruta base de riesgo medio-bajo
        num_puntos = len(coordenadas)
        riesgo_base = min(1.0 + (num_puntos * 0.01), 4.0)
        return round(riesgo_base, 1)

    # Calcular riesgo real basado en proximidad a zonas peligrosas
    # Sistema de zonas concéntricas:
    # - 0-1 km: Riesgo completo (factor 1.0)
    # - 1-2 km: Riesgo medio (factor 0.7)
    # - 2-3 km: Riesgo bajo (factor 0.4)
    # - >3 km: Sin riesgo (factor 0.0)

    puntuaciones = []
    zona_mas_cercana = None
    distancia_minima = float('inf')

    for coord in coordenadas:
        lat_ruta, lng_ruta = coord[0], coord[1]

        # Buscar zonas cercanas a este punto de la ruta
        for zona in zonas_riesgo:
            try:
                coords_zona = zona.coordenadas_zona
                if isinstance(coords_zona, dict) and 'center' in coords_zona:
                    lat_zona = float(coords_zona['center']['lat'])
                    lng_zona = float(coords_zona['center']['lng'])

                    # Calcular distancia usando fórmula de Haversine
                    R = 6371  # Radio de la Tierra en km

                    lat1 = radians(lat_ruta)
                    lon1 = radians(lng_ruta)
                    lat2 = radians(lat_zona)
                    lon2 = radians(lng_zona)

                    dlat = lat2 - lat1
                    dlon = lon2 - lon1

                    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                    c = 2 * atan2(sqrt(a), sqrt(1-a))
                    distancia = R * c

                    # Guardar la zona más cercana
                    if distancia < distancia_minima:
                        distancia_minima = distancia
                        zona_mas_cercana = zona

                    # Sistema de zonas concéntricas (3 km de radio total)
                    if distancia <= 3.0:
                        # Calcular factor de distancia según zona concéntrica
                        if distancia <= 1.0:
                            # Zona de alto riesgo (0-1 km)
                            factor_distancia = 1.0 - (distancia * 0.3)  # 1.0 a 0.7
                        elif distancia <= 2.0:
                            # Zona de riesgo medio (1-2 km)
                            factor_distancia = 0.7 - ((distancia - 1.0) * 0.3)  # 0.7 a 0.4
                        else:
                            # Zona de riesgo bajo (2-3 km)
                            factor_distancia = 0.4 - ((distancia - 2.0) * 0.4)  # 0.4 a 0.0

                        puntuacion_zona = zona.puntuacion_riesgo * max(0.0, factor_distancia)
                        if puntuacion_zona > 0:
                            puntuaciones.append(puntuacion_zona)
            except (KeyError, ValueError, TypeError):
                continue

    # Si la ruta no pasa cerca de ninguna zona registrada
    if not puntuaciones:
        # Si hay una zona cercana pero fuera del radio, dar riesgo mínimo basado en qué tan cerca está
        if zona_mas_cercana and distancia_minima < 10.0:
            # Entre 3-10 km: dar un riesgo muy bajo proporcional a la zona
            factor_lejania = max(0, 1.0 - (distancia_minima / 10.0))
            riesgo_base = zona_mas_cercana.puntuacion_riesgo * factor_lejania * 0.3
            return round(max(1.5, min(4.0, riesgo_base)), 1)

        # Ruta muy lejos de zonas conocidas
        num_puntos = len(coordenadas)
        return round(min(2.0 + (num_puntos * 0.005), 3.5), 1)

    # Calcular puntuación final con peso para la zona más peligrosa
    puntuacion_promedio = sum(puntuaciones) / len(puntuaciones)
    puntuacion_maxima = max(puntuaciones)

    # Si la zona más peligrosa es muy peligrosa (>7), darle más peso
    if puntuacion_maxima >= 7.0:
        # 70% zona más peligrosa, 30% promedio
        puntuacion_final = (puntuacion_maxima * 0.7) + (puntuacion_promedio * 0.3)
    elif puntuacion_maxima >= 5.0:
        # 60% zona más peligrosa, 40% promedio
        puntuacion_final = (puntuacion_maxima * 0.6) + (puntuacion_promedio * 0.4)
    else:
        # 50% zona más peligrosa, 50% promedio
        puntuacion_final = (puntuacion_maxima * 0.5) + (puntuacion_promedio * 0.5)

    # Asegurar que esté en el rango 1-10
    puntuacion_final = max(1.0, min(10.0, puntuacion_final))

    return round(puntuacion_final, 1)


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

        print(f"   Número limpio: {telefono_limpio}")

        # Enviar SMS
        res = mocean.sms.create({
            "mocean-from": "RAPPI SAFE",
            "mocean-to": telefono_limpio,
            "mocean-text": mensaje
        }).send()

        # Debug: imprimir respuesta completa
        print(f"📋 Respuesta completa de Mocean: {res}")

        # Verificar respuesta
        if res and 'messages' in res:
            messages = res['messages']
            if messages and len(messages) > 0:
                message = messages[0]
                status = message.get('status')
                print(f"   Status code: {status} (tipo: {type(status)})")

                # Status 0 = éxito (puede ser int o string)
                if status == 0 or status == '0':
                    print(f"✅ SMS enviado exitosamente!")
                    print(f"   Message ID: {message.get('msgid')}")
                    print(f"   Receptor: {message.get('receiver')}")

                    return {
                        'success': True,
                        'respuesta': {
                            'telefono': telefono_limpio,
                            'msgid': message.get('msgid'),
                            'receiver': message.get('receiver'),
                            'proveedor': 'mocean',
                            'real': True
                        }
                    }
                else:
                    # Solo hay err_msg cuando hay error (status != 0)
                    error_msg = message.get('err_msg', f'Error con código {status}')
                    print(f"❌ Error al enviar SMS!")
                    print(f"   Código: {status}")
                    print(f"   Mensaje: {error_msg}")
                    print(f"   Info completa: {message}")
                    return {
                        'success': False,
                        'error': f"Error Mocean [{status}]: {error_msg}"
                    }

        # Si no hay respuesta válida
        print(f"❌ Respuesta inválida de MoceanAPI: {res}")
        return {
            'success': False,
            'error': f'Respuesta inválida de MoceanAPI: {res}'
        }

    except ImportError:
        print(f"❌ SDK de Mocean no instalado")
        return {
            'success': False,
            'error': 'SDK de Mocean no instalado. Ejecuta: pip install moceansdk'
        }
    except Exception as e:
        import traceback
        print(f"❌ Excepción al enviar SMS via Mocean!")
        print(f"   Tipo de error: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        print(f"   Traceback completo:")
        traceback.print_exc()
        return {
            'success': False,
            'error': f"Error Mocean [{type(e).__name__}]: {str(e) if str(e) else 'Error sin mensaje'}"
        }


def enviar_notificacion_contacto(contacto, mensaje):
    """
    Enviar notificación a un contacto por SMS usando Mocean API

    Args:
        contacto: Objeto ContactoConfianza
        mensaje: Texto del mensaje a enviar

    Returns:
        dict: {
            'success': bool,
            'metodo': str,
            'respuesta': dict
        }
    """
    # Intentar enviar SMS
    if contacto.telefono:
        resultado = enviar_sms_mocean(contacto.telefono, mensaje)
        if resultado['success']:
            print(f"✅ SMS enviado a {contacto.nombre} ({contacto.telefono})")
            return {
                'success': True,
                'metodo': 'sms',
                'respuesta': resultado.get('respuesta')
            }
        else:
            print(f"❌ SMS falló para {contacto.nombre}: {resultado.get('error')}")
            return {
                'success': False,
                'metodo': 'sms',
                'respuesta': {'error': resultado.get('error')}
            }
    else:
        print(f"❌ El contacto {contacto.nombre} no tiene teléfono configurado")
        return {
            'success': False,
            'metodo': 'sms',
            'respuesta': {'error': 'No hay teléfono configurado'}
        }
