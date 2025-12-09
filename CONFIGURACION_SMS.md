# Configuración de Notificaciones SMS a Contactos de Emergencia

## Resumen

Cuando un repartidor activa una alerta de pánico (botón SOS o agitación del teléfono), el sistema automáticamente:

1. ✅ Crea la alerta en la base de datos
2. ✅ Notifica a los operadores por WebSocket
3. ✅ **Envía SMS a todos los contactos de emergencia registrados**
4. ✅ Registra cada notificación enviada en la base de datos

## Implementación Actual

### Estado: **SIMULADO** ⚠️

Por ahora, el sistema **simula** el envío de SMS. Los contactos de emergencia son notificados en los logs pero **NO se envían SMS reales**.

### Logs de Notificación

Cuando se activa una alerta, verás en la consola:

```
📱 [SIMULADO] Enviando SMS a +5215512345678
   Mensaje: 🚨 ALERTA DE PÁNICO - RAPPI SAFE...
✅ SMS enviado a Juan Pérez (+5215512345678)
📊 Resultado notificaciones para alerta abc-123:
   ✅ Enviadas: 2
   ❌ Fallidas: 0
```

## Configurar SMS Reales con Twilio

Para enviar SMS reales en producción, sigue estos pasos:

### 1. Crear Cuenta en Twilio

