# 📱 Guía Rápida: Configurar SMS con Twilio

## ✅ Lo que Ya Está Hecho

- ✅ Twilio instalado
- ✅ Credenciales configuradas en `.env`
- ✅ Código listo para enviar SMS reales

---

## ⚠️ Problemas Comunes y Soluciones

### Error 21608: "The number is unverified"

**Causa:** Tu cuenta Trial de Twilio solo puede enviar SMS a números verificados.

**Solución:**

1. Ve a: https://console.twilio.com/us1/develop/phone-numbers/manage/verified
2. Haz clic en **"+ Verify a new number"**
3. Ingresa tu número con código de país: `+5219515551234`
4. Twilio te enviará un código por SMS o llamada
5. Ingresa el código para verificar

Debes hacer esto para **CADA número** que quiera recibir SMS.

---

### Error 21408: "Permission to send an SMS has not been enabled"

**Causa:** Tu cuenta de Twilio no tiene habilitada la región de México.

**Solución:**

1. Ve a: https://console.twilio.com/us1/develop/sms/settings/geo-permissions
2. Busca **"Mexico"** en la lista de países
3. **Activa** el checkbox ✅
4. Haz clic en **"Save"**

---

### Error: Formato de Número Incorrecto

**Números CORRECTOS:**
```
✅ +5219515551234  (México, celular)
✅ +5215512345678  (México DF, celular)
✅ +14155551234    (USA)
```

**Números INCORRECTOS:**
```
❌ 9515551234       (falta código de país)
❌ 5219515551234    (falta el símbolo +)
❌ +52 951 555 1234 (no usar espacios)
```

**Formato correcto para México:**
- Símbolo `+`
- Código de país: `52`
- Celular: `1` + 10 dígitos
- Ejemplo completo: `+5219515551234`

---

## 🚀 Pasos para Probar SMS Reales

### 1. Verifica tus Números en Twilio

- Ve a: https://console.twilio.com/us1/develop/phone-numbers/manage/verified
- Verifica TODOS los números que quieres que reciban SMS

### 2. Habilita la Región

- Ve a: https://console.twilio.com/us1/develop/sms/settings/geo-permissions
- Activa **Mexico** ✅

### 3. Agrega Contactos con Formato Correcto

- Ve a **"Mi Perfil"** en RappiSafe
- Haz clic en **"+ Agregar Contacto"**
- Ingresa el número con formato: `+5219515551234`
- El sistema validará el formato automáticamente

### 4. Prueba la Alerta

- Ve al Dashboard del repartidor
- Mantén presionado el botón **SOS rojo** por 3 segundos
- ¡El SMS debería llegar en segundos! 📱

---

## 💰 Cuenta Trial vs Cuenta de Pago

### **Cuenta Trial (GRATIS - $15 USD)**

✅ Puedes probar el sistema
✅ Enviar SMS a números verificados
❌ No puedes enviar a números sin verificar
❌ Los SMS incluyen un prefijo de Twilio

### **Cuenta de Pago (desde $20 USD)**

✅ Enviar a cualquier número (sin verificar)
✅ SMS sin prefijo de Twilio
✅ Sin restricciones
💰 ~$0.045 USD por SMS en México

**Para actualizar:**
https://console.twilio.com/billing/upgrade

---

## 🔍 Verificar que Funciona

En la **consola del servidor** verás:

```
📱 Enviando SMS REAL via Twilio a +5219515551234
   Mensaje: 🚨 ALERTA DE PÁNICO - RAPPI SAFE...
✅ SMS enviado exitosamente! SID: SMxxxxxxxxxxxxx
```

También puedes ver el status en:
https://console.twilio.com/us1/monitor/logs/sms

---

## 📞 Soporte

- **Documentación Twilio:** https://www.twilio.com/docs/sms
- **Errores comunes:** https://www.twilio.com/docs/api/errors
- **Geo-permissions:** https://www.twilio.com/docs/usage/tutorials/how-to-use-geo-permissions-sms

---

## ✅ Checklist Rápido

Antes de probar, verifica que:

- [ ] Números verificados en Twilio
- [ ] Región de México habilitada
- [ ] Números con formato correcto (+52...)
- [ ] Servidor Django reiniciado
- [ ] Contactos marcados como "Validados"

**¡Listo para enviar SMS reales!** 🚀
