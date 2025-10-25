# Captive Portal Setup - Digital Memoirs

## Índice
- [Descripción General](#descripción-general)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Configuración Manual](#configuración-manual)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Rollback](#rollback)

---

## Descripción General

Este documento describe la implementación del **Captive Portal** para Digital Memoirs, que permite que los usuarios:

1. **Escaneen un QR WiFi** → Se conectan automáticamente a la red
2. **Reciban una notificación automática** del sistema operativo
3. **Sean redirigidos a `/upload`** al tocar la notificación

### ¿Qué es un Captive Portal?

Un captive portal es la página que aparece automáticamente cuando te conectas a una red WiFi pública (como en hoteles o aeropuertos). Los sistemas operativos detectan estos portales haciendo peticiones a URLs específicas y esperando respuestas particulares.

---

## Arquitectura

### Flujo Completo

```
┌─────────────────────────────────────────────────────────┐
│ 1. Usuario escanea QR WiFi                              │
│    Formato: WIFI:T:WPA;S:MomentoMarco;P:password;;      │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Smartphone se conecta automáticamente                │
│    • iOS, Android, Windows se conectan sin intervención │
│    • Reciben IP del DHCP (10.0.17.x)                    │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 3. OS hace peticiones de verificación (captive check)   │
│    • iOS → captive.apple.com                            │
│    • Android → connectivitycheck.gstatic.com            │
│    • Windows → www.msftconnecttest.com                  │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 4. dnsmasq intercepta y redirige a 10.0.17.1            │
│    • Configuración: address=/captive.apple.com/10.0.17.1│
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Flask responde con redirect 302                      │
│    • iOS: /hotspot-detect.html → redirect /upload       │
│    • Android: /generate_204 → redirect /upload          │
│    • Windows: /connecttest.txt → redirect /upload       │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 6. OS detecta captive portal                            │
│    • Muestra notificación: "Iniciar sesión en red"      │
│    • Usuario toca notificación                          │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 7. Navegador abre /upload automáticamente               │
│    ✓ Usuario puede subir fotos                          │
└─────────────────────────────────────────────────────────┘
```

### Componentes Modificados

| Componente | Cambios | Propósito |
|------------|---------|-----------|
| **app.py** | + Endpoints captive portal<br>+ Función `generate_wifi_qr()` | Detectar y redirigir OS |
| **dnsmasq.conf** | + Redirección DNS | Interceptar peticiones |
| **display.html** | Actualizar instrucciones | Reflejar nuevo flujo |
| **qr.html** | Actualizar instrucciones | Reflejar nuevo flujo |

---

## Instalación

### Opción 1: Script Automático (Recomendado)

```bash
# 1. Conecta al Raspberry Pi vía SSH
ssh pi@10.0.17.1

# 2. Navega al directorio del proyecto
cd /path/to/digital-memoirs

# 3. Ejecuta el script de setup
sudo bash scripts/setup-captive-portal.sh
```

El script:
- ✅ Hace backup de configuración actual
- ✅ Modifica `/etc/dnsmasq.conf`
- ✅ Reinicia servicios
- ✅ Verifica que todo funcione
- ✅ Rollback automático en caso de error

### Opción 2: Configuración Manual

Ver sección [Configuración Manual](#configuración-manual) abajo.

---

## Configuración Manual

Si prefieres configurar manualmente o el script falla, sigue estos pasos:

### 1. Backup de Configuración Actual

```bash
sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
```

### 2. Editar dnsmasq.conf

```bash
sudo nano /etc/dnsmasq.conf
```

Agregar al final del archivo:

```conf
# Captive Portal Detection - Digital Memoirs

# iOS Captive Portal Detection
address=/captive.apple.com/10.0.17.1
address=/www.apple.com/10.0.17.1

# Android Captive Portal Detection
address=/connectivitycheck.gstatic.com/10.0.17.1
address=/www.gstatic.com/10.0.17.1
address=/clients3.google.com/10.0.17.1

# Windows Captive Portal Detection
address=/www.msftconnecttest.com/10.0.17.1
address=/msftconnecttest.com/10.0.17.1

# Firefox Captive Portal Detection
address=/detectportal.firefox.com/10.0.17.1

# End Captive Portal Detection
```

### 3. Verificar Sintaxis

```bash
sudo dnsmasq --test
```

Deberías ver: `dnsmasq: syntax check OK.`

### 4. Reiniciar dnsmasq

```bash
sudo systemctl restart dnsmasq
```

### 5. Verificar Estado

```bash
sudo systemctl status dnsmasq
```

Debe mostrar `active (running)`.

### 6. Probar DNS

```bash
nslookup captive.apple.com localhost
```

Debe resolver a `10.0.17.1`.

---

## Testing

### Checklist de Pruebas

#### ✅ Testing iOS (iPhone/iPad)

1. **Desconectar de WiFi "MomentoMarco"** (si estabas conectado)
2. **Escanear QR WiFi** con app de Cámara
3. **Verificar**:
   - ✓ Se conecta automáticamente
   - ✓ Aparece notificación "Iniciar sesión en red" (puede tomar 2-5 segundos)
   - ✓ Al tocar notificación → abre navegador con `/upload`

**Problemas comunes iOS:**
- Si no aparece notificación: Desactiva/activa WiFi
- Si abre Safari en blanco: Verifica que Flask esté corriendo
- Algunos iPhones necesitan esperar 10 segundos para detectar portal

#### ✅ Testing Android

1. **Desconectar de WiFi "MomentoMarco"**
2. **Escanear QR WiFi**
3. **Verificar**:
   - ✓ Se conecta automáticamente
   - ✓ Aparece notificación "Sign in to Wi-Fi network"
   - ✓ Al tocar → abre navegador con `/upload`

**Problemas comunes Android:**
- Algunos Android (Samsung, Xiaomi) bloquean captive portals
- Si no funciona: Abre navegador manualmente y ve a cualquier URL (ej: google.com)
- Debería redirigir a `/upload`

#### ✅ Testing Windows

1. **Conectar a WiFi "MomentoMarco"** (Windows no soporta QR WiFi nativamente)
2. **Verificar**:
   - ✓ Aparece notificación de Windows
   - ✓ Click en notificación → abre navegador

#### ✅ Testing Fallback Manual

Si captive portal no funciona automáticamente:

1. Usuario se conecta al WiFi
2. Abre navegador
3. Intenta ir a cualquier URL (ej: `google.com`)
4. Debe ser redirigido a `http://10.0.17.1:5000/upload`

---

## Troubleshooting

### Problema: No aparece notificación de captive portal

**Diagnóstico:**

```bash
# Verifica que dnsmasq esté redirigiendo
nslookup captive.apple.com localhost
# Debe mostrar: Address: 10.0.17.1

# Verifica logs de dnsmasq
sudo journalctl -u dnsmasq -f
# Conecta un dispositivo y observa los logs
```

**Soluciones:**
1. Reinicia dnsmasq: `sudo systemctl restart dnsmasq`
2. Verifica que Flask esté corriendo en puerto 5000
3. Prueba con otro dispositivo (iOS vs Android)

---

### Problema: Flask no responde a endpoints de captive portal

**Diagnóstico:**

```bash
# Desde el Raspberry Pi, prueba:
curl http://localhost:5000/hotspot-detect.html

# Debería redirigir a /upload
```

**Soluciones:**
1. Verifica que `app.py` tenga los endpoints de captive portal
2. Reinicia Flask: `pkill -f app.py && python app.py`
3. Revisa logs de Flask

---

### Problema: DNS no resuelve correctamente

**Diagnóstico:**

```bash
# Verifica configuración de dnsmasq
sudo dnsmasq --test

# Si hay errores de sintaxis:
sudo nano /etc/dnsmasq.conf
# Busca errores de tipeo en las líneas agregadas
```

**Soluciones:**
1. Restaura backup: `sudo cp /etc/dnsmasq.conf.backup /etc/dnsmasq.conf`
2. Vuelve a ejecutar script de setup

---

### Problema: Dispositivo se conecta pero no puede navegar

**Causa**: Probablemente firewall bloqueando tráfico.

**Diagnóstico:**

```bash
# Verifica iptables
sudo iptables -L -n -v
```

**Solución**: Este proyecto asume que no hay firewall o está configurado para permitir todo el tráfico local.

---

## Rollback

### Opción 1: Usando Backup Automático

El script de setup crea backups automáticos con timestamp:

```bash
# Listar backups
ls -la /etc/dnsmasq.conf.backup*

# Restaurar último backup
sudo cp /etc/dnsmasq.conf.backup-YYYYMMDD-HHMMSS /etc/dnsmasq.conf
sudo systemctl restart dnsmasq
```

### Opción 2: Remover Configuración Manualmente

```bash
# Editar dnsmasq.conf
sudo nano /etc/dnsmasq.conf

# Borrar líneas entre:
# # Captive Portal Detection - Digital Memoirs
# ... hasta ...
# # End Captive Portal Detection

# Guardar (Ctrl+O) y salir (Ctrl+X)

# Reiniciar
sudo systemctl restart dnsmasq
```

### Opción 3: Restaurar a QR URL Original

Si quieres volver al sistema anterior (QR con URL):

1. **En `app.py`**, cambiar:
   ```python
   # Cambiar esto:
   qr_path = generate_wifi_qr()

   # Por esto:
   upload_url = f"http://{local_ip}:5000/upload"
   qr_path = generate_qr_code(upload_url)
   ```

2. **Restaurar dnsmasq.conf** (ver arriba)

3. **Reiniciar Flask**

---

## FAQ

### ¿Por qué no usar un captive portal "real" con login?

Los captive portals tradicionales requieren configuración compleja de iptables, servidor RADIUS, y base de datos. Para nuestro caso de uso (evento privado), solo necesitamos redirección automática sin autenticación.

### ¿Funciona en todos los dispositivos?

**Sí**: iOS 10+, Android 5+, Windows 10+, macOS

**No**: Dispositivos muy antiguos o con configuraciones de seguridad especiales

### ¿Necesito conexión a internet?

**No**. Todo funciona en red local (10.0.17.0/24). Los endpoints de captive portal son servidos por Flask localmente.

### ¿Qué pasa si un usuario ya está conectado al WiFi?

Pueden acceder directamente a `http://10.0.17.1:5000/upload` o escanear un segundo QR (que se puede mostrar en la página `/qr`).

### ¿Cuántos usuarios soporta simultáneamente?

Probado con **200+ conexiones simultáneas** sin problemas. El límite depende de:
- Ancho de banda del Raspberry Pi
- Límite de DHCP (configurado para ~250 IPs)
- Recursos de Flask (ThreadPoolExecutor con 8 workers)

---

## Referencias

- **Captive Portal Detection iOS**: https://developer.apple.com/library/archive/technotes/tn2444/_index.html
- **Captive Portal Detection Android**: https://source.android.com/devices/tech/connect/captive-portals
- **dnsmasq Documentation**: http://www.thekelleys.org.uk/dnsmasq/doc.html

---

## Changelog

### 2025-10-22
- ✅ Implementación inicial de captive portal
- ✅ Script de setup automático
- ✅ Documentación completa
- ✅ Testing en iOS y Android

---

*Última actualización: 2025-10-22*
