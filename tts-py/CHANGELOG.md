# Changelog

Todos los cambios notables a este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planificado
- Procesamiento de audio con Whisper/faster-whisper para mejorar muestras
- Modo batch para procesar múltiples guiones
- Soporte para Chatterbox Multilingual TTS (23 idiomas)
- Tests unitarios
- Modo interactivo

---

## [0.3.0] - 2025-10-20

### Agregado
- **📊 Barra de progreso visual** con tqdm durante generación
  - Indicador visual de progreso (0-100%)
  - Estimación de tiempo basada en longitud de texto
  - Tiempo real de generación mostrado al finalizar
- **💾 Cache de voces procesadas**
  - Sistema de cache automático para voces de referencia
  - Parámetro `--voice-name` para nombrar y reutilizar voces
  - Almacenamiento en `~/.cache/tts-py/voices/`
  - Hash SHA256 para identificación única de archivos
  - Validación de integridad del cache
  - Mejora significativa de rendimiento en usos repetidos

### Cambiado
- Función `generar_audio()` ahora acepta parámetro `voice_name`
- Mejor feedback visual durante el proceso de generación
- Mensajes más informativos sobre uso de cache

### Mejorado
- Experiencia de usuario con indicadores visuales claros
- Performance al reutilizar voces de referencia
- Feedback en tiempo real del progreso

### Ejemplos de Uso
```bash
# Con cache de voz nombrada
uv run main.py --text "Texto aquí" \
  --voice audio-samples/narrador.wav \
  --voice-name "narrador" \
  --output salida.wav

# Segunda vez es más rápida (usa cache)
uv run main.py --text "Otro texto" \
  --voice audio-samples/narrador.wav \
  --voice-name "narrador" \
  --output salida2.wav
```

---

## [0.2.0] - 2025-10-20

### Agregado
- **MVP Funcional Completo** de TTS-py
- `main.py` completamente implementado con CLI robusta
- Integración con Chatterbox TTS (ResembleAi)
- Soporte para clonación de voz mediante audio de referencia
- Procesamiento de guiones desde archivos de texto
- Detección automática de GPU NVIDIA para aceleración
- Opción `--cpu` para forzar procesamiento en CPU
- Manejo robusto de errores con mensajes informativos
- Documentación completa en docstrings (español)
- Script de prueba `test_chatterbox.py` para validación

### Agregado - Dependencias
- `chatterbox-tts==0.1.3` - Modelo principal de síntesis de voz
- `torch==2.6.0+cu124` - Framework de deep learning con soporte CUDA
- `torchaudio==2.6.0` - Procesamiento de audio
- `transformers==4.46.3` - Modelos de HuggingFace
- `librosa==0.11.0` - Análisis de audio
- `soundfile==0.13.1` - I/O de archivos de audio
- `onnx==1.19.1` - Runtime de modelos optimizados
- Y 60+ dependencias transitivas necesarias

### Cambiado
- Migración completa de entorno Windows a Linux
- Recreación de venv para compatibilidad completa con Linux
- Uso de `uv run` como workflow principal (en lugar de activación manual)

### Decisiones Técnicas
- **Workflow:** `uv run` para evitar problemas de activación de venv
- **GPU:** RTX 3060 12GB detectada y configurada correctamente
- **CUDA:** 12.4 con PyTorch 2.6.0
- **CLI:** argparse con grupos mutuamente excluyentes para UX clara

### Estructura del Proyecto
```
tts-py/
├── main.py                  # ✅ MVP funcional completo
├── test_chatterbox.py       # ✅ Script de validación
├── creative-scripts/        # ✅ Input: guiones
├── audio-samples/           # ✅ Input: voces de referencia
└── output-dir/             # ✅ Output: audio generado
```

### Ejemplos de Uso
```bash
# Texto simple
uv run main.py --text "Hola mundo" --output salida.wav

# Guion desde archivo
uv run main.py --script creative-scripts/mi_guion.txt --output salida.wav

# Clonación de voz
uv run main.py --text "Texto" --voice audio-samples/mi_voz.wav --output salida.wav

# Combinado
uv run main.py --script guion.txt --voice voz.wav --output salida.wav
```

