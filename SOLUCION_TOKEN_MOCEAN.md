# Solucion: Token de Mocean no se actualizaba

## Problema Identificado

El sistema estaba usando un token antiguo (`apit-6zTN9LakOaiSRGbuVLYFcOu63...`) en lugar del nuevo token configurado en el archivo `.env`.

**Causa**: Django estaba cargando variables de entorno del sistema Windows que tenian prioridad sobre el archivo `.env`.

## Solucion Aplicada

Se modifico el archivo `mysite/settings.py` para usar `override=True` al cargar el `.env`:

```python
# ANTES
load_dotenv(BASE_DIR / '.env')

# AHORA
load_dotenv(BASE_DIR / '.env', override=True)
```

Esto garantiza que el token del archivo `.env` tenga prioridad sobre cualquier variable de entorno del sistema.

## Token Actual Configurado

```
MOCEAN_API_TOKEN=apit-qOrNRlPrykyAGoH0h9TSwUK6RSUiXoKb-21OHb
```

Longitud: 43 caracteres
Ubicacion: `.env` (linea 2)

## Pasos para Aplicar los Cambios

### 1. Reiniciar el Servidor Django

**IMPORTANTE**: Debes reiniciar el servidor Django para que cargue el nuevo token:

```bash
# Si el servidor esta corriendo:
# 1. Presiona Ctrl+C en la terminal donde corre el servidor
# 2. Vuelve a iniciarlo:
python manage.py runserver

# O si usas ngrok:
python manage.py runserver 0.0.0.0:8000
```

### 2. Verificar que el Token se Cargo Correctamente

Ejecuta el script de prueba:

```bash
python test_sms_mocean.py
```

Deberia mostrar:
```
[OK] Token configurado: apit-qOrNRlPrykyAGoH0h9TSwUK6R...
     Longitud: 43 caracteres
```

### 3. Probar Envio de SMS Real (Opcional)

Si quieres probar que el SMS llegue a tu telefono:

```bash
python test_sms_mocean.py
```

Cuando pregunte "Deseas probar el envio de un SMS real? (s/n):", responde `s` y proporciona tu numero con codigo de pais (ejemplo: +521234567890).

## Verificacion en Produccion

Para verificar que los SMS se envien correctamente cuando se activa una alerta:

1. **Asegurate de tener contactos de emergencia registrados**:
   - Los contactos deben estar en la base de datos
   - Deben tener `validado=True`
   - Los numeros deben tener formato internacional (+521234567890)

2. **Activa una alerta desde la app movil**:
   - Inicia sesion como repartidor
   - Presiona el boton de panico o accidente
   - Revisa la consola del servidor Django para ver los logs

3. **Logs que deberias ver**:
   ```
   📱 Enviando SMS REAL via MOCEAN a +521234567890
      Mensaje: ALERTA DE PANICO - RAPPI SAFE...
   ✅ SMS enviado exitosamente!
      Message ID: xxxxx
      Receptor: 521234567890
   ```

## Archivos Modificados

1. `mysite/settings.py` (linea 22): Agregado `override=True` a `load_dotenv()`
2. `test_sms_mocean.py` (linea 13): Agregado `override=True` a `load_dotenv()`

## Verificacion del Saldo de Mocean

Recuerda que Mocean cobra por cada SMS enviado. Verifica tu saldo en:
https://dashboard.moceanapi.com/

## Notas Adicionales

- **Token anterior**: `apit-6zTN9LakOaiSRGbuVLYFcOu63CYbXgyU-DhxCS` (sin creditos)
- **Token nuevo**: `apit-qOrNRlPrykyAGoH0h9TSwUK6RSUiXoKb-21OHb` (activo)

Si en el futuro cambias de token nuevamente, solo actualiza el valor en `.env` y reinicia el servidor Django. El sistema ahora siempre usara el token del `.env` independientemente de las variables de entorno del sistema.
