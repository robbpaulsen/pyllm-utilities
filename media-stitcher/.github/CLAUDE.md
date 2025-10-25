# CLAUDE.md - Media-Stitcher Project Context

## 📋 Propósito del Proyecto

**Media-Stitcher** es un wrapper de FFmpeg diseñado para eliminar dependencias de servicios externos en el flujo de post-producción de videos para YouTube.

### Problema que Resuelve
Eliminar la dependencia de contenedores o servicios de terceros para tareas esenciales de manipulación multimedia (unir, cortar, incrustar audio, ajustar velocidad), asegurando la **continuidad operativa** del pipeline de creación de contenido.

### Objetivo Principal
Ofrecer una interfaz programática Python sencilla y fiable para ejecutar las operaciones más comunes de post-producción de video y audio usando comandos FFmpeg internos.

---

## 🎯 La Regla de Oro Antidistracción

**Esta es la regla SUPREMA del proyecto. Cualquier funcionalidad que no pase este filtro debe ser rechazada o pospuesta.**

> **"Cualquier nueva funcionalidad debe ser una manipulación directa de archivos multimedia (video/audio) que pueda ser resuelta mediante la ejecución de uno o más comandos de FFmpeg, priorizando las operaciones necesarias para ensamblar un video de YouTube."**

**Ejemplos de lo que SÍ cumple la regla:**
- ✅ Unir múltiples videos en secuencia
- ✅ Incrustar audio a un video
- ✅ Ajustar velocidad de reproducción de audio
- ✅ Recortar segmentos de video/audio
- ✅ Convertir formatos multimedia

**Ejemplos de lo que NO cumple la regla:**
- ❌ Generar thumbnails con IA
- ❌ Transcripción automática de audio
- ❌ Gestión de metadatos de YouTube
- ❌ Análisis de engagement de videos
- ❌ Compresión inteligente basada en contenido

---

## 🏗️ Decisiones de Arquitectura

### Estructura del Proyecto
```
media-stitcher/
├── media_stitcher/          # Paquete principal
│   ├── __init__.py          # Exporta funciones públicas
│   ├── core.py              # Funciones principales (unir, integrar, ajustar)
│   └── utils.py             # Validaciones, helpers, verificación FFmpeg
├── video-samples/           # Archivos de prueba (no versionados)
├── main.py                  # Script de ejemplo de uso
├── CLAUDE.md                # Este archivo
├── MainDraft-Idea.md        # Boceto original de la idea
├── README.md                # Documentación de usuario
└── pyproject.toml           # Configuración del proyecto (uv)
```

### Filosofía de Implementación
1. **Simplicidad sobre abstracción**: FFmpeg ya es la abstracción. No crear capas innecesarias.
2. **Happy path primero**: Funcionalidad que funcione para casos comunes antes que manejo exhaustivo de edge cases.
3. **Validaciones esenciales**: Verificar existencia de archivos y FFmpeg en PATH. No validar cada parámetro posible.
4. **Logging básico**: Usar módulo `logging` estándar. INFO para operaciones, ERROR para fallos.
5. **Subprocess directo**: Llamar FFmpeg vía `subprocess.run()` sin wrappers externos.

### Dependencias
- **Python**: >=3.11 (según pyproject.toml)
- **FFmpeg**: Debe estar disponible en PATH del sistema
- **GPU**: Setup con NVIDIA 12GB VRAM disponible (aceleración opcional para futuro)

### Estrategia de Aceleración GPU (Futuro)
- Implementación actual usa CPU (compatibilidad universal)
- NVIDIA nvenc/cuvid disponible para encoding/decoding acelerado
- Parámetros FFmpeg para GPU: `-hwaccel cuda -hwaccel_output_format cuda`
- Dejar como TODO para fase de optimización

---

## 🚀 Funcionalidades Core (MVP)

### 1. `unir_archivos(lista_paths, output_path)` ⭐ PRIORIDAD MÁXIMA
**Propósito**: Concatenar múltiples archivos de video/audio en secuencia.

**Caso de uso**: Unir intro + cuerpo + outro del video de YouTube.

**Método FFmpeg**:
- Opción 1 (concat demuxer): Más rápido, sin re-encoding
- Opción 2 (concat filter): Compatible con diferentes formatos

### 2. `integrar_audio_a_video(video_path, audio_path, output_path)`
**Propósito**: Incrustar audio TTS generado en un video o imagen estática de fondo.

**Caso de uso**: Agregar narración a video de background loops o imagen estática.

**Método FFmpeg**: `-i video -i audio -c:v copy -c:a aac -map 0:v:0 -map 1:a:0`

### 3. `ajustar_velocidad_audio(audio_path, factor_velocidad, output_path)`
**Propósito**: Cambiar velocidad de reproducción sin alterar el pitch (tono).

**Caso de uso**: Acelerar/desacelerar guiones largos para ajustar duración total del video.

**Método FFmpeg**: Filtro `atempo` (rango: 0.5 - 2.0, encadenable para rangos mayores)

---

## 📝 TODOs y Roadmap

### Fase Actual: MVP Funcional ✅
- [x] Crear estructura del proyecto
- [x] Implementar `utils.py` con validaciones básicas
- [x] Implementar `unir_archivos()`
- [x] Implementar `integrar_audio_a_video()`
- [x] Implementar `ajustar_velocidad_audio()`
- [x] README.md con ejemplos de uso
- [x] Script de ejemplo `main.py`