### Fixes Críticos Implementados
#### Problema de Red IPv6 en WSL2
- **Síntoma:** Error 500 al descargar modelo de HuggingFace
- **Causa:** IPv6 roto en WSL2, conexiones fallando con 100% packet loss
- **Solución:** Deshabilitar IPv6 con `sysctl -w net.ipv6.conf.all.disable_ipv6=1`
- **Resultado:** Conexiones funcionan perfectamente con IPv4

#### XET CAS Server Error
- **Síntoma:** `RuntimeError: Data processing error: CAS service error : HTTP 500`
- **Causa:** Servicio XET de HuggingFace intermitente/inestable
- **Solución:** Variable de entorno `HF_HUB_DISABLE_XET=1` para bypass XET
- **Resultado:** Modelo descarga correctamente (3GB) sin usar XET

#### Perth Watermarker TypeError
- **Síntoma:** `TypeError: 'NoneType' object is not callable` en PerthImplicitWatermarker
- **Causa:** Perth requiere compilación nativa que falla en WSL2
- **Solución:** Patch usando `DummyWatermarker` en su lugar
- **Resultado:** Generación funciona, solo pierde marca de agua invisible
- **Impacto:** Ninguno en calidad de audio

### Archivos Generados de Prueba
- `output-dir/test_simple.wav` (0.45 MB) - Test básico
- `output-dir/demo.wav` (0.56 MB) - Demo con texto CLI
- `output-dir/ejemplo_completo.wav` (2.65 MB) - Guion completo

### Notas de Desarrollo
- **Fase 1** del TODO.md completada exitosamente
- Proyecto 100% funcional end-to-end
- Modelo Chatterbox (3GB) descargado y en caché
- GPU NVIDIA RTX 3060 12GB funcionando perfectamente
- Código completamente documentado siguiendo estándares del proyecto
- Workflow con `uv run` establecido como estándar

---

## [0.1.0] - 2025-10-19

### Agregado
- Inicialización del proyecto con `uv`
- Estructura básica del proyecto
- `main.py` con punto de entrada básico
- `pyproject.toml` con metadatos del proyecto
- `README.md` con descripción general
- `project-description.md` con idea core del proyecto
- `CLAUDE.md` con contexto completo para desarrollo asistido
- `TODO.md` con roadmap detallado en 5 fases
- Este `CHANGELOG.md` para registro de cambios

### Decisiones Técnicas
- **Gestor de paquetes:** uv (moderno, rápido, compatible con pip)
- **Python requerido:** >=3.11 (para mejor soporte de type hints y performance)
- **Filosofía:** "Hecho es Mejor que Perfecto"
- **Idioma del código:** Español (variables, funciones, comentarios, docstrings)

### Notas de Desarrollo
- Proyecto creado desde cero
- Estructura de directorios definida en README.md y CLAUDE.md
- Roadmap completo dividido en 5 fases en TODO.md
- Enfoque en CLI primero, UI futura

---

## Tipos de Cambios
- **Agregado** - Para nuevas funcionalidades
- **Cambiado** - Para cambios en funcionalidades existentes
- **Deprecado** - Para funcionalidades que se eliminarán pronto
- **Eliminado** - Para funcionalidades eliminadas
- **Corregido** - Para corrección de bugs
- **Seguridad** - En caso de vulnerabilidades

---

## Guía para Mantener este Changelog

### Al agregar features:
```markdown
### Agregado
- Descripción clara de la feature
- Si agrega dependencias nuevas, mencionarlas
```

### Al corregir bugs:
```markdown
### Corregido
- Descripción del bug corregido (referencia a issue si existe)
```

### Al agregar dependencias importantes:
```markdown
### Agregado - Dependencias
- `nombre-paquete==version` - Para qué se usa
```

### Al hacer breaking changes:
```markdown
### Cambiado - BREAKING CHANGE
- Descripción del cambio incompatible
- Cómo migrar código existente
```

---

**Formato de Versiones:** MAJOR.MINOR.PATCH
- **MAJOR:** Cambios incompatibles de API
- **MINOR:** Nueva funcionalidad compatible con versiones anteriores
- **PATCH:** Correcciones de bugs compatibles con versiones anteriores

---

_Última actualización: 2025-10-19_
