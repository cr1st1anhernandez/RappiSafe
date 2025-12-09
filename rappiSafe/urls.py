from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Repartidor
    path('repartidor/', views.repartidor_home, name='repartidor_home'),
    path('test-sensores/', views.test_sensores, name='test_sensores'),
    path('repartidor/alerta/panico/', views.crear_alerta_panico, name='crear_alerta_panico'),
    path('repartidor/alerta/accidente/', views.crear_alerta_accidente, name='crear_alerta_accidente'),
    path('repartidor/alerta/<uuid:alerta_id>/cancelar/', views.cancelar_alerta, name='cancelar_alerta'),
    path('repartidor/ubicacion/', views.actualizar_ubicacion, name='actualizar_ubicacion'),
    path('repartidor/bateria/', views.actualizar_bateria, name='actualizar_bateria'),
    path('repartidor/contactos/', views.contactos_confianza_view, name='contactos_confianza'),
    path('repartidor/contactos/agregar/', views.agregar_contacto, name='agregar_contacto'),
    path('repartidor/contactos/validar/<int:contacto_id>/', views.validar_contacto, name='validar_contacto'),
    path('repartidor/contactos/eliminar/<int:contacto_id>/', views.eliminar_contacto, name='eliminar_contacto'),
    path('repartidor/ayuda-psicologica/', views.solicitar_ayuda_psicologica_view, name='solicitar_ayuda_psicologica'),
    path('repartidor/mi-perfil/', views.mi_perfil_view, name='mi_perfil'),
    path('repartidor/rutas/', views.rutas_view, name='rutas'),
    path('repartidor/rutas/calcular/', views.calcular_rutas, name='calcular_rutas'),
    path('repartidor/historial/', views.historial_view, name='historial'),

    # Operador
    path('operador/', views.operador_dashboard, name='operador_dashboard'),
    path('operador/alerta/<uuid:alerta_id>/', views.ver_alerta, name='ver_alerta'),
    path('operador/alerta/<uuid:alerta_id>/atender/', views.atender_alerta, name='atender_alerta'),
    path('operador/alerta/<uuid:alerta_id>/cerrar/', views.cerrar_alerta, name='cerrar_alerta'),
    path('operador/incidente/<int:incidente_id>/bitacora/', views.agregar_bitacora, name='agregar_bitacora'),
    path('operador/incidente/<int:incidente_id>/folio/', views.actualizar_folio_911, name='actualizar_folio_911'),
    path('operador/solicitudes-psicologicas/', views.gestionar_solicitudes_psicologicas, name='gestionar_solicitudes_psicologicas'),
    path('operador/solicitud-psicologica/<int:solicitud_id>/atender/', views.atender_solicitud_psicologica, name='atender_solicitud_psicologica'),
    path('operador/reportes/', views.reportes_operador, name='reportes_operador'),
    path('operador/repartidores/', views.lista_repartidores, name='lista_repartidores'),

    # Administrador
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('admin-dashboard/estadisticas/', views.estadisticas_view, name='estadisticas'),
]
