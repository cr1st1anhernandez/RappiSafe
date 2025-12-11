# Limpieza: Solo SMS via Mocean API

## Resumen de Cambios

Se eliminaron todas las funcionalidades de Telegram y Email, dejando únicamente SMS via Mocean API como método de notificación.

## Archivos Modificados

### 1. `rappiSafe/utils.py`

**Eliminado:**
- Función `enviar_telegram()` (líneas 494-547)
- Función `enviar_email()` (líneas 550-609)

**Modificado:**
- Función `enviar_notificacion_contacto()` (línea 590-628)
  - **Antes**: Intentaba SMS → Telegram → Email → Simulado
  - **Ahora**: Solo intenta SMS via Mocean API

**Nueva lógica simplificada:**
```python
def enviar_notificacion_contacto(contacto, mensaje):
    """Enviar notificación por SMS usando Mocean API"""
    if contacto.telefono:
        resultado = enviar_sms_mocean(contacto.telefono, mensaje)
        if resultado['success']:
            return {'success': True, 'metodo': 'sms', ...}
        else:
            return {'success': False, 'metodo': 'sms', ...}
    else:
        return {'success': False, 'error': 'No hay teléfono'}
```

### 2. `.env`

**Antes:**
```env
# Mocean API
MOCEAN_API_TOKEN=...

# Telegram Bot (respaldo)
TELEGRAM_BOT_TOKEN=...

# Email (respaldo)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
EMAIL_USE_TLS=True
```

**Ahora:**
```env
# Configuración de Mocean API para SMS
MOCEAN_API_TOKEN=apit-qOrNRlPrykyAGoH0h9TSwUK6RSUiXoKb-21OHb
```

### 3. `mysite/settings.py`

**Eliminado:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = ...
EMAIL_HOST_USER = ...
EMAIL_HOST_PASSWORD = ...
```

**Reemplazado por:**
```python
# Configuración de notificaciones
# Solo se usa SMS via Mocean API (configurado en .env: MOCEAN_API_TOKEN)
```

### 4. `test_sms_mocean.py`

**Actualizado:**
- Eliminadas referencias a Telegram Bot y Email
- Actualizado flujo de información
- Simplificado mensaje de configuración actual

## Flujo Actual de Notificaciones

```
Alerta Activada
     ↓
Obtener Contactos de Emergencia
     ↓
Enviar SMS via Mocean API
     ↓
    ✅ Éxito: SMS enviado
    ❌ Fallo: Error registrado
```

## Ventajas de Solo SMS

1. **Simplicidad**: Un solo método de notificación, más fácil de mantener
2. **Fiabilidad**: SMS tiene mayor tasa de entrega que email
3. **Inmediatez**: SMS llega instantáneamente
4. **Sin dependencias**: No requiere que los contactos tengan apps específicas
5. **Menor complejidad**: Menos código, menos puntos de fallo

## Funcionamiento

Cuando se activa una alerta:

1. Sistema obtiene contactos de emergencia del repartidor
2. Para cada contacto:
   - Verifica que tenga teléfono configurado
   - Envía SMS via Mocean API
   - Registra resultado en base de datos (`NotificacionContacto`)
3. Los contactos reciben SMS con:
   - Tipo de alerta (PÁNICO o ACCIDENTE)
   - Nombre del repartidor
   - Ubicación en Google Maps
   - Hora del incidente

## Formato del Mensaje SMS

```
🚨 ALERTA DE PÁNICO - RAPPI SAFE

[Nombre Repartidor] ha activado una alerta de emergencia.

📍 Ubicación: https://www.google.com/maps?q=[lat],[lng]

Hora: [fecha/hora]

Este mensaje es automático. Por favor, contacte inmediatamente
con [Nombre] o las autoridades.
```

## Requisitos para que Funcione

1. **Token Mocean válido**: Configurado en `.env`
2. **Contactos con teléfono**: Formato internacional (+521234567890)
3. **Contactos validados**: Campo `validado=True` en la base de datos
4. **Servidor reiniciado**: Después de cambiar el token

## Verificación

Ejecutar script de prueba:
```bash
python test_sms_mocean.py
```

Debería mostrar:
```
[OK] Token configurado
[OK] SDK de Mocean instalado
Metodo de envio: SMS via Mocean API
```

## Costos

- **Mocean API**: Pago por SMS enviado
- **No hay costos** de Telegram o email
- Monitorear saldo en: https://dashboard.moceanapi.com/

## Próximos Pasos

1. **Reiniciar servidor Django** para aplicar cambios
2. **Probar envío de SMS** usando el script de prueba
3. **Activar alerta** desde la app para verificar funcionamiento completo
4. **Monitorear logs** en la consola del servidor

## Notas Importantes

- ✅ Código más limpio y mantenible
- ✅ Una sola dependencia (moceansdk)
- ✅ Flujo de notificación simplificado
- ⚠️ Si falla el SMS, NO hay método de respaldo
- 📊 Importante monitorear créditos de Mocean
