from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator
from datetime import timedelta, datetime, date
import json
import uuid

from .models import (
    User, RepartidorProfile, Alerta, Trayectoria, ContactoConfianza,
    Incidente, Bitacora, EstadisticaRiesgo, SolicitudAyudaPsicologica, RutaSegura
)
from .utils import (
    enviar_nueva_alerta, enviar_actualizacion_alerta,
    enviar_actualizacion_ubicacion, serializar_alerta, enviar_notificacion
)


# ==================== AUTENTICACIÓN ====================

def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.activo:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciales inválidas o cuenta inactiva')

    return render(request, 'registration/login.html')


@login_required
def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('login')


@login_required
def dashboard(request):
    """
    Vista del dashboard principal que redirige según el rol del usuario
    """
    user = request.user

    if user.rol == 'repartidor':
        return redirect('repartidor_home')
    elif user.rol == 'operador':
        return redirect('operador_dashboard')
    elif user.rol == 'administrador':
        return redirect('admin_dashboard')
    else:
        messages.error(request, 'Rol no reconocido')
        return redirect('login')


# ==================== VERIFICADORES DE ROLES ====================

def es_repartidor(user):
    return user.is_authenticated and user.rol == 'repartidor'


def es_operador(user):
    return user.is_authenticated and user.rol == 'operador'


def es_administrador(user):
    return user.is_authenticated and user.rol == 'administrador'


# ==================== VISTAS REPARTIDOR ====================

def test_sensores(request):
    """Página de prueba de sensores GPS y movimiento (sin login)"""
    return render(request, 'rappiSafe/test_sensores.html')


