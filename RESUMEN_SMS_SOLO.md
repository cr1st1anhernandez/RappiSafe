# Resumen: Sistema de Notificaciones SMS Únicamente

## Estado Actual

El sistema **solo envía SMS** usando MoceanAPI cuando se activa una alerta SOS. Se han eliminado todas las demás opciones de notificación (Telegram, Email, modo simulado).

## Flujo de Funcionamiento

### Cuando un repartidor activa el SOS:

1. **Trigger:** `crear_alerta_panico()` en `rappiSafe/views.py:113`
   - Usuario presiona botón SOS 3 segundos
   - O sensor de agitación detecta 3 sacudidas

2. **Procesamiento:** `notificar_contactos_emergencia()` en `rappiSafe/utils.py:260`
   - Obtiene todos los contactos validados del repartidor
   - Genera mensaje personalizado con ubicación y hora
   - Itera sobre cada contacto

3. **Envío:** `enviar_notificacion_contacto()` en `rappiSafe/utils.py:600`
   - **Solo envía SMS con MoceanAPI**
   - Valida que el contacto tenga teléfono
   - Trunca mensaje a 160 caracteres
   - Retorna éxito o error

4. **Registro:**
   - Cada intento se guarda en `NotificacionContacto`
   - Método siempre es 'sms'
   - Estado: 'enviado' o 'fallido'

## Mensaje SMS Enviado

```
!!! ALERTA DE PÁNICO - RAPPI SAFE !!!

[Nombre del repartidor] ha activado una alerta de emergencia.

Ubicación:
https://www.google.com/maps?q=[lat],[lon]

Hora: [DD/MM/YYYY HH:MM]

Este mensaje es automático. Por favor, contacte inmediatamente con [Nombre] o las autoridades.
```

## Requisitos para que Funcione

### 1. Configuración del Sistema
- ✅ Token de MoceanAPI en `.env`: `MOCEAN_API_TOKEN=apit-VJujvCC1muCK0Cq8gGjtOibeYM7masjT-1C2k4`
- ✅ SDK instalado: `moceansdk==1.2.0`
- ✅ Código modificado para usar solo SMS

### 2. Configuración de Contactos
Los contactos de emergencia deben:
- ✅ Estar validados (`validado=True` en la BD)
- ✅ Tener número telefónico configurado
- ✅ Número en formato internacional (sin +): `60123456789`, `521234567890`, etc.

### 3. Créditos de MoceanAPI
- Verificar saldo en: https://dashboard.moceanapi.com/
- El sistema NO fallará si no hay créditos, solo registrará el error

## Archivos Modificados

1. **`rappiSafe/utils.py`**
   - Línea 509: Nueva función `enviar_sms_mocean()`
   - Línea 600: `enviar_notificacion_contacto()` simplificada (solo SMS)
   - Línea 325: `notificar_contactos_emergencia()` actualizada

2. **`.env`**
   - Agregado: `MOCEAN_API_TOKEN=apit-VJujvCC1muCK0Cq8gGjtOibeYM7masjT-1C2k4`

3. **`requirements.txt`**
   - Agregado: `moceansdk==1.2.0`

## Ventajas de Usar Solo SMS

1. **Simplicidad:** Un solo canal de comunicación
2. **Confiabilidad:** SMS funciona sin internet
3. **Universal:** Todos los teléfonos reciben SMS
4. **Directo:** No requiere apps adicionales
5. **Urgencia:** SMS llega inmediatamente

## Lo que se Eliminó

- ❌ Notificaciones por Telegram
- ❌ Notificaciones por Email
- ❌ Modo "simulado" de prueba
- ❌ Lógica de "intentar múltiples canales"

## Testing

### Prueba Rápida
```bash
python test_sms_simple.py
```

### Desde Django Shell
```python
python manage.py shell

from rappiSafe.utils import enviar_sms_mocean

resultado = enviar_sms_mocean(
    telefono="60123456789",
    mensaje="Prueba de SMS"
)

print(resultado)
```

### Verificar Logs
Cuando se envía una alerta, buscar en la consola:
```
📱 Enviando SMS por MOCEAN a [telefono]
✅ SMS enviado exitosamente!
   Message ID: [id]
   Receptor: [numero]
```

## Monitoreo

### Dashboard de MoceanAPI
- URL: https://dashboard.moceanapi.com/
- Ver: Créditos restantes, historial de SMS, mensajes fallidos

### Base de Datos
```sql
-- Ver últimas notificaciones enviadas
SELECT * FROM rappiSafe_notificacioncontacto
ORDER BY creado_en DESC
LIMIT 10;

-- Contar éxitos vs fallos
SELECT estado, COUNT(*)
FROM rappiSafe_notificacioncontacto
WHERE metodo='sms'
GROUP BY estado;
```

## Troubleshooting

### "❌ El contacto no tiene teléfono configurado"
**Solución:** Agregar número en el perfil del contacto en formato internacional

### "❌ Error Mocean: Authorization failed"
**Solución:** Verificar token en `.env` y reiniciar servidor

### "SMS no llega al destinatario"
**Verificar:**
1. Créditos en dashboard de MoceanAPI
2. Formato del número (sin +, sin espacios)
3. País del número soportado por MoceanAPI
4. Logs del servidor para ver respuesta de API

### "No se envían SMS en producción"
**Verificar:**
1. Archivo `.env` existe en el servidor
2. Variable `MOCEAN_API_TOKEN` está configurada
3. Servidor Django se reinició después de agregar token
4. Contactos están marcados como validados

## Próximos Pasos Opcionales

1. **Rate Limiting:** Evitar spam de SMS
2. **Retry Logic:** Reintentar automáticamente si falla
3. **Confirmación de Entrega:** Webhooks de MoceanAPI
4. **Dashboard:** Panel de estadísticas de SMS enviados
5. **Alertas de Créditos:** Notificar cuando se agoten créditos

## Soporte

- **MoceanAPI:** support@moceanapi.com
- **Docs:** https://docs.moceanapi.com/
- **Código:** Ver `rappiSafe/utils.py` líneas 509-645