### Fase 2: GPU, Progreso y Tests ✅
- [x] Implementar detección GPU NVIDIA (nvenc, cuvid, CUDA)
- [x] Agregar parámetro `use_gpu` a funciones core
- [x] Implementar parsing de progreso FFmpeg con tqdm
- [x] Agregar parámetro `show_progress` a funciones core
- [x] Gestión de archivos temporales (GestorTemporales context manager)
- [x] Tests unitarios con pytest (tests/test_core.py)
- [x] Agregar tqdm como dependencia
- [x] Actualizar documentación (README.md, CLAUDE.md)

### Fase 3: Herramientas Avanzadas ✅
- [x] Función `recortar_segmento()` para extraer clips
- [x] CLI completa con argparse y subcomandos
- [x] Logging a archivo configurable
- [x] Soporte codecs GPU adicionales (HEVC, VP9)
- [x] Comando `media-stitcher info` para verificar sistema
- [x] Entry point en pyproject.toml

### Fase 4: Optimización Futura (Próxima Sesión)
- [ ] Validación de formatos de entrada (extensiones soportadas)
- [ ] Parámetros avanzados (bitrate, resolución, codec customizables)
- [ ] Métricas de rendimiento (tiempo de procesamiento)
- [ ] Tests comprehensivos para CLI

### Fase 5: Sincronización Audio-Video (Consideración Futura)
- [ ] Detectar duración de audio/video
- [ ] Ajustar velocidad automáticamente para match de duración
- [ ] Fade in/out de audio
- [ ] Normalización de volumen

---

## 🔧 Comandos de Desarrollo

```bash
# Activar entorno virtual (Windows PowerShell)
.venv/Scripts/activate.ps1

# Activar entorno virtual (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -e .

# Instalar dependencias de desarrollo (incluye pytest)
pip install -e ".[dev]"

# Verificar FFmpeg instalado
ffmpeg -version

# Verificar GPU NVIDIA disponible
ffmpeg -encoders | grep nvenc
ffmpeg -hwaccels | grep cuda

# Ejecutar ejemplo básico
python main.py

# Ejecutar tests
pytest
pytest -v  # verbose
pytest tests/test_core.py::test_unir_archivos_basico  # test específico

# Usar CLI
media-stitcher --help
media-stitcher info
media-stitcher unir video1.mp4 video2.mp4 -o output.mp4 -g -p
media-stitcher recortar video.mp4 10 30 -o clip.mp4

# Limpiar archivos de output
rm video-samples/output_*
rm video-samples/TEST_*
rm video-samples/test_outputs/*
```

---

## 📚 Referencias Útiles

- [FFmpeg Documentation](https://ffmpeg.org/ffmpeg.html)
- [FFmpeg concat demuxer](https://ffmpeg.org/ffmpeg-formats.html#concat)
- [FFmpeg atempo filter](https://ffmpeg.org/ffmpeg-filters.html#atempo)
- [NVIDIA GPU acceleration](https://docs.nvidia.com/video-technologies/video-codec-sdk/ffmpeg-with-nvidia-gpu/)

---

## 🤝 Convenciones de Código

- **Naming**: snake_case para funciones y variables
- **Docstrings**: Formato Google style
- **Type hints**: Usar cuando mejore claridad (no obligatorio en MVP)
- **Error handling**: Try/except en llamadas FFmpeg + logging
- **Returns**: Devolver `True` en éxito, `False` en fallo (o lanzar excepción según contexto)

---

**Última actualización**: 2025-10-23
**Versión del proyecto**: 0.3.0

---

## 📊 Changelog

### v0.3.0 (2025-10-23) - Fase 3 Completada
**Nuevas funcionalidades:**
- ✅ CLI completa con argparse (5 comandos: unir, integrar, ajustar, recortar, info)
- ✅ Función `recortar_segmento()` para extraer clips por tiempo
- ✅ Logging a archivo configurable
- ✅ Detección de codecs GPU adicionales (HEVC, VP9)

**Cambios en API:**
- Agregada función: `recortar_segmento(input, start, end, output, stream_copy, use_gpu, show_progress)`
- Agregada función: `configurar_logging(level, log_file, format_string)` en utils
- Extendida: `detectar_gpu_nvidia()` ahora detecta hevc_nvenc y vp9_nvenc
- Entry point CLI: `media-stitcher` comando disponible

**CLI:**
- `media-stitcher unir` - Concatenar videos
- `media-stitcher integrar` - Agregar audio a video
- `media-stitcher ajustar` - Cambiar velocidad de audio
- `media-stitcher recortar` - Extraer segmentos
- `media-stitcher info` - Ver capacidades del sistema

**Opciones globales CLI:**
- `--log-file FILE` - Guardar logs en archivo
- `-v, --verbose` - Modo debug
- `-g, --gpu` - Aceleración GPU
- `-p, --progress` - Barra de progreso

### v0.2.0 (2025-10-23) - Fase 2 Completada
**Nuevas funcionalidades:**
- ✅ Aceleración GPU NVIDIA (nvenc, cuvid, CUDA)
- ✅ Progress bars con tqdm
- ✅ Gestión automática de archivos temporales
- ✅ Tests unitarios con pytest

**Cambios en API:**
- Agregado `use_gpu` parameter a `unir_archivos()` y `integrar_audio_a_video()`
- Agregado `show_progress` parameter a todas las funciones core
- Nueva función: `detectar_gpu_nvidia()` en utils
- Nueva función: `ejecutar_ffmpeg_con_progreso()` en utils
- Nuevo context manager: `GestorTemporales()` en utils

**Dependencias:**
- Agregado: `tqdm>=4.66.0`
- Agregado (dev): `pytest>=7.4.0`

### v0.1.0 (2025-10-23) - MVP Inicial
- ✅ Implementación inicial de 3 funciones core
- ✅ Sistema de validaciones y logging
- ✅ Documentación básica
