# Integración de MoceanAPI para Envío de SMS en Alertas SOS

## Descripción

Se ha integrado **MoceanAPI** para enviar mensajes SMS a los contactos de emergencia cuando un repartidor activa el botón SOS o cuando se detecta una agitación del dispositivo.

## Cambios Realizados

### 1. Instalación de Dependencias

Se agregó el SDK de MoceanAPI al proyecto:

```bash
pip install moceansdk==1.2.0
```

Actualizado en `requirements.txt`:
```
moceansdk==1.2.0
```

### 2. Configuración del Token API

Se agregó la configuración del token de MoceanAPI en los archivos de entorno:

**`.env`** (archivo real con credenciales):
```env
MOCEAN_API_TOKEN=apit-VJujvCC1muCK0Cq8gGjtOibeYM7masjT-1C2k4
```

**`.env.example`** (plantilla para otros desarrolladores):
```env
MOCEAN_API_TOKEN=tu_token_aqui
```

### 3. Nueva Función de Envío de SMS

Se agregó la función `enviar_sms_mocean()` en `rappiSafe/utils.py`:

**Ubicación:** `rappiSafe/utils.py:509`

**Características:**
- Envía SMS usando la API REST de MoceanAPI
- Limpia automáticamente el formato del número telefónico
- Maneja errores y retorna respuestas estructuradas
- Registra logs detallados del proceso de envío

**Ejemplo de uso:**
```python
from rappiSafe.utils import enviar_sms_mocean

resultado = enviar_sms_mocean(
    telefono="60123456789",  # Formato internacional sin +
    mensaje="ALERTA: Mensaje de emergencia"
)

if resultado['success']:
    print(f"SMS enviado exitosamente: {resultado['respuesta']}")
else:
    print(f"Error al enviar SMS: {resultado['error']}")
```

### 4. Integración en el Sistema de Notificaciones

Se modificó la función `enviar_notificacion_contacto()` para enviar ÚNICAMENTE SMS:

**Ubicación:** `rappiSafe/utils.py:600`

**Método de notificación:**
- **SMS via MoceanAPI** - Único método habilitado

**Características:**
- Trunca automáticamente mensajes largos a 160 caracteres para SMS
- Valida que el contacto tenga teléfono configurado
- Registra éxitos y fallos en la base de datos
- Retorna información detallada del envío

### 5. Integración con Alertas SOS

Cuando un repartidor activa el SOS (botón o agitación), el sistema:

1. Crea una alerta en la base de datos
2. Notifica a los operadores vía WebSocket
3. **Envía SMS a todos los contactos de emergencia validados**

**Ubicación del trigger:** `rappiSafe/views.py:113` (función `crear_alerta_panico`)

## Formato del Mensaje SMS

El mensaje enviado a los contactos de emergencia incluye:

```
🚨 ALERTA DE PÁNICO - RAPPI SAFE

[Nombre del repartidor] ha activado una alerta de emergencia.

📍 Ubicación: https://www.google.com/maps?q=[lat],[lon]

Hora: [DD/MM/YYYY HH:MM]

Este mensaje es automático. Por favor, contacte inmediatamente con [Nombre] o las autoridades.
```

**Nota:** Para SMS, el mensaje se trunca a 160 caracteres automáticamente.

## Testing

### Script de Prueba Simple

Se ha creado un script de prueba en `test_sms_simple.py`:

```bash
python test_sms_simple.py
```

Este script:
1. Verifica que el token esté configurado en `.env`
2. Solicita un número de teléfono
3. Envía un SMS de prueba
4. Muestra el resultado y los detalles de la respuesta

### Prueba Manual

Para probar manualmente desde la consola de Django:

```python
python manage.py shell

# En la consola:
from rappiSafe.utils import enviar_sms_mocean

# Enviar SMS de prueba
resultado = enviar_sms_mocean(
    telefono="60123456789",  # Reemplaza con tu número
    mensaje="Prueba desde Django shell"
)

print(resultado)
```

## Formato de Números Telefónicos

MoceanAPI requiere números en formato internacional **sin el símbolo +**:

**Correcto:**
- `60123456789` (Malasia)
- `521234567890` (México)
- `14155551234` (USA)

**Incorrecto:**
- `+60123456789`
- `(123) 456-7890`
- `123-456-7890`

La función `enviar_sms_mocean()` limpia automáticamente el formato, pero es recomendable guardar los números en formato internacional en la base de datos.

## Costos y Límites

**MoceanAPI - Plan Gratuito:**
- Créditos de prueba limitados
- Pricing por país (varía)
- Ver precios en: https://www.moceanapi.com/pricing

**Recomendación:** Monitorear el uso de créditos en el dashboard de MoceanAPI.

## Seguridad

1. **Token de API:**
   - Nunca commitear el archivo `.env` al repositorio
   - El token está en `.gitignore`
   - Usar `.env.example` como plantilla

2. **Validación de Números:**
   - Solo se envían SMS a contactos validados (`validado=True`)
   - Los números se limpian antes de enviar

3. **Rate Limiting:**
   - MoceanAPI tiene límites de tasa
   - El sistema no implementa throttling adicional actualmente
   - Considerar agregar rate limiting para producción

## Troubleshooting

### Error: "No hay token de MoceanAPI configurado"

**Solución:**
```bash
# 1. Verifica que existe el archivo .env
ls .env

# 2. Verifica que contiene el token
cat .env | grep MOCEAN

# 3. Reinicia el servidor Django
python manage.py runserver
```

### Error: "Authorization failed"

**Causa:** Token inválido o expirado

**Solución:**
1. Verifica el token en https://dashboard.moceanapi.com/
2. Copia el token correcto al archivo `.env`
3. Reinicia el servidor

### Error: "Invalid phone number format"

**Causa:** Formato de número incorrecto

**Solución:**
- Usa formato internacional sin +
- Ejemplo correcto: `60123456789`
- Ejemplo incorrecto: `+60 12 345 6789`

### SMS no llega

**Posibles causas:**
1. Sin créditos en la cuenta de MoceanAPI
2. Número bloqueado o inválido
3. Problemas con el operador telefónico
4. Número no registrado en el país soportado

**Verificación:**
1. Revisar logs del servidor Django
2. Verificar créditos en dashboard de MoceanAPI
3. Revisar logs de envío en MoceanAPI

## Próximos Pasos (Opcional)

1. **Rate Limiting:** Implementar throttling para evitar spam
2. **Retry Logic:** Reintentar envíos fallidos automáticamente
3. **Analytics:** Dashboard de estadísticas de envíos
4. **Templates:** Sistema de plantillas de mensajes personalizables
5. **Webhooks:** Recibir confirmaciones de entrega desde MoceanAPI
6. **Costos:** Monitoreo de costos y alertas de presupuesto

## Referencias

- **MoceanAPI Docs:** https://docs.moceanapi.com/
- **Dashboard:** https://dashboard.moceanapi.com/
- **Pricing:** https://www.moceanapi.com/pricing
- **SDK Python:** https://github.com/MoceanAPI/moceansdk-python

## Soporte

Para problemas con MoceanAPI:
- Email: support@moceanapi.com
- Docs: https://docs.moceanapi.com/

Para problemas con la integración:
- Revisar logs en `rappiSafe/utils.py`
- Ejecutar script de prueba: `python test_sms_simple.py`
