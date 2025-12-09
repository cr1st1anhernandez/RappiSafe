from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid


class User(AbstractUser):
    """
    Modelo de usuario extendido con roles
    """
    ROLES = (
        ('repartidor', 'Repartidor'),
        ('operador', 'Operador'),
        ('administrador', 'Administrador'),
    )

    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    rol = models.CharField(max_length=20, choices=ROLES, default='repartidor', verbose_name='Rol')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    telefono_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número telefónico debe estar en formato: '+999999999'. Hasta 15 dígitos permitidos."
    )
    telefono = models.CharField(validators=[telefono_regex], max_length=17, blank=True, verbose_name='Teléfono')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"


class RepartidorProfile(models.Model):
    """
    Perfil extendido para repartidores
    """
    ESTADOS = (
        ('disponible', 'Disponible'),
        ('en_ruta', 'En Ruta'),
        ('emergencia', 'Emergencia'),
        ('offline', 'Offline'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_repartidor')
    ultima_latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Última latitud')
    ultima_longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Última longitud')
    ultima_actualizacion_ubicacion = models.DateTimeField(null=True, blank=True, verbose_name='Última actualización de ubicación')
    nivel_bateria = models.IntegerField(null=True, blank=True, verbose_name='Nivel de batería (%)')
    ultima_actualizacion_bateria = models.DateTimeField(null=True, blank=True, verbose_name='Última actualización de batería')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='offline', verbose_name='Estado')
    foto = models.ImageField(upload_to='perfiles/', null=True, blank=True, verbose_name='Foto de perfil')
    numero_identificacion = models.CharField(max_length=50, unique=True, verbose_name='Número de identificación')

    # Información de seguro (opcional)
    tiene_seguro = models.BooleanField(default=False, verbose_name='¿Tiene seguro?')
    nombre_aseguradora = models.CharField(max_length=100, blank=True, verbose_name='Nombre de la aseguradora')
    numero_poliza = models.CharField(max_length=50, blank=True, verbose_name='Número de póliza')
    telefono_aseguradora = models.CharField(max_length=20, blank=True, verbose_name='Teléfono de la aseguradora')
    vigencia_seguro = models.DateField(null=True, blank=True, verbose_name='Vigencia del seguro')

    # Configuración de detección de agitación
    sensibilidad_agitacion = models.IntegerField(default=15, verbose_name='Sensibilidad de agitación (10-30)')
    agitacion_habilitada = models.BooleanField(default=True, verbose_name='Detección de agitación habilitada')

    class Meta:
        verbose_name = 'Perfil de Repartidor'
        verbose_name_plural = 'Perfiles de Repartidores'

    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"


class Alerta(models.Model):
    """
    Modelo para alertas de pánico y automáticas
    """
    TIPOS = (
        ('panico', 'Pánico'),
        ('accidente', 'Accidente Detectado'),
    )

    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_atencion', 'En Atención'),
        ('atendida', 'Atendida'),
        ('cerrada', 'Cerrada'),
        ('falsa_alarma', 'Falsa Alarma'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repartidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas', limit_choices_to={'rol': 'repartidor'})
    tipo = models.CharField(max_length=20, choices=TIPOS, verbose_name='Tipo de alerta')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente', verbose_name='Estado')
    latitud = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitud')
    longitud = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitud')
    nivel_bateria = models.IntegerField(null=True, blank=True, verbose_name='Nivel de batería (%)')
    datos_sensores = models.JSONField(null=True, blank=True, verbose_name='Datos de sensores')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    atendido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas_atendidas', limit_choices_to={'rol': 'operador'})
    notas_iniciales = models.TextField(blank=True, verbose_name='Notas iniciales')

    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-creado_en']

    def __str__(self):
        return f"Alerta {self.get_tipo_display()} - {self.repartidor.get_full_name()} - {self.creado_en.strftime('%Y-%m-%d %H:%M')}"


class Trayectoria(models.Model):
    """
    Modelo para registrar la trayectoria del repartidor durante una alerta
    """
    alerta = models.ForeignKey(Alerta, on_delete=models.CASCADE, related_name='trayectorias')
    latitud = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitud')
    longitud = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitud')
    precision = models.FloatField(null=True, blank=True, verbose_name='Precisión (metros)')
    velocidad = models.FloatField(null=True, blank=True, verbose_name='Velocidad (m/s)')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora')

    class Meta:
        verbose_name = 'Punto de Trayectoria'
        verbose_name_plural = 'Trayectorias'
        ordering = ['timestamp']

    def __str__(self):
        return f"Trayectoria de alerta {self.alerta.id} - {self.timestamp.strftime('%H:%M:%S')}"


class ContactoConfianza(models.Model):
    """
    Contactos de confianza de un repartidor
    """
    repartidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contactos_confianza', limit_choices_to={'rol': 'repartidor'})
    nombre = models.CharField(max_length=100, verbose_name='Nombre completo')
    telefono_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número telefónico debe estar en formato: '+999999999'. Hasta 15 dígitos permitidos."
    )
    telefono = models.CharField(validators=[telefono_regex], max_length=17, verbose_name='Teléfono')
    relacion = models.CharField(max_length=50, blank=True, verbose_name='Relación')
    validado = models.BooleanField(default=False, verbose_name='Validado')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')

    class Meta:
        verbose_name = 'Contacto de Confianza'
        verbose_name_plural = 'Contactos de Confianza'
        unique_together = ['repartidor', 'telefono']

    def __str__(self):
        return f"{self.nombre} - {self.telefono}"


class Incidente(models.Model):
    """
    Incidente asociado a una alerta con seguimiento detallado
    """
    ESTADOS = (
        ('abierto', 'Abierto'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    )

    alerta = models.OneToOneField(Alerta, on_delete=models.CASCADE, related_name='incidente')
    operador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='incidentes_asignados', limit_choices_to={'rol': 'operador'})
    folio_911 = models.CharField(max_length=50, blank=True, verbose_name='Folio 911')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierto', verbose_name='Estado')
    notas = models.TextField(blank=True, verbose_name='Notas del incidente')
    contactos_notificados = models.BooleanField(default=False, verbose_name='Contactos notificados')
    autoridades_contactadas = models.BooleanField(default=False, verbose_name='Autoridades contactadas')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    cerrado_en = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de cierre')
    tiempo_respuesta = models.DurationField(null=True, blank=True, verbose_name='Tiempo de respuesta')

    class Meta:
        verbose_name = 'Incidente'
        verbose_name_plural = 'Incidentes'
        ordering = ['-creado_en']

    def __str__(self):
        return f"Incidente {self.id} - Alerta {self.alerta.id}"


class Bitacora(models.Model):
    """
    Bitácora de acciones realizadas durante un incidente
    """
    incidente = models.ForeignKey(Incidente, on_delete=models.CASCADE, related_name='bitacoras')
    operador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'rol': 'operador'})
    accion = models.TextField(verbose_name='Acción realizada')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora')

    class Meta:
        verbose_name = 'Entrada de Bitácora'
        verbose_name_plural = 'Bitácoras'
        ordering = ['timestamp']

    def __str__(self):
        return f"Bitácora {self.incidente.id} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class EstadisticaRiesgo(models.Model):
    """
    Estadísticas de riesgo por zona geográfica
    """
    nombre_zona = models.CharField(max_length=200, verbose_name='Nombre de la zona')
    coordenadas_zona = models.JSONField(verbose_name='Coordenadas de la zona (GeoJSON)')
    puntuacion_riesgo = models.FloatField(verbose_name='Puntuación de riesgo (0-100)')
    total_alertas = models.IntegerField(default=0, verbose_name='Total de alertas')
    alertas_panico = models.IntegerField(default=0, verbose_name='Alertas de pánico')
    alertas_accidente = models.IntegerField(default=0, verbose_name='Alertas de accidente')
    ultima_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    periodo_inicio = models.DateField(verbose_name='Inicio del período')
    periodo_fin = models.DateField(verbose_name='Fin del período')

    class Meta:
        verbose_name = 'Estadística de Riesgo'
        verbose_name_plural = 'Estadísticas de Riesgo'
        ordering = ['-puntuacion_riesgo']

    def __str__(self):
        return f"{self.nombre_zona} - Riesgo: {self.puntuacion_riesgo}"


