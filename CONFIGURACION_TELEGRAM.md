# 📱 Configuración de Notificaciones por Telegram (GRATIS)

## ⭐ ¿Por Qué Telegram?

- ✅ **Completamente GRATIS** - sin límites, sin costos
- ✅ **Sin restricciones** - funciona en todos los países
- ✅ **Instantáneo** - mensajes llegan en segundos
- ✅ **Fácil de configurar** - solo 5 minutos
- ✅ **Más confiable** - no depende de operadoras telefónicas
- ✅ **Sin verificación** - no necesitas verificar números

---

## 🚀 Configuración Rápida (5 minutos)

### Paso 1: Crear tu Bot de Telegram (2 minutos)

1. **Abre Telegram** en tu teléfono o computadora

2. **Busca** el usuario: `@BotFather`
   - Es el bot oficial de Telegram para crear bots
   - Tiene una palomita azul de verificación ✅

3. **Inicia conversación** enviando: `/start`

4. **Crea tu bot** enviando: `/newbot`

5. **Nombre del bot**: Elige un nombre para tu bot
   ```
   Ejemplo: RappiSafe Alertas
   ```

6. **Username del bot**: Debe terminar en "bot"
   ```
   Ejemplo: rappisafe_alertas_bot
   ```

7. **Copia el TOKEN**: BotFather te dará algo como:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   ```
   ⚠️ **GUARDA ESTE TOKEN** - lo necesitarás en el siguiente paso

### Paso 2: Configurar el TOKEN en RappiSafe (1 minuto)

1. Abre el archivo `.env` en la raíz del proyecto

2. Pega tu token de Telegram:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   ```

3. **Reinicia el servidor Django**:
   ```bash
   # Detén el servidor (Ctrl+C) y vuelve a iniciarlo
   python manage.py runserver
   ```

### Paso 3: Obtener tu Telegram ID (1 minuto)

Cada contacto de emergencia necesita su Telegram ID:

1. **Abre Telegram** y busca: `@userinfobot`

2. **Envía**: `/start`

3. El bot te responderá con tu información, incluyendo tu **ID**:
   ```
   Id: 123456789
   ```

4. **Copia ese número** - es tu Telegram ID

### Paso 4: Iniciar Chat con tu Bot (1 minuto)

⚠️ **IMPORTANTE**: Cada persona debe iniciar conversación con el bot primero.

1. **Busca tu bot** en Telegram por el username que le pusiste
   ```
   Ejemplo: @rappisafe_alertas_bot
   ```

2. **Haz clic en "Start"** o envía `/start`

3. ¡Listo! Ya pueden recibir alertas

---

## 📝 Agregar Contactos en RappiSafe

1. Inicia sesión como **repartidor**

2. Ve a **"Mi Perfil"**

3. En **"Contactos de Emergencia"**, haz clic en **"+ Agregar Contacto"**

4. Llena el formulario:
   - **Nombre**: Nombre del contacto
   - **Teléfono**: +5219515551234 (requerido, aunque se use Telegram)
   - **ID de Telegram**: 123456789 (el ID que obtuviste en Paso 3)
   - **Email**: opcional, como backup
   - **Relación**: Familiar, amigo, etc.

5. **Guardar**

---

## 🎯 Probar que Funciona

1. Ve al **Dashboard del repartidor**

2. Mantén presionado el **botón SOS rojo** por 3 segundos

3. El contacto debería recibir un mensaje en Telegram en segundos:
   ```
   🚨 ALERTA DE PÁNICO - RAPPI SAFE

   Juan Pérez ha activado una alerta de emergencia.

   📍 Ubicación: https://www.google.com/maps?q=19.4326,-99.1332

   Hora: 09/12/2025 14:30

   Este mensaje es automático...
   ```

4. En la **consola del servidor** verás:
   ```
   📱 Enviando mensaje por TELEGRAM a 123456789
   ✅ Mensaje de Telegram enviado exitosamente!
   ✅ Notificación enviada a Juan Pérez via TELEGRAM
   ```

---

## 🔧 Solución de Problemas

### "Error: No hay token de Telegram configurado"
- ✅ Verifica que agregaste el token en `.env`
- ✅ Reinicia el servidor después de editar `.env`

