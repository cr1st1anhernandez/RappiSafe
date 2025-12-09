# 📱 Cómo Acceder a RappiSafe desde tu Teléfono

## 🎯 Tu IP Local: **192.168.0.93**

---

## ✅ Pasos para Acceder

### 1. Verifica que tu Teléfono esté en la MISMA Red WiFi

**IMPORTANTE:** Tu teléfono y tu computadora deben estar conectados a la **misma red WiFi**.

---

### 2. Asegúrate que el Servidor esté Corriendo

En tu computadora, el servidor debe estar activo:

```bash
daphne -b 0.0.0.0 -p 8001 mysite.asgi:application
```

Deberías ver:
```
Starting server at tcp:port=8001:interface=0.0.0.0
Listening on TCP address 0.0.0.0:8001
```

---

### 3. Abre el Navegador en tu Teléfono

En tu teléfono, abre **Chrome**, **Safari** o cualquier navegador y ve a:

```
http://192.168.0.93:8001
```

O directamente al login:

```
http://192.168.0.93:8001/login/
```

---

## 🧪 Funcionalidades para Probar en el Teléfono

Una vez que inicies sesión como **repartidor**, podrás probar:

### ✅ GPS Real del Teléfono
- El sistema usará la ubicación GPS de tu teléfono
- Más preciso que la simulación en PC

### ✅ Detección de Agitación
- **Agita tu teléfono** fuertemente 3 veces
- Se activará una alerta de pánico automáticamente
- Recibe notificaciones por Telegram y Email

### ✅ Botón SOS
- Mantén presionado el botón rojo por 3 segundos
- Envía alerta con tu ubicación GPS real

### ✅ Actualización de Ubicación en Tiempo Real
- El sistema actualiza tu ubicación automáticamente
- Los operadores pueden verte en el mapa

### ✅ Notificaciones Push
- El navegador pedirá permiso para notificaciones
- Recibe alertas en tiempo real

---

## ⚠️ Si No Funciona

### Problema 1: "No se puede acceder al sitio"

**Solución A - Firewall de Windows:**
1. Busca "Firewall de Windows" en el menú de inicio
2. Haz clic en "Permitir una aplicación a través del Firewall"
3. Busca "Python" y activa las casillas de "Privada" y "Pública"

**Solución B - Desactivar temporalmente el firewall:**
1. Busca "Firewall de Windows"
2. Haz clic en "Activar o desactivar Firewall de Windows Defender"
3. Desactiva para "Red privada" temporalmente
4. Prueba de nuevo

---

### Problema 2: "La página no carga"

Verifica:
1. ✅ ¿Estás en la misma WiFi que la computadora?
2. ✅ ¿El servidor está corriendo? (revisa la ventana de comando)
3. ✅ ¿La IP es correcta? (ejecuta `python obtener_ip.py` si cambió)

---

### Problema 3: "Error 500" o "Error 400"

**Solución:** Ya está configurado `ALLOWED_HOSTS = ['*']` en settings.py

Si persiste, reinicia el servidor:
1. Presiona `Ctrl+C` para detener
2. Vuelve a ejecutar: `daphne -b 0.0.0.0 -p 8001 mysite.asgi:application`

---

## 🔄 Si tu IP Cambia

Tu IP local puede cambiar si:
- Reinicias el router
- Desconectas y reconectas el WiFi
- Cambias de red

**Para obtener la nueva IP:**
```bash
python obtener_ip.py
```

---

## 💡 Tips Adicionales

### Para una IP Fija (Opcional):
1. Ve a la configuración de tu router
2. Busca "DHCP Reservation" o "IP Estática"
3. Asigna una IP fija a tu computadora

### Usar QR Code:
Puedes crear un código QR de la URL para acceder más fácil:
- Ve a: https://www.qr-code-generator.com/
- Ingresa: `http://192.168.0.93:8001`
- Escanea con tu teléfono

---

## 📊 Vista desde el Teléfono

Cuando accedas, verás:
- ✅ Interfaz responsive (adaptada a móvil)
- ✅ Botón SOS grande y fácil de presionar
- ✅ Navegación inferior (Inicio, Perfil, Rutas, etc.)
- ✅ Todas las funcionalidades disponibles

---

## 🎉 ¡Listo!

Una vez configurado, puedes:
1. Caminar con el teléfono
2. Probar el GPS real
3. Agitar para activar alertas
4. Recibir notificaciones de Telegram/Email
5. Ver tu ubicación en tiempo real en el panel de operadores

---

## 🆘 Problemas Comunes

| Problema | Solución |
|----------|----------|
| No carga la página | Verifica firewall y misma red WiFi |
| GPS no funciona | Dale permisos de ubicación al navegador |
| Agitación no detecta | Revisa sensibilidad en "Mi Perfil" |
| No llegan notificaciones | Verifica Telegram ID y email configurados |

---

**🚀 Disfruta probando RappiSafe en tu teléfono con todas las funciones reales!**