class SolicitudAyudaPsicologica(models.Model):
    """
    Solicitudes de ayuda psicológica de repartidores
    """
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('atendida', 'Atendida'),
        ('cerrada', 'Cerrada'),
    )

    repartidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_psicologicas', limit_choices_to={'rol': 'repartidor'})
    descripcion = models.TextField(verbose_name='Descripción de la solicitud')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente', verbose_name='Estado')
    urgencia = models.IntegerField(default=5, verbose_name='Nivel de urgencia (1-10)')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de solicitud')
    atendido_en = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de atención')
    notas_atencion = models.TextField(blank=True, verbose_name='Notas de atención')

    class Meta:
        verbose_name = 'Solicitud de Ayuda Psicológica'
        verbose_name_plural = 'Solicitudes de Ayuda Psicológica'
        ordering = ['-creado_en']

    def __str__(self):
        return f"Solicitud {self.id} - {self.repartidor.get_full_name()} - {self.get_estado_display()}"


class RutaSegura(models.Model):
    """
    Rutas seguras calculadas y guardadas
    """
    repartidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rutas', limit_choices_to={'rol': 'repartidor'})
    origen_lat = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitud origen')
    origen_lon = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitud origen')
    destino_lat = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitud destino')
    destino_lon = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitud destino')
    ruta_rapida = models.JSONField(verbose_name='Datos de ruta rápida')
    ruta_segura = models.JSONField(verbose_name='Datos de ruta segura')
    puntuacion_riesgo_rapida = models.FloatField(verbose_name='Riesgo ruta rápida')
    puntuacion_riesgo_segura = models.FloatField(verbose_name='Riesgo ruta segura')
    seleccionada = models.CharField(max_length=10, choices=[('rapida', 'Rápida'), ('segura', 'Segura')], verbose_name='Ruta seleccionada')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de cálculo')

    class Meta:
        verbose_name = 'Ruta Segura'
        verbose_name_plural = 'Rutas Seguras'
        ordering = ['-creado_en']

    def __str__(self):
        return f"Ruta de {self.repartidor.get_full_name()} - {self.creado_en.strftime('%Y-%m-%d %H:%M')}"


class NotificacionContacto(models.Model):
    """
    Registro de notificaciones enviadas a contactos de emergencia
    """
    METODOS = (
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('llamada', 'Llamada'),
    )

    ESTADOS = (
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('fallido', 'Fallido'),
        ('pendiente', 'Pendiente'),
    )

    alerta = models.ForeignKey(Alerta, on_delete=models.CASCADE, related_name='notificaciones_contactos')
    contacto = models.ForeignKey(ContactoConfianza, on_delete=models.CASCADE, related_name='notificaciones')
    metodo = models.CharField(max_length=20, choices=METODOS, default='sms', verbose_name='Método de notificación')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente', verbose_name='Estado')
    mensaje = models.TextField(verbose_name='Mensaje enviado')
    respuesta_api = models.JSONField(null=True, blank=True, verbose_name='Respuesta del servicio')
    enviado_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de envío')
    error_mensaje = models.TextField(blank=True, verbose_name='Mensaje de error')

    class Meta:
        verbose_name = 'Notificación a Contacto'
        verbose_name_plural = 'Notificaciones a Contactos'
        ordering = ['-enviado_en']

    def __str__(self):
        return f"Notificación a {self.contacto.nombre} - {self.get_metodo_display()}"
