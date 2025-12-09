# 🚀 Inicio Rápido - Telegram (5 minutos)

## ✅ Lo que Ya Está Hecho

- ✅ Código de Telegram implementado
- ✅ Base de datos actualizada
- ✅ Interfaz lista para Telegram IDs y Emails
- ✅ Sistema de prioridad: Telegram > Email > Simulado

---

## 📱 3 Pasos para Activar

### 1️⃣ Crea tu Bot (2 min)

1. Abre Telegram y busca: **@BotFather**
2. Envía: `/newbot`
3. Dale nombre: `RappiSafe Alertas`
4. Dale username: `rappisafe_alertas_bot`
5. **Copia el TOKEN** que te da

### 2️⃣ Configura el Token (1 min)

Abre `.env` y agrega:
```env
TELEGRAM_BOT_TOKEN=TU_TOKEN_AQUI
```

Reinicia el servidor:
```bash
python manage.py runserver
```

### 3️⃣ Obtén tu Telegram ID (1 min)

1. Busca en Telegram: **@userinfobot**
2. Envía: `/start`
3. Copia tu **ID** (ejemplo: `123456789`)

---

## 🎯 Agregar Contacto

1. Ve a **"Mi Perfil"**
2. Haz clic en **"+ Agregar Contacto"**
3. Llena:
   - Nombre: `Yaxche`
   - Teléfono: `+5219515551234` (requerido)
   - **ID de Telegram**: `123456789` ⭐
   - Email: `ejemplo@gmail.com` (opcional)

4. **IMPORTANTE**: El contacto debe buscar tu bot en Telegram y hacer clic en **"Start"** primero

---

## ✅ Probar

1. Ve al Dashboard
2. Mantén presionado el botón **SOS** por 3 segundos
3. ¡El contacto recibirá el mensaje en Telegram!

---

## ❓ ¿No Funciona?

- ¿Agregaste el TOKEN en `.env`?
- ¿Reiniciaste el servidor?
- ¿El contacto hizo clic en "Start" en el bot?
- Revisa la consola para ver errores

---

## 📖 Guía Completa

Lee **`CONFIGURACION_TELEGRAM.md`** para más detalles.

**¡Listo! Notificaciones GRATIS e instantáneas** 🎉
