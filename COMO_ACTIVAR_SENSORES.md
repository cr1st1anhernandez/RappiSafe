# 📱 Cómo Activar los Sensores de Agitación en tu Teléfono

## ✅ Requisito Previo

Primero asegúrate de tener **activada la detección de agitación** en tu perfil:

1. Ve a **Mi Perfil** en la app
2. Busca la sección **"Detección de Agitación"**
3. Activa el checkbox **"Activar detección de agitación"**
4. Guarda los cambios

---

## 🍎 iPhone (Safari)

### **Paso 1: Configurar Safari**

1. Ve a **Ajustes** de iPhone → **Safari**
2. Baja hasta **"Sensores de Movimiento y Orientación"**
3. **Actívalo** (debe estar en verde) ✅
4. Vuelve a Safari

### **Paso 2: Activar Sensores en RappiSafe**

1. Abre RappiSafe en Safari: `http://192.168.0.93:8001/repartidor/`
2. Verás un cuadro **azul** que dice **"Sensores de Movimiento"**
3. Toca el botón **"Activar Sensores"**
4. Safari te pedirá permiso → Toca **"Permitir"**
5. Verás un mensaje verde: **"Sensores activados"** ✅

### **¿No aparece el cuadro azul?**

- Verifica que la detección de agitación esté **activada** en tu perfil
- Recarga la página (arrastra hacia abajo para refrescar)
- Verifica que estés en **Safari** (no Chrome u otro navegador)

---

## 🤖 Android (Chrome)

### **¡Buenas noticias!**

En Android **NO necesitas activar manualmente** los sensores. Se activan automáticamente cuando cargas la página.

Solo asegúrate de:
1. Tener la detección de agitación **activada** en tu perfil
2. Estar usando **Chrome** (recomendado)
3. Tener los permisos de ubicación configurados (ya lo hiciste con flags)

---

## 🧪 Cómo Probar que Funciona

### **Opción 1: Página de Test (Recomendada)**

1. Ve a: `http://192.168.0.93:8001/test-sensores/`
2. Toca **"Activar Sensores"** (solo en iPhone)
3. **Agita tu teléfono** fuertemente
4. Los valores X, Y, Z deben **cambiar rápidamente**

Si los valores cambian → **¡Los sensores funcionan!** ✅

### **Opción 2: En la App Principal**

1. Ve a: `http://192.168.0.93:8001/repartidor/`
2. **iPhone:** Toca el botón **"Activar Sensores"** si aparece
3. **Android:** No necesitas hacer nada extra
4. **Agita tu teléfono** fuertemente 3 veces
5. Deberías ver una **notificación roja** en pantalla: **"¡Alerta de emergencia enviada!"**

---

## ⚙️ Configurar la Sensibilidad

Si la agitación se activa muy fácil o muy difícil:

1. Ve a **Mi Perfil**
2. En **"Detección de Agitación"**
3. Ajusta el **control deslizante de sensibilidad**:
   - **Valores bajos (10-15)**: Necesitas agitar MUY fuerte (recomendado)
   - **Valores medios (16-20)**: Balance entre seguridad y facilidad
   - **Valores altos (21-30)**: Se activa con movimientos más suaves (puede dar falsas alarmas)

4. **Guarda los cambios**

---

## 🔍 Verificar que Está Activo

Puedes ver en la **consola del navegador** si los sensores están activos:

### **En iPhone (Safari):**
1. Abre Safari → Ajustes → Avanzado → Web Inspector (en Mac con Safari)
2. O simplemente observa si aparece el botón azul de "Activar Sensores"

### **En Android (Chrome):**
1. Ve a `chrome://inspect` en tu computadora
2. Conecta tu teléfono por USB
3. Abre DevTools para la página de RappiSafe
4. Ve a Console
5. Deberías ver: `📱 Detección de agitación ACTIVADA` y `👂 Escuchando eventos de movimiento...`

---

## ❌ Solución de Problemas

### **iPhone: El botón "Activar Sensores" no hace nada**