### "Error: Chat not found"
- ✅ La persona debe iniciar conversación con el bot primero
- ✅ Busca el bot en Telegram y haz clic en "Start"

### "No llega el mensaje"
- ✅ Verifica que el Telegram ID sea correcto
- ✅ Verifica que iniciaste conversación con el bot
- ✅ Revisa la consola del servidor para errores

### "El servidor no arranca después de configurar"
- ✅ Verifica que instalaste: `pip install python-telegram-bot`
- ✅ Verifica que el token esté bien copiado (sin espacios extras)

---

## 📊 Ventajas vs SMS

| Característica | Telegram | SMS (Twilio) |
|----------------|----------|--------------|
| **Costo** | ✅ GRATIS | ❌ $0.045 USD c/u |
| **Restricciones** | ✅ Ninguna | ❌ Requiere verificar números |
| **Países** | ✅ Todos | ❌ Algunos restringidos |
| **Velocidad** | ✅ Instantáneo | ⚠️ 1-10 segundos |
| **Confiabilidad** | ✅ 99.9% | ⚠️ Depende operadora |
| **Multimedia** | ✅ Soporta fotos/ubicación | ❌ Solo texto |

---

## 🎨 Ejemplo de Mensaje que Llega

Cuando se activa una alerta, el contacto recibe:

```
🚨 ALERTA DE PÁNICO - RAPPI SAFE

Juan Pérez ha activado una alerta de emergencia.

📍 Ubicación: https://www.google.com/maps?q=19.4326,-99.1332

Hora: 09/12/2025 14:30

Este mensaje es automático. Por favor, contacte inmediatamente
con Juan Pérez o las autoridades.
```

El mensaje incluye:
- ✅ Tipo de alerta (pánico o accidente)
- ✅ Nombre del repartidor
- ✅ **Link directo a Google Maps** con la ubicación
- ✅ Fecha y hora exacta
- ✅ Instrucciones claras

---

## 💡 Tips Importantes

### Para Repartidores:
1. **Agrega al menos 2 contactos** con Telegram ID
2. **Pídeles que inicien conversación** con el bot antes
3. **Prueba el sistema** antes de salir a trabajar

### Para Contactos de Emergencia:
1. **Instala Telegram** si no lo tienes
2. **Busca el bot** y haz clic en "Start"
3. **Obtén tu ID** con @userinfobot
4. **Mantén Telegram activo** - las notificaciones llegarán aunque la app esté cerrada

---

## 🔐 Privacidad y Seguridad

- ✅ **Cifrado**: Telegram usa cifrado de extremo a extremo
- ✅ **Privado**: Solo tú y tus contactos ven las alertas
- ✅ **Sin spam**: El bot solo envía alertas de emergencia
- ✅ **Control total**: Puedes pausar o eliminar el bot cuando quieras

---

## 📧 Alternativa: Email

Si prefieres, también puedes usar **Email** como método de notificación:

1. Configura el email en `.env`:
   ```env
   EMAIL_HOST_USER=tu_email@gmail.com
   EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
   ```

2. Para Gmail, necesitas una **contraseña de aplicación**:
   - Ve a: https://myaccount.google.com/apppasswords
   - Genera una contraseña para "RappiSafe"
   - Úsala en EMAIL_HOST_PASSWORD

3. Agrega el email del contacto en el formulario

**Prioridad de envío**:
1. ✅ **Telegram** (si tiene ID)
2. ✅ **Email** (si no tiene Telegram)
3. ⚠️ **Simulado** (si no tiene ninguno)

---

## ✅ Checklist Final

Antes de usar en producción, verifica:

- [ ] Bot creado en BotFather
- [ ] Token configurado en `.env`
- [ ] Servidor reiniciado
- [ ] python-telegram-bot instalado (`pip install python-telegram-bot`)
- [ ] Contactos con Telegram ID agregados
- [ ] Contactos iniciaron conversación con el bot
- [ ] Prueba exitosa del botón SOS

**¡Listo para producción!** 🚀

---

## 🆘 Soporte

- **Documentación Telegram Bot API**: https://core.telegram.org/bots/api
- **BotFather Commands**: https://core.telegram.org/bots#6-botfather
- **Python Telegram Bot**: https://docs.python-telegram-bot.org/

---

**🎉 ¡Disfruta de notificaciones GRATIS e instantáneas!**
