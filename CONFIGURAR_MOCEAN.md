# Configuración de Mocean API para SMS Reales

## ¿Qué es Mocean?

Mocean es un proveedor de servicios de SMS con cobertura internacional, incluyendo México y Latinoamérica. Es una alternativa confiable y económica para enviar SMS de emergencia.

## Pasos para Configurar Mocean API

### 1. Crear Cuenta en Mocean

1. Ve a [https://dashboard.moceanapi.com/register](https://dashboard.moceanapi.com/register)
2. Regístrate con tu email
3. Verifica tu cuenta

### 2. Obtener Token de API

1. Inicia sesión en [https://dashboard.moceanapi.com](https://dashboard.moceanapi.com)
2. Ve a la sección "API Credentials" o "Settings"
3. Copia tu **API Token** (es un token único que incluye key + secret)

### 3. Instalar SDK de Mocean

El sistema usa el SDK oficial de Mocean. Instálalo con:

```bash
pip install moceansdk
```

### 4. Configurar Variable de Entorno

#### En Windows (Desarrollo):

1. Abre PowerShell como Administrador
2. Ejecuta este comando (reemplaza con tu token real):

```powershell
[System.Environment]::SetEnvironmentVariable('MOCEAN_API_TOKEN', 'tu_token_aqui', 'User')
```

3. Reinicia tu terminal o IDE para que cargue la variable

#### Verificar Variable (PowerShell):

```powershell
$env:MOCEAN_API_TOKEN
```

#### En Producción (Linux/Servidor):

1. Edita el archivo de entorno:
```bash
nano ~/.bashrc
```

2. Agrega al final:
```bash
export MOCEAN_API_TOKEN="tu_token_aqui"
```

3. Recarga:
```bash
source ~/.bashrc
```

### 5. Verificar Configuración

Ejecuta este script de prueba:

```python
import os

api_token = os.environ.get('MOCEAN_API_TOKEN')

if api_token:
    print("✅ Token de Mocean configurado correctamente")
    print(f"   Token: {api_token[:15]}...")
else:
    print("❌ MOCEAN_API_TOKEN NO configurado")
```

### 6. Probar Envío de SMS

Una vez configurado el token, las alertas de pánico automáticamente enviarán SMS reales a los contactos de emergencia.

## Formato de Números de Teléfono

Los números deben estar en formato internacional:
- **Correcto**: `+521234567890` (México)
- **Correcto**: `+5491112345678` (Argentina)
- **Incorrecto**: `1234567890` (sin código de país)

## Costos

Mocean cobra por SMS enviado. Los precios varían por país:
- México: ~$0.05 USD por SMS
- Revisa los precios actuales en: [https://www.moceanapi.com/pricing](https://www.moceanapi.com/pricing)

## Créditos de Prueba

Mocean suele ofrecer créditos de prueba gratuitos al registrarte. Úsalos para:
1. Probar el sistema
2. Validar que los SMS lleguen correctamente
3. Verificar el formato de los mensajes

## Solución de Problemas

### Error: "No hay token de MoceanAPI configurado"

- Verifica que la variable MOCEAN_API_TOKEN esté configurada
- Reinicia el servidor de Django después de configurarla
- En Windows, reinicia tu terminal/PowerShell

### Error: "SDK de Mocean no instalado"

- Instala el SDK con: `pip install moceansdk`
- Asegúrate de estar en el entorno virtual correcto

### Error: "Mocean rechazó el SMS"

- Verifica que el número esté en formato internacional (+52...)
- Asegúrate de tener créditos en tu cuenta Mocean
- Revisa que el número de destino sea válido

### SMS no llegan

- Verifica el estado en el Dashboard de Mocean
- Revisa los logs del servidor Django para ver el message_id
- Contacta al soporte de Mocean si persiste el problema

## Alternativas de Desarrollo

Si no quieres usar Mocean durante desarrollo, el sistema automáticamente usará:
1. **Telegram** (si está configurado para el contacto)
2. **Email** (si está configurado)
3. **Simulado** (solo logs, sin envío real)

Pero para **PRODUCCIÓN**, se recomienda siempre tener Mocean configurado para SMS reales.

## Soporte

- Documentación oficial: [https://docs.moceanapi.com](https://docs.moceanapi.com)
- Soporte Mocean: [support@moceanapi.com](mailto:support@moceanapi.com)