**Solución:**
1. Ve a **Ajustes** → **Safari** → **Sensores de Movimiento y Orientación**
2. **Actívalo** (si ya estaba activado, desactívalo y vuelve a activarlo)
3. **Cierra Safari completamente** (desliza hacia arriba en el selector de apps)
4. Abre Safari de nuevo y vuelve a RappiSafe
5. Toca "Activar Sensores" de nuevo

### **iPhone: Dice "Permiso denegado"**

Si tocas "Activar Sensores" y dice que el permiso está denegado:

**Solución:**
1. **Ajustes** → **Safari**
2. Baja hasta **"Sitios web"** → **"Sensores de Movimiento"**
3. Busca `192.168.0.93` y cambia a **"Permitir"**
4. Recarga Safari

### **Android: La agitación no se detecta**

**Solución:**
1. Verifica que la detección esté **activada** en tu perfil
2. Abre la consola (F12 en Chrome desktop conectado por USB)
3. Busca mensajes de error
4. Intenta con **más fuerza** al agitar (3 veces rápido)
5. Espera 5 segundos entre pruebas (hay un cooldown)

### **La agitación se activa demasiado fácil**

**Solución:**
- Ve a **Mi Perfil** → **Detección de Agitación**
- **Reduce** el valor de sensibilidad a **10 o 12**
- Guarda los cambios
- Recarga la página de repartidor

### **La agitación NO se activa nunca**

**Solución:**
- Ve a **Mi Perfil** → **Detección de Agitación**
- **Aumenta** el valor de sensibilidad a **22 o 25**
- Guarda los cambios
- Recarga la página de repartidor
- Agita **MUY fuerte** 3 veces seguidas

---

## 📊 Cómo Funciona la Detección

Para que se active una alerta de pánico por agitación:

1. Necesitas agitar el teléfono **3 veces**
2. Las 3 agitaciones deben ocurrir en **menos de 0.5 segundos** (medio segundo)
3. Después de enviar una alerta, hay un **cooldown de 5 segundos** (no se pueden enviar alertas seguidas)
4. La alerta se envía **automáticamente** con tu ubicación GPS

---

## ✅ Checklist Final

Antes de confiar en la detección de agitación, verifica:

- [ ] Detección de agitación **activada** en Mi Perfil
- [ ] Sensibilidad configurada (recomendado: **15**)
- [ ] **iPhone:** Sensores de Movimiento activados en Ajustes de Safari
- [ ] **iPhone:** Botón "Activar Sensores" presionado y permiso concedido
- [ ] GPS funcionando (probado en test-sensores)
- [ ] Al agitar 3 veces fuerte, aparece notificación roja
- [ ] Contactos de emergencia configurados con Telegram y Email

---

## 💡 Consejos de Uso

### **Cuándo Usar la Agitación:**
- Situaciones donde **no puedes tocar el botón SOS**
- Necesitas activar una alerta **discretamente**
- Estás siendo asaltado y no puedes sacar el teléfono

### **Cómo Agitar Correctamente:**
- **Fuerte y rápido**: Como si sacudieras el agua del teléfono
- **3 veces seguidas**: Arriba-abajo-arriba (muy rápido)
- **No necesita estar desbloqueado**: Funciona con pantalla apagada (en algunos navegadores)

### **Importante:**
- Practica primero en un lugar seguro
- No agites accidentalmente durante el día normal
- Configura la sensibilidad según tu estilo de vida (delivery en moto = sensibilidad baja)

---

## 🆘 Última Opción

Si nada funciona:

1. **Reinicia el teléfono**
2. Vuelve a abrir `http://192.168.0.93:8001/repartidor/`
3. **iPhone:** Activa los sensores de nuevo
4. Prueba en la página de test primero

Si aún no funciona, es posible que tu teléfono/navegador no soporte DeviceMotion API. En ese caso, usa solo el **botón SOS** para emergencias.

---

**🎉 ¡Una vez configurado, los sensores quedarán activos mientras tengas la pestaña abierta!**
