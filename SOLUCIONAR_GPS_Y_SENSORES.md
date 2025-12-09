# 📱 Solucionar Problemas de GPS y Sensores en el Teléfono

## 🧪 PASO 1: Probar los Sensores

Primero, vamos a verificar que tu teléfono funcione correctamente.

En tu teléfono, ve a:

```
http://192.168.0.93:8001/test-sensores/
```

Esta página te permite probar:
- ✅ GPS / Ubicación
- ✅ Sensores de movimiento (para agitar)
- ℹ️ Información del dispositivo

---

## 📍 Problemas con GPS / Ubicación

### **Android (Chrome):**

1. **Cuando cargue la página**, debería aparecer un pop-up:
   > "¿Permitir que este sitio conozca tu ubicación?"

   → Toca **"Permitir"**

2. **Si NO apareció el pop-up:**
   - Toca el **candado** en la barra de direcciones
   - Busca **"Permisos" o "Ubicación"**
   - Cambia a **"Permitir"**
   - **Recarga la página** (arrastra hacia abajo para refrescar)

3. **Si dice "Permiso denegado":**
   - Ve a **Configuración de Android** → **Ubicación**
   - Activa **"Ubicación"** (GPS)
   - Ve a **Configuración de Chrome** → **Permisos del sitio** → **Ubicación**
   - Busca `192.168.0.93` y marca **"Permitir"**

### **iPhone (Safari):**

1. **Primera vez:**
   - Safari preguntará: "¿Permitir acceso a la ubicación?"
   - Toca **"Permitir"**

2. **Si NO preguntó:**
   - Ve a **Ajustes** de iPhone → **Safari**
   - Baja hasta **"Ubicación"**
   - Selecciona **"Permitir"** o **"Preguntar"**
   - **Recarga Safari**

3. **Si sigue sin funcionar:**
   - Ve a **Ajustes** → **Privacidad** → **Ubicación**
   - Verifica que **"Safari"** tenga permiso **"Siempre"** o **"Al usar la App"**

---

## 📲 Problemas con Detección de Agitación

### **Android (Chrome):**

✅ **Los sensores de movimiento funcionan automáticamente** en Android

Solo necesitas:
1. Ir a la página de test: `http://192.168.0.93:8001/test-sensores/`
2. Tocar el botón **"Activar Sensores"**
3. **Agitar el teléfono** para ver los valores cambiar

Si NO funciona:
- Verifica que el teléfono no esté en modo ahorro de energía
- Algunos navegadores alternativos pueden no soportarlo (usa Chrome)

### **iPhone (Safari):**

En iOS 13+, los sensores necesitan **permiso explícito**:

1. Ve a la página de test: `http://192.168.0.93:8001/test-sensores/`

2. Toca el botón **"Activar Sensores"**

3. Aparecerá un pop-up pidiendo permiso → Toca **"Permitir"**

4. **Si NO aparece el pop-up:**
   - Ve a **Ajustes** de iPhone → **Safari**
   - Baja hasta **"Sensores de Movimiento y Orientación"**
   - **Actívalo** ✅
   - **Recarga Safari**

---

## ✅ Cómo Usar la Página de Test

### **Test de GPS:**

1. Toca **"Probar GPS"**
2. Permite el acceso cuando lo pida
3. Deberías ver:
   ```
   ✅ GPS funcionando correctamente
   Latitud: 19.432608
   Longitud: -99.133209
   Precisión: 15 metros
   ```

Si ves **latitud y longitud**, el GPS funciona! ✅

### **Test de Sensores:**

1. Toca **"Activar Sensores"**
2. Permite el acceso cuando lo pida (solo en iPhone)
3. **Agita tu teléfono** fuertemente
4. Deberías ver los valores X, Y, Z cambiar rápidamente

Si los valores cambian al agitar, los sensores funcionan! ✅

---

## 🎯 Una Vez que Ambos Funcionen

Cuando GPS y sensores funcionen en la página de test, regresa a RappiSafe:

```
http://192.168.0.93:8001/repartidor/
```

Ahora:
- ✅ El mapa mostrará tu ubicación GPS real
- ✅ Puedes agitar el teléfono para activar alertas
- ✅ El botón SOS enviará tu ubicación precisa

---

## ⚠️ Consejos Importantes

### **Para GPS:**
- Activa **"Alta precisión"** en los ajustes de ubicación
- Asegúrate de tener señal GPS (estar cerca de una ventana ayuda)
- WiFi activado mejora la precisión (incluso sin estar conectado)

### **Para Sensores:**
- La agitación debe ser **fuerte** (como si sacudieras el teléfono para limpiar la pantalla)
- Necesitas agitar **3 veces** en menos de 0.5 segundos
- Hay un cooldown de 5 segundos entre alertas

### **General:**
- Usa **Chrome en Android** o **Safari en iPhone** (otros navegadores pueden tener problemas)
- Mantén el navegador abierto y activo (no en segundo plano)
- No uses modo incógnito (algunos permisos no se guardan)

---

## 🔧 Problemas Comunes

| Problema | Solución |
|----------|----------|
| "Permiso denegado" | Ve a configuración del navegador y permite ubicación |
| "Ubicación no disponible" | Activa GPS en ajustes del teléfono |
| "Timeout" | Señal GPS débil, sal al exterior o acércate a ventana |
| Sensores no detectan | Verifica permisos en Safari o actualiza Chrome |
| Valores no cambian al agitar | Agita más fuerte y rápido |

---

## 📊 Información Técnica (Opcional)

La página de test muestra:
- **Navegador:** Qué navegador estás usando
- **Sistema:** Android, iOS, etc.
- **Es móvil:** Si detecta que es un dispositivo móvil
- **DeviceMotion:** Si el API de sensores está disponible
- **Geolocation:** Si el API de GPS está disponible

Si dice "❌ No disponible" en alguno, ese navegador no soporta esa función.

---

## ✅ Checklist Final

Antes de volver a RappiSafe, verifica:

- [ ] En `http://192.168.0.93:8001/test-sensores/` el GPS funciona
- [ ] Los sensores de movimiento funcionan (valores cambian al agitar)
- [ ] Permisos de ubicación: **Permitir**
- [ ] Permisos de sensores: **Permitir** (solo iPhone)
- [ ] GPS del teléfono activado en ajustes
- [ ] Navegador: Chrome (Android) o Safari (iPhone)

**¡Una vez que todo funcione en el test, funcionará en RappiSafe!** 🚀

---

## 🆘 Última Opción

Si nada funciona, prueba:

1. **Reiniciar el navegador** (cerrar todas las pestañas y abrir de nuevo)
2. **Reiniciar el teléfono**
3. **Probar con otro navegador** (Chrome, Firefox, Safari)
4. **Actualizar el navegador** a la última versión

---

**💡 Una vez que funcione el test, todo funcionará en RappiSafe!**