1. Ve a [https://www.twilio.com/](https://www.twilio.com/)
2. Crea una cuenta gratuita (incluye crédito de prueba)
3. Verifica tu número telefónico

### 2. Obtener Credenciales

En el dashboard de Twilio, encontrarás:

- **Account SID**: Identificador de tu cuenta
- **Auth Token**: Token de autenticación
- **Número telefónico**: Tu número de Twilio (debe tener capacidad de SMS)

### 3. Instalar Librería de Twilio

```bash
pip install twilio
```

Agregar a `requirements.txt`:
```
twilio>=8.0.0
```

### 4. Configurar Variables de Entorno

#### Opción A: Archivo `.env` (Desarrollo)

Crear archivo `.env` en la raíz del proyecto:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
TWILIO_PHONE_NUMBER=+14155551234
```

Instalar `python-decouple`:
```bash
pip install python-decouple
```

En `settings.py`:
```python
from decouple import config

TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')
```

#### Opción B: Variables de Sistema (Producción)

**Windows:**
```cmd
setx TWILIO_ACCOUNT_SID "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
setx TWILIO_AUTH_TOKEN "tu_auth_token_aqui"
setx TWILIO_PHONE_NUMBER "+14155551234"
```

**Linux/Mac:**
```bash
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="tu_auth_token_aqui"
export TWILIO_PHONE_NUMBER="+14155551234"
```

### 5. El Código Ya Está Listo

El código en `rappiSafe/utils.py` ya detecta automáticamente si hay credenciales de Twilio configuradas:

```python
def enviar_sms_contacto(telefono, mensaje):
    # Verificar si hay configuración de Twilio
    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_from = os.environ.get('TWILIO_PHONE_NUMBER')

    if twilio_sid and twilio_token and twilio_from:
        # Usar Twilio para enviar SMS reales
        from twilio.rest import Client
        client = Client(twilio_sid, twilio_token)
        message = client.messages.create(
            body=mensaje,
            from_=twilio_from,
            to=telefono
        )
        return {'success': True, 'respuesta': {...}}

    # Si no hay config, simular envío
    return {'success': True, 'respuesta': {'simulado': True}}
```

### 6. Probar el Sistema

1. Configura las variables de entorno
2. Reinicia el servidor Django
3. Activa una alerta de pánico
4. Verifica que los SMS se envíen correctamente

## Formato del Mensaje SMS

Los contactos de emergencia reciben:

```
🚨 ALERTA DE PÁNICO - RAPPI SAFE

Juan Pérez ha activado una alerta de emergencia.

📍 Ubicación: https://www.google.com/maps?q=19.4326,-99.1332

Hora: 09/12/2025 14:30

Este mensaje es automático. Por favor, contacte inmediatamente con Juan Pérez o las autoridades.
```

## Registro de Notificaciones

Todas las notificaciones se registran en el modelo `NotificacionContacto`:

### Campos:
- `alerta`: Alerta relacionada
- `contacto`: Contacto de emergencia
- `metodo`: 'sms', 'whatsapp', 'llamada'
- `estado`: 'enviado', 'entregado', 'fallido', 'pendiente'
- `mensaje`: Texto enviado
- `respuesta_api`: Respuesta del servicio (JSON)
- `error_mensaje`: Mensaje de error si falló
- `enviado_en`: Timestamp

### Acceder a las Notificaciones

En el admin de Django o por código:

```python
from rappiSafe.models import NotificacionContacto

# Ver todas las notificaciones de una alerta
notificaciones = NotificacionContacto.objects.filter(alerta=alerta)

# Verificar notificaciones exitosas
exitosas = NotificacionContacto.objects.filter(estado='enviado').count()

# Ver notificaciones fallidas
fallidas = NotificacionContacto.objects.filter(estado='fallido')
for notif in fallidas:
    print(f"Error al notificar a {notif.contacto.nombre}: {notif.error_mensaje}")
```

## Alternativas a Twilio

Si prefieres otro proveedor de SMS:

### AWS SNS
```python
import boto3

def enviar_sms_aws(telefono, mensaje):
    sns = boto3.client('sns', region_name='us-east-1')
    response = sns.publish(
        PhoneNumber=telefono,
        Message=mensaje
    )
    return response
```

### Vonage (Nexmo)
```python
import vonage

def enviar_sms_vonage(telefono, mensaje):
    client = vonage.Client(key="api_key", secret="api_secret")
    sms = vonage.Sms(client)
    response = sms.send_message({
        "from": "RappiSafe",
        "to": telefono,
        "text": mensaje,
    })
    return response
```

## Costos Estimados (Twilio)

- **SMS en México**: ~$0.045 USD por mensaje
- **SMS en USA**: ~$0.0075 USD por mensaje
- **Cuenta gratuita**: $15 USD de crédito inicial

Con el crédito gratuito puedes enviar aproximadamente:
- 333 SMS en México
- 2000 SMS en USA

## Consideraciones Importantes

### 1. Formato de Números Telefónicos

Los números deben estar en formato internacional:
- ✅ Correcto: `+5215512345678` (México)
- ✅ Correcto: `+14155551234` (USA)
- ❌ Incorrecto: `5512345678`
- ❌ Incorrecto: `55 1234 5678`

### 2. Límites de Twilio

- **Cuenta de prueba**: Solo puede enviar a números verificados
- **Cuenta paga**: Sin restricciones
- **Rate limit**: 1 mensaje por segundo por defecto

### 3. Seguridad

⚠️ **NUNCA** commits las credenciales al repositorio:
```bash
# Agregar a .gitignore
.env
*.env
```

### 4. Monitoreo

Twilio provee:
- Dashboard con logs de todos los SMS
- Webhooks para recibir confirmaciones de entrega
- Métricas de uso y costos

## Soporte y Debugging

### Ver Logs de Envío

Los logs del servidor mostrarán:
```
📱 [SIMULADO] Enviando SMS a +5215512345678  # Sin Twilio
📱 Enviando SMS a +5215512345678 via Twilio  # Con Twilio
✅ SMS enviado a Juan Pérez (+5215512345678)
❌ Error al enviar SMS: [ERROR_MESSAGE]
```

### Problemas Comunes

**Error: "Unable to create record"**
- Verifica que el número esté en formato internacional
- Verifica que tu cuenta de Twilio esté activa

**Error: "Authentication failed"**
- Verifica TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN
- Asegúrate de haber reiniciado el servidor después de configurar

**No se envían SMS**
- Verifica que los contactos tengan números válidos
- Revisa los logs del servidor
- Verifica el dashboard de Twilio para errores

## Conclusión

El sistema de notificaciones a contactos de emergencia está **completamente implementado** y listo para usar. Solo necesitas:

1. ✅ Configurar credenciales de Twilio (o dejar simulado para desarrollo)
2. ✅ Los repartidores agregan sus contactos de emergencia en su perfil
3. ✅ Cuando activan una alerta, los contactos son notificados automáticamente

**¡Listo para producción con Twilio configurado!** 🚀