@login_required
@user_passes_test(es_repartidor, login_url='login')
def repartidor_home(request):
    """Página principal del repartidor con botón de pánico"""
    from math import radians, sin, cos, sqrt, atan2

    perfil = request.user.perfil_repartidor
    alertas_activas = Alerta.objects.filter(
        repartidor=request.user,
        estado__in=['pendiente', 'en_atencion']
    ).order_by('-creado_en')

    # Calcular zonas de riesgo cercanas basadas en la ubicación del repartidor
    zonas_riesgo_cercanas = []
    if perfil.ultima_latitud and perfil.ultima_longitud:
        # Obtener todas las zonas de riesgo
        zonas_riesgo = EstadisticaRiesgo.objects.all().order_by('-puntuacion_riesgo')[:10]

        # Calcular distancia a cada zona
        for zona in zonas_riesgo:
            try:
                # Las coordenadas están en formato GeoJSON
                coords = zona.coordenadas_zona
                # Asumiendo que coords tiene 'center' con lat y lng
                if isinstance(coords, dict) and 'center' in coords:
                    zona_lat = float(coords['center']['lat'])
                    zona_lng = float(coords['center']['lng'])

                    # Fórmula de Haversine para calcular distancia
                    R = 6371  # Radio de la Tierra en km

                    lat1 = radians(float(perfil.ultima_latitud))
                    lon1 = radians(float(perfil.ultima_longitud))
                    lat2 = radians(zona_lat)
                    lon2 = radians(zona_lng)

                    dlat = lat2 - lat1
                    dlon = lon2 - lon1

                    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                    c = 2 * atan2(sqrt(a), sqrt(1-a))
                    distancia = R * c

                    # Solo mostrar zonas dentro de 10 km
                    if distancia <= 10:
                        zonas_riesgo_cercanas.append({
                            'zona': zona,
                            'distancia': round(distancia, 1)
                        })
            except (KeyError, ValueError, TypeError) as e:
                # Si hay error con las coordenadas, ignorar esta zona
                continue

        # Ordenar por distancia
        zonas_riesgo_cercanas.sort(key=lambda x: x['distancia'])
        # Limitar a las 5 zonas más cercanas
        zonas_riesgo_cercanas = zonas_riesgo_cercanas[:5]

    context = {
        'perfil': perfil,
        'alertas_activas': alertas_activas,
        'zonas_riesgo_cercanas': zonas_riesgo_cercanas,
    }
    return render(request, 'rappiSafe/repartidor/home.html', context)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def crear_alerta_panico(request):
    """Crear una alerta de pánico"""
    try:
        # Verificar si ya existe una alerta activa
        alerta_activa = Alerta.objects.filter(
            repartidor=request.user,
            estado__in=['pendiente', 'en_atencion']
        ).first()

        if alerta_activa:
            return JsonResponse({
                'success': False,
                'error': 'Ya tienes una alerta activa. Espera a que sea resuelta o cancélala primero.'
            }, status=400)

        data = json.loads(request.body)

        # Crear la alerta
        alerta = Alerta.objects.create(
            repartidor=request.user,
            tipo='panico',
            estado='pendiente',
            latitud=data.get('latitud'),
            longitud=data.get('longitud'),
            nivel_bateria=data.get('bateria'),
            datos_sensores=data.get('datos_sensores', {}),
        )

        # Actualizar el perfil del repartidor
        perfil = request.user.perfil_repartidor
        perfil.estado = 'emergencia'
        perfil.ultima_latitud = data.get('latitud')
        perfil.ultima_longitud = data.get('longitud')
        perfil.nivel_bateria = data.get('bateria')
        perfil.ultima_actualizacion_ubicacion = timezone.now()
        perfil.save()

        # Enviar notificación por WebSocket
        enviar_nueva_alerta(serializar_alerta(alerta))

        # Notificar a contactos de emergencia
        from .utils import notificar_contactos_emergencia
        resultado_notificaciones = notificar_contactos_emergencia(alerta)

        return JsonResponse({
            'success': True,
            'alerta_id': str(alerta.id),
            'mensaje': 'Alerta de pánico activada',
            'contactos_notificados': resultado_notificaciones.get('contactos_notificados', 0),
            'notificaciones_info': f"{resultado_notificaciones.get('contactos_notificados', 0)} contacto(s) notificado(s)"
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def crear_alerta_accidente(request):
    """Crear una alerta automática por detección de accidente"""
    try:
        data = json.loads(request.body)

        # Crear la alerta
        alerta = Alerta.objects.create(
            repartidor=request.user,
            tipo='accidente',
            estado='pendiente',
            latitud=data.get('latitud'),
            longitud=data.get('longitud'),
            nivel_bateria=data.get('bateria'),
            datos_sensores=data.get('datos_sensores', {}),
        )

        # Actualizar el perfil del repartidor
        perfil = request.user.perfil_repartidor
        perfil.estado = 'emergencia'
        perfil.ultima_latitud = data.get('latitud')
        perfil.ultima_longitud = data.get('longitud')
        perfil.nivel_bateria = data.get('bateria')
        perfil.ultima_actualizacion_ubicacion = timezone.now()
        perfil.save()

        # Enviar notificación por WebSocket
        enviar_nueva_alerta(serializar_alerta(alerta))

        # Notificar a contactos de emergencia
        from .utils import notificar_contactos_emergencia
        resultado_notificaciones = notificar_contactos_emergencia(alerta)

        return JsonResponse({
            'success': True,
            'alerta_id': str(alerta.id),
            'mensaje': 'Alerta de accidente creada',
            'contactos_notificados': resultado_notificaciones.get('contactos_notificados', 0),
            'notificaciones_info': f"{resultado_notificaciones.get('contactos_notificados', 0)} contacto(s) notificado(s)"
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def cancelar_alerta(request, alerta_id):
    """Cancelar una alerta (marcar como falsa alarma)"""
    try:
        alerta = get_object_or_404(Alerta, id=alerta_id, repartidor=request.user)

        if alerta.estado in ['pendiente', 'en_atencion']:
            alerta.estado = 'falsa_alarma'
            alerta.save()

            # Actualizar perfil del repartidor
            perfil = request.user.perfil_repartidor
            perfil.estado = 'disponible'
            perfil.save()

            # Notificar actualización
            enviar_actualizacion_alerta(serializar_alerta(alerta))

            return JsonResponse({
                'success': True,
                'mensaje': 'Alerta cancelada'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'La alerta no puede ser cancelada'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def actualizar_ubicacion(request):
    """Actualizar ubicación del repartidor durante una alerta"""
    try:
        data = json.loads(request.body)
        alerta_id = data.get('alerta_id')

        if alerta_id:
            # Enviar actualización por WebSocket
            enviar_actualizacion_ubicacion(
                alerta_id,
                data.get('latitud'),
                data.get('longitud'),
                data.get('precision'),
                data.get('velocidad')
            )

        # Actualizar perfil del repartidor
        perfil = request.user.perfil_repartidor
        perfil.ultima_latitud = data.get('latitud')
        perfil.ultima_longitud = data.get('longitud')
        perfil.ultima_actualizacion_ubicacion = timezone.now()
        perfil.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def actualizar_bateria(request):
    """Actualizar nivel de batería del dispositivo"""
    try:
        data = json.loads(request.body)
        perfil = request.user.perfil_repartidor
        perfil.nivel_bateria = data.get('bateria')
        perfil.ultima_actualizacion_bateria = timezone.now()
        perfil.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@user_passes_test(es_repartidor)
def contactos_confianza_view(request):
    """Ver y gestionar contactos de confianza"""
    contactos = ContactoConfianza.objects.filter(repartidor=request.user).order_by('-creado_en')

    context = {
        'contactos': contactos,
    }
    return render(request, 'rappiSafe/repartidor/contactos.html', context)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def agregar_contacto(request):
    """Agregar un nuevo contacto de confianza"""
    try:
        # Verificar que no tenga más de 3 contactos
        if ContactoConfianza.objects.filter(repartidor=request.user).count() >= 3:
            return JsonResponse({
                'success': False,
                'error': 'Solo puedes tener hasta 3 contactos de confianza'
            }, status=400)

        data = json.loads(request.body)

        contacto = ContactoConfianza.objects.create(
            repartidor=request.user,
            nombre=data.get('nombre'),
            telefono=data.get('telefono'),
            relacion=data.get('relacion', ''),
            validado=True  # Marcar como validado automáticamente
        )

        return JsonResponse({
            'success': True,
            'mensaje': 'Contacto agregado exitosamente',
            'contacto': {
                'id': contacto.id,
                'nombre': contacto.nombre,
                'telefono': contacto.telefono,
                'relacion': contacto.relacion,
                'validado': contacto.validado
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def validar_contacto(request, contacto_id):
    """Validar un contacto de confianza"""
    try:
        contacto = ContactoConfianza.objects.get(id=contacto_id, repartidor=request.user)
        contacto.validado = True
        contacto.save()

        return JsonResponse({
            'success': True,
            'mensaje': 'Contacto validado exitosamente'
        })
    except ContactoConfianza.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Contacto no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def eliminar_contacto(request, contacto_id):
    """Eliminar un contacto de confianza"""
    try:
        contacto = ContactoConfianza.objects.get(id=contacto_id, repartidor=request.user)
        contacto.delete()

        return JsonResponse({
            'success': True,
            'mensaje': 'Contacto eliminado exitosamente'
        })
    except ContactoConfianza.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Contacto no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
def solicitar_ayuda_psicologica_view(request):
    """Solicitar ayuda psicológica"""
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        urgencia = request.POST.get('urgencia', 5)

        SolicitudAyudaPsicologica.objects.create(
            repartidor=request.user,
            descripcion=descripcion,
            urgencia=urgencia
        )

        messages.success(request, 'Tu solicitud ha sido registrada. Pronto te contactaremos.')
        return redirect('repartidor_home')

    return render(request, 'rappiSafe/repartidor/ayuda_psicologica.html')


@login_required
@user_passes_test(es_repartidor)
def mi_perfil_view(request):
    """Vista de perfil del repartidor"""
    perfil = request.user.perfil_repartidor
    contactos = ContactoConfianza.objects.filter(repartidor=request.user).order_by('-creado_en')

    if request.method == 'POST':
        # Actualizar información del usuario
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.telefono = request.POST.get('telefono', '')
        request.user.save()

        # Actualizar información del perfil
        perfil.tiene_seguro = request.POST.get('tiene_seguro') == 'on'
        perfil.nombre_aseguradora = request.POST.get('nombre_aseguradora', '')
        perfil.numero_poliza = request.POST.get('numero_poliza', '')
        perfil.telefono_aseguradora = request.POST.get('telefono_aseguradora', '')

        vigencia = request.POST.get('vigencia_seguro')
        if vigencia:
            perfil.vigencia_seguro = vigencia
        else:
            perfil.vigencia_seguro = None

        # Actualizar configuración de agitación
        perfil.agitacion_habilitada = request.POST.get('agitacion_habilitada') == 'on'
        sensibilidad = request.POST.get('sensibilidad_agitacion', '15')
        try:
            sensibilidad_val = int(sensibilidad)
            if 10 <= sensibilidad_val <= 30:
                perfil.sensibilidad_agitacion = sensibilidad_val
        except ValueError:
            pass

        # Manejar foto de perfil
        if 'foto' in request.FILES:
            perfil.foto = request.FILES['foto']

        perfil.save()

        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('mi_perfil')

    context = {
        'perfil': perfil,
        'contactos': contactos,
    }
    return render(request, 'rappiSafe/repartidor/mi_perfil.html', context)


@login_required
@user_passes_test(es_repartidor)
def rutas_view(request):
    """Vista de rutas seguras"""
    perfil = request.user.perfil_repartidor

    context = {
        'perfil': perfil,
    }
    return render(request, 'rappiSafe/repartidor/rutas.html', context)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def calcular_rutas(request):
    """Calcular rutas (rápida y seguras) usando API de routing real"""
    try:
        data = json.loads(request.body)
        origen_lat = float(data.get('origen_lat'))
        origen_lon = float(data.get('origen_lon'))
        destino_lat = float(data.get('destino_lat'))
        destino_lon = float(data.get('destino_lon'))

        # Obtener rutas reales usando OSRM
        from .utils import obtener_rutas_alternativas

        resultado = obtener_rutas_alternativas(origen_lat, origen_lon, destino_lat, destino_lon)

        if not resultado.get('success'):
            return JsonResponse({
                'success': False,
                'error': resultado.get('error', 'Error al calcular rutas')
            }, status=400)

        ruta_rapida = resultado['rapida']
        rutas_seguras = resultado['seguras']

        # Preparar datos para respuesta
        ruta_rapida_response = {
            'tipo': 'rapida',
            'distancia': ruta_rapida['distancia'],
            'duracion': ruta_rapida['duracion'],
            'puntuacion_riesgo': round(ruta_rapida['puntuacion_riesgo'], 1),
            'coordenadas': ruta_rapida['coordenadas']
        }

        rutas_seguras_response = [
            {
                'tipo': 'segura',
                'distancia': ruta['distancia'],
                'duracion': ruta['duracion'],
                'puntuacion_riesgo': round(ruta['puntuacion_riesgo'], 1),
                'coordenadas': ruta['coordenadas']
            }
            for ruta in rutas_seguras
        ]

        # Guardar en base de datos
        RutaSegura.objects.create(
            repartidor=request.user,
            origen_lat=origen_lat,
            origen_lon=origen_lon,
            destino_lat=destino_lat,
            destino_lon=destino_lon,
            ruta_rapida=ruta_rapida_response,
            ruta_segura={'rutas': rutas_seguras_response},
            puntuacion_riesgo_rapida=ruta_rapida_response['puntuacion_riesgo'],
            puntuacion_riesgo_segura=rutas_seguras_response[0]['puntuacion_riesgo'],
            seleccionada='rapida'
        )

        return JsonResponse({
            'success': True,
            'rutas': {
                'rapida': ruta_rapida_response,
                'seguras': rutas_seguras_response
            }
        })

    except Exception as e:
        import traceback
        print(f"Error al calcular rutas: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Error al calcular rutas: {str(e)}'
        }, status=400)


# ==================== VISTAS OPERADOR ====================

@login_required
@user_passes_test(es_operador, login_url='login')
def operador_dashboard(request):
    """Dashboard de monitoreo para operadores"""
    alertas_activas = Alerta.objects.filter(
        estado__in=['pendiente', 'en_atencion']
    ).select_related('repartidor').order_by('-creado_en')

    # Incluir solicitudes de ayuda psicológica pendientes
    solicitudes_psicologicas = SolicitudAyudaPsicologica.objects.filter(
        estado__in=['pendiente', 'en_proceso']
    ).select_related('repartidor').order_by('-creado_en')

    context = {
        'alertas_activas': alertas_activas,
        'solicitudes_psicologicas': solicitudes_psicologicas,
        'total_solicitudes_pendientes': solicitudes_psicologicas.filter(estado='pendiente').count(),
    }
    return render(request, 'rappiSafe/operador/dashboard.html', context)


@login_required
@user_passes_test(es_operador)
def ver_alerta(request, alerta_id):
    """Ver detalles de una alerta específica"""
    alerta = get_object_or_404(Alerta, id=alerta_id)
    trayectorias = Trayectoria.objects.filter(alerta=alerta).order_by('timestamp')
    contactos = ContactoConfianza.objects.filter(repartidor=alerta.repartidor)

    # Intentar obtener el incidente asociado
    try:
        incidente = alerta.incidente
        bitacoras = incidente.bitacoras.all().order_by('timestamp')
    except Incidente.DoesNotExist:
        incidente = None
        bitacoras = []

    # Total de solicitudes pendientes para el badge de navegación
    total_solicitudes_pendientes = SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()

    context = {
        'alerta': alerta,
        'trayectorias': trayectorias,
        'contactos': contactos,
        'incidente': incidente,
        'bitacoras': bitacoras,
        'total_solicitudes_pendientes': total_solicitudes_pendientes,
    }
    return render(request, 'rappiSafe/operador/ver_alerta.html', context)


@login_required
@user_passes_test(es_operador)
def contactar_emergencias(request, alerta_id):
    """Vista para contactar servicios de emergencia"""
    alerta = get_object_or_404(Alerta, id=alerta_id)

    # Total de solicitudes pendientes para el badge de navegación
    total_solicitudes_pendientes = SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()

    context = {
        'alerta': alerta,
        'total_solicitudes_pendientes': total_solicitudes_pendientes,
    }
    return render(request, 'rappiSafe/operador/emergencias.html', context)


@login_required
@user_passes_test(es_operador)
@require_POST
def atender_alerta(request, alerta_id):
    """Marcar alerta como en atención"""
    try:
        alerta = get_object_or_404(Alerta, id=alerta_id)
        alerta.estado = 'en_atencion'
        alerta.atendido_por = request.user
        alerta.save()

        # Crear incidente si no existe
        if not hasattr(alerta, 'incidente'):
            incidente = Incidente.objects.create(
                alerta=alerta,
                operador=request.user,
                estado='abierto'
            )

            # Registrar en bitácora
            Bitacora.objects.create(
                incidente=incidente,
                operador=request.user,
                accion='Alerta tomada en atención por el operador'
            )

        # Notificar actualización
        enviar_actualizacion_alerta(serializar_alerta(alerta))

        return JsonResponse({
            'success': True,
            'mensaje': 'Alerta atendida'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def cerrar_alerta(request, alerta_id):
    """Cerrar una alerta"""
    try:
        data = json.loads(request.body)
        alerta = get_object_or_404(Alerta, id=alerta_id)
        alerta.estado = 'cerrada'
        alerta.save()

        # Actualizar el incidente
        if hasattr(alerta, 'incidente'):
            incidente = alerta.incidente
            incidente.estado = 'cerrado'
            incidente.cerrado_en = timezone.now()
            incidente.tiempo_respuesta = incidente.cerrado_en - incidente.creado_en
            incidente.save()

            # Registrar en bitácora
            Bitacora.objects.create(
                incidente=incidente,
                operador=request.user,
                accion=f"Alerta cerrada. {data.get('notas', '')}"
            )

        # Actualizar perfil del repartidor
        perfil = alerta.repartidor.perfil_repartidor
        perfil.estado = 'disponible'
        perfil.save()

        # Notificar actualización
        enviar_actualizacion_alerta(serializar_alerta(alerta))

        return JsonResponse({
            'success': True,
            'mensaje': 'Alerta cerrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def agregar_bitacora(request, incidente_id):
    """Agregar entrada a la bitácora de un incidente"""
    try:
        data = json.loads(request.body)
        incidente = get_object_or_404(Incidente, id=incidente_id)

        Bitacora.objects.create(
            incidente=incidente,
            operador=request.user,
            accion=data.get('accion')
        )

        return JsonResponse({
            'success': True,
            'mensaje': 'Entrada agregada a la bitácora'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def actualizar_folio_911(request, incidente_id):
    """Actualizar el folio 911 de un incidente"""
    try:
        data = json.loads(request.body)
        incidente = get_object_or_404(Incidente, id=incidente_id)
        incidente.folio_911 = data.get('folio')
        incidente.autoridades_contactadas = True
        incidente.save()

        # Registrar en bitácora
        Bitacora.objects.create(
            incidente=incidente,
            operador=request.user,
            accion=f'Folio 911 registrado: {data.get("folio")}'
        )

        return JsonResponse({
            'success': True,
            'mensaje': 'Folio 911 registrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_operador)
def gestionar_solicitudes_psicologicas(request):
    """Vista para gestionar solicitudes de ayuda psicológica"""
    solicitudes = SolicitudAyudaPsicologica.objects.all().select_related('repartidor').order_by('-creado_en')

    context = {
        'solicitudes': solicitudes,
        'total_solicitudes_pendientes': solicitudes.filter(estado='pendiente').count(),
    }
    return render(request, 'rappiSafe/operador/solicitudes_psicologicas.html', context)


@login_required
@user_passes_test(es_operador)
@require_POST
def atender_solicitud_psicologica(request, solicitud_id):
    """Atender una solicitud de ayuda psicológica"""
    try:
        data = json.loads(request.body)
        solicitud = get_object_or_404(SolicitudAyudaPsicologica, id=solicitud_id)

        solicitud.estado = data.get('estado', 'en_proceso')
        solicitud.notas_atencion = data.get('notas_atencion', '')

        if solicitud.estado == 'atendida' and not solicitud.atendido_en:
            solicitud.atendido_en = timezone.now()

        solicitud.save()

        return JsonResponse({
            'success': True,
            'mensaje': 'Solicitud actualizada correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_operador)
def reportes_operador(request):
    """Vista de reportes para operadores"""
    from datetime import datetime, timedelta
    from django.db.models import Count, Avg, Q
    from django.db.models.functions import TruncDate

    # Obtener rango de fechas (últimos 30 días por defecto)
    fecha_fin = timezone.now()
    fecha_inicio = fecha_fin - timedelta(days=30)

    # Filtros opcionales
    if request.GET.get('fecha_inicio'):
        fecha_inicio = datetime.strptime(request.GET.get('fecha_inicio'), '%Y-%m-%d')
        fecha_inicio = timezone.make_aware(fecha_inicio)
    if request.GET.get('fecha_fin'):
        fecha_fin = datetime.strptime(request.GET.get('fecha_fin'), '%Y-%m-%d')
        fecha_fin = timezone.make_aware(fecha_fin)

    # Alertas en el período
    alertas = Alerta.objects.filter(
        creado_en__range=[fecha_inicio, fecha_fin]
    )

    # Estadísticas generales
    total_alertas = alertas.count()
    alertas_panico = alertas.filter(tipo='panico').count()
    alertas_accidente = alertas.filter(tipo='accidente').count()
    alertas_cerradas = alertas.filter(estado='cerrada').count()
    alertas_pendientes = alertas.filter(estado='pendiente').count()

    # Alertas por día
    alertas_por_dia = alertas.annotate(
        fecha=TruncDate('creado_en')
    ).values('fecha').annotate(
        total=Count('id')
    ).order_by('fecha')

    # Incidentes con tiempo de respuesta
    incidentes = Incidente.objects.filter(
        creado_en__range=[fecha_inicio, fecha_fin],
        tiempo_respuesta__isnull=False
    )

    # Calcular tiempo promedio de respuesta
    if incidentes.exists():
        tiempo_promedio = incidentes.aggregate(
            promedio=Avg('tiempo_respuesta')
        )['promedio']
        if tiempo_promedio:
            tiempo_promedio_minutos = int(tiempo_promedio.total_seconds() / 60)
        else:
            tiempo_promedio_minutos = 0
    else:
        tiempo_promedio_minutos = 0

    # Alertas atendidas por el operador actual
    mis_alertas = alertas.filter(atendido_por=request.user).count()

    # Top 5 operadores con más alertas resueltas
    top_operadores = alertas.filter(
        estado='cerrada',
        atendido_por__isnull=False
    ).values(
        'atendido_por__first_name',
        'atendido_por__last_name',
        'atendido_por__id'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    # Solicitudes psicológicas en el período
    solicitudes_psico = SolicitudAyudaPsicologica.objects.filter(
        creado_en__range=[fecha_inicio, fecha_fin]
    )
    total_solicitudes_psico = solicitudes_psico.count()
    solicitudes_psico_atendidas = solicitudes_psico.filter(estado='atendida').count()

    # Total de solicitudes pendientes para el badge de navegación
    total_solicitudes_pendientes = SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()

    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_alertas': total_alertas,
        'alertas_panico': alertas_panico,
        'alertas_accidente': alertas_accidente,
        'alertas_cerradas': alertas_cerradas,
        'alertas_pendientes': alertas_pendientes,
        'alertas_por_dia': list(alertas_por_dia),
        'tiempo_promedio_minutos': tiempo_promedio_minutos,
        'mis_alertas': mis_alertas,
        'top_operadores': top_operadores,
        'total_solicitudes_psico': total_solicitudes_psico,
        'solicitudes_psico_atendidas': solicitudes_psico_atendidas,
        'total_solicitudes_pendientes': total_solicitudes_pendientes,
    }
    return render(request, 'rappiSafe/operador/reportes.html', context)


@login_required
@user_passes_test(es_operador)
def historial_alertas_operador(request):
    """Vista de historial completo de alertas para operadores"""
    from django.core.paginator import Paginator
    from django.db.models import Q

    # Obtener todas las alertas
    alertas = Alerta.objects.all().select_related('repartidor', 'atendido_por').order_by('-creado_en')

    # Aplicar filtros
    estado = request.GET.get('estado', '')
    tipo = request.GET.get('tipo', '')
    buscar = request.GET.get('buscar', '')

    if estado:
        alertas = alertas.filter(estado=estado)

    if tipo:
        alertas = alertas.filter(tipo=tipo)

    if buscar:
        alertas = alertas.filter(
            Q(repartidor__first_name__icontains=buscar) |
            Q(repartidor__last_name__icontains=buscar) |
            Q(repartidor__telefono__icontains=buscar)
        )

    # Estadísticas para el resumen
    total_alertas = alertas.count()
    alertas_pendientes = alertas.filter(estado='pendiente').count()
    alertas_en_atencion = alertas.filter(estado='en_atencion').count()
    alertas_cerradas = alertas.filter(estado='cerrado').count()

    # Paginación
    paginator = Paginator(alertas, 20)  # 20 alertas por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Total de solicitudes pendientes para el badge de navegación
    total_solicitudes_pendientes = SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()

    context = {
        'page_obj': page_obj,
        'total_alertas': total_alertas,
        'alertas_pendientes': alertas_pendientes,
        'alertas_en_atencion': alertas_en_atencion,
        'alertas_cerradas': alertas_cerradas,
        'total_solicitudes_pendientes': total_solicitudes_pendientes,
    }
    return render(request, 'rappiSafe/operador/historial_alertas.html', context)


@login_required
@user_passes_test(es_operador)
@require_POST
def notificar_contactos_operador(request, alerta_id):
    """Endpoint para notificar contactos de confianza desde el operador"""
    from rappiSafe.utils import notificar_contactos_emergencia

    try:
        alerta = Alerta.objects.select_related('repartidor').get(id=alerta_id)

        # Verificar que la alerta pertenezca a un repartidor
        if not hasattr(alerta.repartidor, 'perfil_repartidor'):
            return JsonResponse({
                'success': False,
                'error': 'El usuario no tiene perfil de repartidor'
            })

        # Llamar a la función de notificaciones
        resultado = notificar_contactos_emergencia(alerta)

        # Actualizar el incidente si existe
        try:
            incidente = Incidente.objects.get(alerta=alerta)
            incidente.contactos_notificados = True
            incidente.save()
        except Incidente.DoesNotExist:
            pass

        return JsonResponse({
            'success': resultado['success'],
            'contactos_notificados': resultado.get('contactos_notificados', 0),
            'notificaciones_fallidas': resultado.get('notificaciones_fallidas', 0),
            'detalles': resultado.get('detalles', [])
        })
    except Alerta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Alerta no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(lambda u: u.rol in ['operador', 'administrador'])
def generar_reporte_pdf(request):
    """Generar reporte PDF de alertas - Accesible para operadores y administradores"""
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from datetime import datetime, timedelta
    from django.db.models import Count, Avg
    from django.db.models.functions import TruncDate
    import io

    # Obtener rango de fechas
    fecha_fin = timezone.now()
    fecha_inicio = fecha_fin - timedelta(days=30)

    if request.GET.get('fecha_inicio'):
        fecha_inicio = datetime.strptime(request.GET.get('fecha_inicio'), '%Y-%m-%d')
        fecha_inicio = timezone.make_aware(fecha_inicio)
    if request.GET.get('fecha_fin'):
        fecha_fin = datetime.strptime(request.GET.get('fecha_fin'), '%Y-%m-%d')
        fecha_fin = timezone.make_aware(fecha_fin)

    # Obtener datos
    alertas = Alerta.objects.filter(creado_en__range=[fecha_inicio, fecha_fin])
    total_alertas = alertas.count()
    alertas_panico = alertas.filter(tipo='panico').count()
    alertas_accidente = alertas.filter(tipo='accidente').count()
    alertas_cerradas = alertas.filter(estado='cerrada').count()
    alertas_pendientes = alertas.filter(estado='pendiente').count()

    # Crear el PDF en memoria
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=12,
        spaceBefore=12
    )

    # Título
    elements.append(Paragraph("Reporte de Alertas - RappiSafe", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Período
    periodo_text = f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
    elements.append(Paragraph(periodo_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Estadísticas generales
    elements.append(Paragraph("Estadísticas Generales", heading_style))
    data_stats = [
        ['Métrica', 'Valor'],
        ['Total de Alertas', str(total_alertas)],
        ['Alertas de Pánico', str(alertas_panico)],
        ['Alertas de Accidente', str(alertas_accidente)],
        ['Alertas Cerradas', str(alertas_cerradas)],
        ['Alertas Pendientes', str(alertas_pendientes)],
    ]

    table_stats = Table(data_stats, colWidths=[3*inch, 2*inch])
    table_stats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table_stats)
    elements.append(Spacer(1, 0.3*inch))

    # Top Repartidores
    elements.append(Paragraph("Top 5 Repartidores con Más Alertas", heading_style))
    top_repartidores = alertas.values(
        'repartidor__first_name',
        'repartidor__last_name'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    data_top = [['Posición', 'Repartidor', 'Total Alertas']]
    for idx, rep in enumerate(top_repartidores, 1):
        nombre = f"{rep['repartidor__first_name']} {rep['repartidor__last_name']}"
        data_top.append([str(idx), nombre, str(rep['total'])])

    if len(data_top) > 1:
        table_top = Table(data_top, colWidths=[1*inch, 3*inch, 1.5*inch])
        table_top.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table_top)
    else:
        elements.append(Paragraph("No hay datos disponibles", styles['Normal']))

    elements.append(Spacer(1, 0.3*inch))

    # Pie de página
    elements.append(Spacer(1, 0.5*inch))
    footer_text = f"Generado el {timezone.now().strftime('%d/%m/%Y %H:%M:%S')} por {request.user.get_full_name()}"
    elements.append(Paragraph(footer_text, styles['Normal']))

    # Construir PDF
    doc.build(elements)

    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"reporte_alertas_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
@user_passes_test(es_operador)
def lista_repartidores(request):
    """Vista para listar todos los repartidores"""
    repartidores = User.objects.filter(
        rol='repartidor',
        is_active=True
    ).select_related('perfil_repartidor').order_by('first_name', 'last_name')

    # Estadísticas por repartidor
    repartidores_data = []
    for repartidor in repartidores:
        # Contar alertas
        total_alertas = Alerta.objects.filter(repartidor=repartidor).count()
        alertas_activas = Alerta.objects.filter(
            repartidor=repartidor,
            estado__in=['pendiente', 'en_atencion']
        ).count()
        ultima_alerta = Alerta.objects.filter(repartidor=repartidor).order_by('-creado_en').first()

        # Obtener perfil
        try:
            perfil = repartidor.perfil_repartidor
            estado = perfil.estado
            ultima_ubicacion = {
                'lat': perfil.ultima_latitud,
                'lon': perfil.ultima_longitud,
                'fecha': perfil.ultima_actualizacion_ubicacion
            } if perfil.ultima_latitud else None
            nivel_bateria = perfil.nivel_bateria
        except:
            estado = 'offline'
            ultima_ubicacion = None
            nivel_bateria = None

        # Contactos de confianza
        contactos = ContactoConfianza.objects.filter(repartidor=repartidor)

        repartidores_data.append({
            'repartidor': repartidor,
            'estado': estado,
            'total_alertas': total_alertas,
            'alertas_activas': alertas_activas,
            'ultima_alerta': ultima_alerta,
            'ultima_ubicacion': ultima_ubicacion,
            'nivel_bateria': nivel_bateria,
            'contactos': contactos,
        })

    # Total de solicitudes pendientes para el badge de navegación
    total_solicitudes_pendientes = SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()

    context = {
        'repartidores_data': repartidores_data,
        'total_solicitudes_pendientes': total_solicitudes_pendientes,
    }
    return render(request, 'rappiSafe/operador/repartidores.html', context)


@login_required
@user_passes_test(es_operador)
def operador_perfil_view(request):
    """Vista de perfil del operador"""
    # Total de solicitudes pendientes para el badge de navegación
    total_solicitudes_pendientes = SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()

    if request.method == 'POST':
        # Actualizar información del usuario
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.telefono = request.POST.get('telefono', '')
        request.user.save()

        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('operador_perfil')

    # Estadísticas del operador
    alertas_atendidas = Alerta.objects.filter(atendido_por=request.user).count()
    alertas_cerradas = Alerta.objects.filter(
        atendido_por=request.user,
        estado='cerrada'
    ).count()

    # Últimas alertas atendidas
    ultimas_alertas = Alerta.objects.filter(
        atendido_por=request.user
    ).select_related('repartidor').order_by('-actualizado_en')[:5]

    context = {
        'alertas_atendidas': alertas_atendidas,
        'alertas_cerradas': alertas_cerradas,
        'ultimas_alertas': ultimas_alertas,
        'total_solicitudes_pendientes': total_solicitudes_pendientes,
    }
    return render(request, 'rappiSafe/operador/perfil.html', context)


# ==================== VISTAS ADMINISTRADOR ====================

@login_required
@user_passes_test(es_administrador, login_url='login')
def admin_dashboard(request):
    """Dashboard principal del administrador"""
    # Estadísticas generales
    total_usuarios = User.objects.filter(activo=True).count()
    total_repartidores = User.objects.filter(rol='repartidor', activo=True).count()
    total_operadores = User.objects.filter(rol='operador', activo=True).count()

    # Alertas del mes actual
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0)
    alertas_mes = Alerta.objects.filter(creado_en__gte=inicio_mes).count()

    # Alertas por tipo
    alertas_por_tipo = Alerta.objects.values('tipo').annotate(total=Count('id'))

    context = {
        'total_usuarios': total_usuarios,
        'total_repartidores': total_repartidores,
        'total_operadores': total_operadores,
        'alertas_mes': alertas_mes,
        'alertas_por_tipo': alertas_por_tipo,
    }
    return render(request, 'rappiSafe/admin/dashboard.html', context)


@login_required
@user_passes_test(es_administrador)
def gestionar_usuarios(request):
    """Gestionar usuarios del sistema"""
    usuarios = User.objects.all().order_by('-date_joined')

    # Filtros
    rol_filtro = request.GET.get('rol')
    if rol_filtro:
        usuarios = usuarios.filter(rol=rol_filtro)

    estado_filtro = request.GET.get('estado')
    if estado_filtro == 'activo':
        usuarios = usuarios.filter(activo=True)
    elif estado_filtro == 'inactivo':
        usuarios = usuarios.filter(activo=False)

    # Paginación
    paginator = Paginator(usuarios, 20)
    page = request.GET.get('page')
    usuarios = paginator.get_page(page)

    context = {
        'usuarios': usuarios,
    }
    return render(request, 'rappiSafe/admin/usuarios.html', context)


@login_required
@user_passes_test(es_administrador)
def estadisticas_view(request):
    """Vista de estadísticas y reportes con datos reales de la BD"""
    from django.db.models import Avg, F, ExpressionWrapper, DurationField

    # Rango de fechas (últimos 30 días por defecto)
    fecha_fin = timezone.now().date()
    fecha_inicio = fecha_fin - timedelta(days=30)

    if request.GET.get('fecha_inicio'):
        fecha_inicio = datetime.strptime(request.GET.get('fecha_inicio'), '%Y-%m-%d').date()
    if request.GET.get('fecha_fin'):
        fecha_fin = datetime.strptime(request.GET.get('fecha_fin'), '%Y-%m-%d').date()

    # ===== ESTADÍSTICAS DE REPARTIDORES =====
    total_repartidores = User.objects.filter(rol='repartidor', is_active=True).count()
    repartidores_con_perfil = RepartidorProfile.objects.count()

    # Repartidores por estado (del perfil)
    repartidores_disponibles = RepartidorProfile.objects.filter(estado='disponible').count()
    repartidores_en_ruta = RepartidorProfile.objects.filter(estado='en_ruta').count()
    repartidores_offline = RepartidorProfile.objects.filter(estado='offline').count()

    # ===== ESTADÍSTICAS DE OPERADORES =====
    total_operadores = User.objects.filter(rol='operador', is_active=True).count()

    # Operadores que han atendido alertas (en el período)
    operadores_activos = Incidente.objects.filter(
        creado_en__date__gte=fecha_inicio,
        creado_en__date__lte=fecha_fin
    ).values('operador').distinct().count()

    # ===== ESTADÍSTICAS DE ALERTAS =====
    alertas = Alerta.objects.filter(
        creado_en__date__gte=fecha_inicio,
        creado_en__date__lte=fecha_fin
    )

    total_alertas = alertas.count()
    alertas_panico = alertas.filter(tipo='panico').count()
    alertas_accidente = alertas.filter(tipo='accidente').count()
    alertas_agitacion = alertas.filter(tipo='agitacion').count()

    # Alertas por estado
    alertas_pendientes = alertas.filter(estado='pendiente').count()
    alertas_atendidas = alertas.filter(estado='atendida').count()
    alertas_resueltas = alertas.filter(estado='resuelta').count()
    alertas_cerradas = alertas.filter(estado='cerrada').count()
    alertas_canceladas = alertas.filter(estado='cancelada').count()

    alertas_por_estado = alertas.values('estado').annotate(total=Count('id')).order_by('-total')

    # ===== TOP REPARTIDORES CON MÁS ALERTAS =====
    top_repartidores = alertas.values(
        'repartidor__id',
        'repartidor__first_name',
        'repartidor__last_name',
        'repartidor__username'
    ).annotate(
        total_alertas=Count('id')
    ).order_by('-total_alertas')[:5]

    # ===== ESTADÍSTICAS DE TIEMPO DE RESPUESTA =====
    # Calcular tiempo promedio de respuesta (entre creación de alerta y creación de incidente)
    incidentes_periodo = Incidente.objects.filter(
        creado_en__date__gte=fecha_inicio,
        creado_en__date__lte=fecha_fin,
        alerta__isnull=False
    )

    tiempos_respuesta = []
    for incidente in incidentes_periodo:
        if incidente.alerta:
            tiempo_diff = incidente.creado_en - incidente.alerta.creado_en
            tiempos_respuesta.append(tiempo_diff.total_seconds() / 60)  # en minutos

    tiempo_promedio_respuesta = round(sum(tiempos_respuesta) / len(tiempos_respuesta), 2) if tiempos_respuesta else 0

    # ===== ALERTAS POR TIPO =====
    alertas_por_tipo = alertas.values('tipo').annotate(total=Count('id')).order_by('-total')

    # ===== INCIDENTES =====
    total_incidentes = Incidente.objects.filter(
        creado_en__date__gte=fecha_inicio,
        creado_en__date__lte=fecha_fin
    ).count()

    incidentes_911 = Incidente.objects.filter(
        creado_en__date__gte=fecha_inicio,
        creado_en__date__lte=fecha_fin,
        folio_911__isnull=False
    ).exclude(folio_911='').count()

    # ===== ESTADÍSTICAS DE AYUDA PSICOLÓGICA =====
    total_solicitudes_psicologicas = SolicitudAyudaPsicologica.objects.filter(
        creado_en__date__gte=fecha_inicio,
        creado_en__date__lte=fecha_fin
    ).count()

    solicitudes_atendidas = SolicitudAyudaPsicologica.objects.filter(
        creado_en__date__gte=fecha_inicio,
        creado_en__date__lte=fecha_fin,
        estado='atendida'
    ).count()

    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,

        # Repartidores
        'total_repartidores': total_repartidores,
        'repartidores_con_perfil': repartidores_con_perfil,
        'repartidores_disponibles': repartidores_disponibles,
        'repartidores_en_ruta': repartidores_en_ruta,
        'repartidores_offline': repartidores_offline,

        # Operadores
        'total_operadores': total_operadores,
        'operadores_activos': operadores_activos,

        # Alertas
        'total_alertas': total_alertas,
        'alertas_panico': alertas_panico,
        'alertas_accidente': alertas_accidente,
        'alertas_agitacion': alertas_agitacion,
        'alertas_pendientes': alertas_pendientes,
        'alertas_atendidas': alertas_atendidas,
        'alertas_resueltas': alertas_resueltas,
        'alertas_cerradas': alertas_cerradas,
        'alertas_canceladas': alertas_canceladas,
        'alertas_por_estado': alertas_por_estado,
        'alertas_por_tipo': alertas_por_tipo,

        # Top repartidores
        'top_repartidores': top_repartidores,

        # Tiempos
        'tiempo_promedio_respuesta': tiempo_promedio_respuesta,

        # Incidentes
        'total_incidentes': total_incidentes,
        'incidentes_911': incidentes_911,

        # Ayuda psicológica
        'total_solicitudes_psicologicas': total_solicitudes_psicologicas,
        'solicitudes_atendidas': solicitudes_atendidas,
    }
    return render(request, 'rappiSafe/admin/estadisticas.html', context)


@login_required
@user_passes_test(es_repartidor)
def historial_view(request):
    """Vista de historial de alertas y solicitudes de ayuda del repartidor"""
    # Obtener todas las alertas del repartidor ordenadas por fecha
    alertas = Alerta.objects.filter(repartidor=request.user).order_by('-creado_en')

    # Obtener todas las solicitudes de ayuda psicológica
    solicitudes_ayuda = SolicitudAyudaPsicologica.objects.filter(
        repartidor=request.user
    ).order_by('-creado_en')

    # Paginación para alertas
    paginator_alertas = Paginator(alertas, 10)
    page_alertas = request.GET.get('page_alertas', 1)
    alertas_page = paginator_alertas.get_page(page_alertas)

    # Paginación para solicitudes
    paginator_solicitudes = Paginator(solicitudes_ayuda, 10)
    page_solicitudes = request.GET.get('page_solicitudes', 1)
    solicitudes_page = paginator_solicitudes.get_page(page_solicitudes)

    # Estadísticas rápidas
    total_alertas = alertas.count()
    alertas_resueltas = alertas.filter(estado='resuelta').count()
    alertas_panico = alertas.filter(tipo='panico').count()
    alertas_accidente = alertas.filter(tipo='accidente').count()
    total_solicitudes = solicitudes_ayuda.count()
    solicitudes_atendidas = solicitudes_ayuda.filter(estado='atendida').count()

    context = {
        'alertas': alertas_page,
        'solicitudes_ayuda': solicitudes_page,
        'total_alertas': total_alertas,
        'alertas_resueltas': alertas_resueltas,
        'alertas_panico': alertas_panico,
        'alertas_accidente': alertas_accidente,
        'total_solicitudes': total_solicitudes,
        'solicitudes_atendidas': solicitudes_atendidas,
    }

    return render(request, 'rappiSafe/repartidor/historial.html', context)


def register_view(request):
    """Vista de registro de nuevos usuarios repartidores"""
    import logging
    from django.db import transaction

    logger = logging.getLogger(__name__)

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        # Obtener datos del formulario y hacer trim
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        numero_identificacion = request.POST.get('numero_identificacion', '').strip()

        logger.info(f'=== INICIO REGISTRO ===')
        logger.info(f'Username: {username}')
        logger.info(f'Email: {email}')
        logger.info(f'Numero ID: {numero_identificacion}')

        # Validaciones básicas
        errors = []

        # Validar campos obligatorios
        if not username:
            errors.append('El nombre de usuario es obligatorio')
        if not email:
            errors.append('El correo electrónico es obligatorio')
        if not password:
            errors.append('La contraseña es obligatoria')
        if not password2:
            errors.append('Debes confirmar tu contraseña')
        if not first_name:
            errors.append('El nombre es obligatorio')
        if not last_name:
            errors.append('El apellido es obligatorio')
        if not telefono:
            errors.append('El teléfono es obligatorio')
        if not numero_identificacion:
            errors.append('El número de identificación es obligatorio')

        # Validar contraseñas
        if password and password2:
            if password != password2:
                errors.append('Las contraseñas no coinciden')
            elif len(password) < 8:
                errors.append('La contraseña debe tener al menos 8 caracteres')
            elif not any(char.isdigit() for char in password):
                errors.append('La contraseña debe contener al menos un número')
            elif not any(char.isalpha() for char in password):
                errors.append('La contraseña debe contener al menos una letra')

        # Validar email
        if email and '@' not in email:
            errors.append('El correo electrónico no es válido')

        # Si hay errores básicos, detener aquí
        if errors:
            for error in errors:
                messages.error(request, error)
            logger.warning(f'Validación fallida: {errors}')
            return render(request, 'registration/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'telefono': telefono,
                'numero_identificacion': numero_identificacion
            })

        # Validar unicidad
        logger.info('Validando unicidad de datos...')

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso')
            logger.warning(f'Username {username} ya existe')
            return render(request, 'registration/register.html', {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'telefono': telefono,
                'numero_identificacion': numero_identificacion
            })

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado')
            logger.warning(f'Email {email} ya existe')
            return render(request, 'registration/register.html', {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'telefono': telefono,
                'numero_identificacion': numero_identificacion
            })

        if RepartidorProfile.objects.filter(numero_identificacion__iexact=numero_identificacion).exists():
            messages.error(request, 'El número de identificación ya está registrado')
            logger.warning(f'Numero identificacion {numero_identificacion} ya existe')
            return render(request, 'registration/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'telefono': telefono
            })

        # Limpiar teléfono
        telefono_limpio = ''.join(c for c in telefono if c.isdigit() or c == '+')
        if len(telefono_limpio) < 10:
            messages.error(request, 'El teléfono debe contener al menos 10 dígitos')
            return render(request, 'registration/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'numero_identificacion': numero_identificacion
            })

        # Crear usuario y perfil en una transacción
        try:
            with transaction.atomic():
                logger.info(f'Creando usuario {username}...')

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    telefono=telefono_limpio,
                    rol='repartidor',
                    activo=True
                )
                logger.info(f'Usuario creado con ID {user.id}')

                # El signal puede haber creado un perfil automáticamente
                # Intentamos obtenerlo o crearlo si no existe
                logger.info(f'Configurando perfil de repartidor...')
                perfil, created = RepartidorProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'numero_identificacion': numero_identificacion,
                        'estado': 'offline'
                    }
                )

                # Si el perfil ya existía (creado por el signal), actualizar el número de identificación
                if not created:
                    logger.info(f'Perfil existente detectado, actualizando número de identificación')
                    perfil.numero_identificacion = numero_identificacion
                    perfil.estado = 'offline'
                    perfil.save()
                else:
                    logger.info(f'Perfil creado con ID {perfil.id}')

            messages.success(request, '¡Cuenta creada exitosamente! Por favor inicia sesión.')
            logger.info(f'=== REGISTRO EXITOSO ===')
            return redirect('login')

        except Exception as e:
            logger.error(f'ERROR al crear cuenta: {str(e)}', exc_info=True)

            # Mensaje de error más amigable
            error_msg = str(e).lower()
            if 'unique' in error_msg and 'numero_identificacion' in error_msg:
                messages.error(request, 'El número de identificación ya está en uso. Por favor usa otro.')
            else:
                messages.error(request, 'Error al crear la cuenta. Por favor intenta nuevamente.')

            return render(request, 'registration/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'telefono': telefono,
                'numero_identificacion': numero_identificacion
            })

    return render(request, 'registration/register.html')


@login_required
@user_passes_test(lambda u: u.rol == 'administrador')
def crear_operador_view(request):
    """Vista para que los administradores creen operadores"""
    import logging
    from django.db import transaction

    logger = logging.getLogger(__name__)

    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        telefono = request.POST.get('telefono', '').strip()

        logger.info(f'=== CREACIÓN DE OPERADOR ===')
        logger.info(f'Admin: {request.user.username}')
        logger.info(f'Nuevo operador: {username}')

        # Validaciones básicas
        errors = []

        if not username:
            errors.append('El nombre de usuario es obligatorio')
        if not email:
            errors.append('El correo electrónico es obligatorio')
        if not password:
            errors.append('La contraseña es obligatoria')
        if not password2:
            errors.append('Debes confirmar la contraseña')
        if not first_name:
            errors.append('El nombre es obligatorio')
        if not last_name:
            errors.append('El apellido es obligatorio')

        # Validar contraseñas
        if password and password2:
            if password != password2:
                errors.append('Las contraseñas no coinciden')
            elif len(password) < 8:
                errors.append('La contraseña debe tener al menos 8 caracteres')

        # Validar email
        if email and '@' not in email:
            errors.append('El correo electrónico no es válido')

        # Si hay errores básicos, detener
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'rappiSafe/admin/crear_operador.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'telefono': telefono
            })

        # Validar unicidad
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso')
            return render(request, 'rappiSafe/admin/crear_operador.html', {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'telefono': telefono
            })

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado')
            return render(request, 'rappiSafe/admin/crear_operador.html', {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'telefono': telefono
            })

        # Limpiar teléfono
        telefono_limpio = ''.join(c for c in telefono if c.isdigit() or c == '+') if telefono else None

        # Crear operador
        try:
            with transaction.atomic():
                logger.info(f'Creando operador {username}...')

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    telefono=telefono_limpio,
                    rol='operador',
                    activo=True
                )
                logger.info(f'Operador creado con ID {user.id}')

            messages.success(request, f'Operador {username} creado exitosamente.')
            logger.info(f'=== OPERADOR CREADO EXITOSAMENTE ===')
            return redirect('gestionar_usuarios')

        except Exception as e:
            logger.error(f'ERROR al crear operador: {str(e)}', exc_info=True)
            messages.error(request, 'Error al crear el operador. Por favor intenta nuevamente.')
            return render(request, 'rappiSafe/admin/crear_operador.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'telefono': telefono
            })

    return render(request, 'rappiSafe/admin/crear_operador.html')
