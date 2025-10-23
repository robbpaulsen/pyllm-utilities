# Media-Stitcher

**Wrapper de FFmpeg para post-producción de videos de YouTube con soporte GPU**

Media-Stitcher es una utilidad Python que proporciona una interfaz simple y confiable para las operaciones más comunes de manipulación multimedia usando FFmpeg, con aceleración GPU NVIDIA opcional.

## 🎯 Propósito

Eliminar dependencias de servicios externos para tareas esenciales de post-producción:
- **Unir** múltiples segmentos de video/audio (intro + cuerpo + outro)
- **Integrar** audio TTS en videos de background
- **Ajustar** velocidad de audio sin alterar el tono
- **Acelerar** procesamiento con GPU NVIDIA (opcional)

## 📋 Requisitos

- **Python** >= 3.11
- **FFmpeg** instalado y disponible en PATH
- **tqdm** >= 4.66.0 (para barras de progreso)
- **GPU NVIDIA** (opcional, para aceleración)

### Verificar FFmpeg

```bash
ffmpeg -version
```

Si no tienes FFmpeg instalado:
- **Windows**: Descargar desde [ffmpeg.org](https://ffmpeg.org/download.html) o usar `winget install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) o `sudo yum install ffmpeg` (RHEL/CentOS)
- **Mac**: `brew install ffmpeg`

### Verificar GPU (Opcional)

Para usar aceleración GPU, FFmpeg debe estar compilado con soporte NVIDIA:

```bash
ffmpeg -encoders | grep nvenc  # Debe mostrar h264_nvenc, hevc_nvenc
ffmpeg -hwaccels | grep cuda   # Debe mostrar cuda
```

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone <repo-url>
cd media-stitcher

# Crear entorno virtual con uv
uv venv
.venv/Scripts/activate.ps1  # Windows PowerShell
# o
source .venv/bin/activate    # Linux/Mac

# Instalar dependencias
pip install -e .

# Instalar dependencias de desarrollo (incluye pytest)
pip install -e ".[dev]"
```

## 💻 Uso

Media-Stitcher ofrece dos interfaces:
1. **CLI** - Línea de comandos (recomendado para uso rápido)
2. **Python API** - Importar funciones en tu código

### CLI - Línea de Comandos

Después de instalar, el comando `media-stitcher` está disponible:

```bash
# Ver ayuda general
media-stitcher --help

# Ver información del sistema (GPU, codecs)
media-stitcher info

# Unir videos
media-stitcher unir intro.mp4 cuerpo.mp4 outro.mp4 -o final.mp4

# Unir con GPU y progreso
media-stitcher unir video1.mp4 video2.mp4 -o output.mp4 -f -g -p

# Integrar audio a video
media-stitcher integrar video.mp4 audio.mp3 -o output.mp4

# Ajustar velocidad de audio
media-stitcher ajustar audio.mp3 1.5 -o rapido.mp3

# Recortar segmento (de 10 a 30 segundos)
media-stitcher recortar video.mp4 10 30 -o clip.mp4

# Recortar desde inicio hasta 2 minutos
media-stitcher recortar video.mp4 00:00:00 00:02:00 -o clip.mp4

# Logging a archivo
media-stitcher unir video1.mp4 video2.mp4 -o output.mp4 --log-file logs/operacion.log
```

**Opciones CLI comunes:**
- `-o, --output`: Archivo de salida (requerido)
- `-g, --gpu`: Usar aceleración GPU
- `-p, --progress`: Mostrar barra de progreso
- `-v, --verbose`: Modo verbose (más logs)
- `--log-file FILE`: Guardar logs en archivo

### Python API

```python
from media_stitcher import (
    unir_archivos,
    integrar_audio_a_video,
    ajustar_velocidad_audio,
    recortar_segmento
)
```

### Ejemplos

#### 1. Unir múltiples videos (intro + cuerpo + outro)

```python
from media_stitcher import unir_archivos

# Modo básico (rápido, sin re-encoding)
resultado = unir_archivos(
    lista_paths=["intro.mp4", "cuerpo.mp4", "outro.mp4"],
    output_path="video_final.mp4",
    safe_mode=True  # concat demuxer (requiere mismo formato)
)

# Con GPU y barra de progreso
resultado = unir_archivos(
    lista_paths=["video1.mp4", "video2.mp4"],
    output_path="video_final.mp4",
    safe_mode=False,      # concat filter (acepta formatos mixtos)
    use_gpu=True,         # Usar aceleración NVIDIA
    show_progress=True    # Mostrar barra de progreso
)
```

**Parámetros:**
- `lista_paths`: Lista de archivos a concatenar (en orden)
- `output_path`: Ruta del archivo de salida
- `safe_mode`:
  - `True` (default): concat demuxer - más rápido, sin re-encoding, requiere mismo formato/codec
  - `False`: concat filter - más lento, re-encoding, acepta formatos mixtos, **soporta GPU**
- `use_gpu`: Si True, usa aceleración GPU NVIDIA (solo con safe_mode=False)
- `show_progress`: Si True, muestra barra de progreso con tqdm

#### 2. Integrar audio TTS en video de background

```python
from media_stitcher import integrar_audio_a_video

# Modo básico
resultado = integrar_audio_a_video(
    video_path="background_loop.mp4",
    audio_path="narration_tts.mp3",
    output_path="video_con_audio.mp4",
    reemplazar_audio=True  # Reemplaza audio existente del video
)

# Con GPU y progreso
resultado = integrar_audio_a_video(
    video_path="background.mp4",
    audio_path="audio.mp3",
    output_path="output.mp4",
    use_gpu=True,         # Usar decoding acelerado
    show_progress=True    # Mostrar progreso
)
```

**Parámetros:**
- `video_path`: Archivo de video (o imagen estática)
- `audio_path`: Archivo de audio a incrustar
- `output_path`: Ruta del archivo de salida
- `reemplazar_audio`: Si True, reemplaza audio del video; si False, mezcla (TODO)
- `use_gpu`: Si True, usa aceleración GPU para decoding
- `show_progress`: Si True, muestra barra de progreso

#### 3. Ajustar velocidad de audio sin cambiar el tono

```python
from media_stitcher import ajustar_velocidad_audio

# Acelerar audio al 125% para reducir duración
resultado = ajustar_velocidad_audio(
    audio_path="guion_largo.mp3",
    factor_velocidad=1.25,  # 1.0 = normal, 1.25 = 25% más rápido
    output_path="guion_acelerado.mp3"
)
```

**Parámetros:**
- `audio_path`: Archivo de audio
- `factor_velocidad`: Factor de velocidad (0.5 = 50%, 2.0 = 200%)
  - Rango soportado: 0.5 - 100.0 (se encadenan filtros automáticamente)
  - Mantiene el pitch/tono original usando filtro `atempo`
- `output_path`: Ruta del archivo de salida

#### 4. Recortar segmento de video/audio (NUEVO v0.3.0)

```python
from media_stitcher import recortar_segmento

# Extraer clip de 1:30 a 2:45
resultado = recortar_segmento(
    input_path="video.mp4",
    start_time="00:01:30",  # O usar segundos: 90
    end_time="00:02:45",    # O usar segundos: 165
    output_path="clip.mp4",
    stream_copy=True        # Rápido, sin re-encoding
)

# Remover intro (cortar desde 10 segundos hasta el final)
resultado = recortar_segmento(
    input_path="video.mp4",
    start_time=10,
    end_time=None,          # None = hasta el final
    output_path="sin_intro.mp4"
)

# Con re-encoding y GPU
resultado = recortar_segmento(
    input_path="video.mp4",
    start_time=30,
    end_time=120,
    output_path="clip.mp4",
    stream_copy=False,      # Re-encodificar
    use_gpu=True,
    show_progress=True
)
```

**Parámetros:**
- `input_path`: Archivo de entrada
- `start_time`: Tiempo de inicio (string "HH:MM:SS" o número en segundos)
- `end_time`: Tiempo de fin (mismo formato que start_time, None para fin del archivo)
- `output_path`: Ruta del archivo de salida
- `stream_copy`: Si True, copia streams (rápido). Si False, re-encodifica (preciso)
- `use_gpu`: Si True, usa GPU para re-encoding
- `show_progress`: Si True, muestra barra de progreso

### Script de ejemplo completo

Ver `main.py` para ejemplos completos del flujo de trabajo:

```bash
python main.py
```

## 🎮 Aceleración GPU

Media-Stitcher puede usar GPU NVIDIA para acelerar el procesamiento de video:

### Qué se acelera con GPU:

- **Decoding (cuvid)**: Lectura de videos más rápida
- **Encoding (nvenc)**: Generación de videos más rápida
  - **H.264** (h264_nvenc) - Codec estándar
  - **HEVC/H.265** (h265_nvenc) - Mejor compresión (v0.3.0)
  - **VP9** (vp9_nvenc) - Codec web (v0.3.0, si disponible)
- **Filtros CUDA**: Procesamiento de video acelerado

### Uso de GPU:

```python
# GPU se activa con el parámetro use_gpu=True
unir_archivos(
    ["video1.mp4", "video2.mp4"],
    "output.mp4",
    safe_mode=False,  # GPU solo funciona con concat filter
    use_gpu=True      # Activar GPU
)
```

### Detección automática:

Media-Stitcher detecta automáticamente las capacidades GPU de tu sistema:

```python
from media_stitcher.utils import detectar_gpu_nvidia

gpu_info = detectar_gpu_nvidia()
print(f"GPU disponible: {gpu_info['disponible']}")
print(f"nvenc: {gpu_info['nvenc']}")
print(f"cuvid: {gpu_info['cuvid']}")
```

**Nota**: Si GPU no está disponible o falla, la operación continúa automáticamente en CPU.

## 📁 Estructura del Proyecto

```
media-stitcher/
├── media_stitcher/          # Paquete principal
│   ├── __init__.py          # Exporta funciones públicas
│   ├── core.py              # Funciones principales (con GPU)
│   └── utils.py             # Utilidades, validaciones, GPU
├── tests/                   # Tests unitarios
│   ├── __init__.py
│   └── test_core.py         # Tests con pytest
├── video-samples/           # Archivos de prueba (no versionados)
├── main.py                  # Script de ejemplo
├── pytest.ini               # Configuración de pytest
├── CLAUDE.md                # Contexto del proyecto para IA
├── README.md                # Este archivo
└── pyproject.toml           # Configuración del proyecto
```

## 🧪 Tests

Media-Stitcher incluye tests unitarios con pytest:

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con output verbose
pytest -v

# Ejecutar tests específicos
pytest tests/test_core.py::test_unir_archivos_basico

# Ejecutar solo tests que no requieren GPU
pytest -m "not gpu"
```

Los tests usan archivos reales de `video-samples/` para validación de integración.

## 🔧 Desarrollo

### Activar entorno virtual

```bash
# Windows PowerShell
.venv/Scripts/activate.ps1

# Linux/Mac
source .venv/bin/activate
```

### Logging

Todas las funciones usan logging para reportar progreso y errores:

```python
import logging
logging.basicConfig(level=logging.INFO)  # Ya configurado por defecto
```

Output:
```
[INFO] FFmpeg detectado correctamente
[INFO] GPU NVIDIA detectada: nvenc=True, cuvid=True, cuda=True
[INFO] Iniciando: Unir archivos -> video_final.mp4
[INFO] ✓ Unir archivos -> video_final.mp4 completada exitosamente
```

### Progress Bars

Con `show_progress=True`, verás barras de progreso visuales:

```
Unir archivos -> output.mp4: 65%|████████▌    | 13.2s/20.0s [00:15<00:07, 1.2s/it]
```

## 🐛 Troubleshooting

### Error: "FFmpeg no encontrado en PATH"

Asegúrate de que FFmpeg esté instalado y accesible:

```bash
ffmpeg -version
```

Si no funciona, agrega FFmpeg a tu PATH o especifica la ruta completa.

### Error: "GPU NVIDIA no disponible"

Verifica que FFmpeg tenga soporte NVIDIA:

```bash
ffmpeg -encoders | grep nvenc
ffmpeg -hwaccels | grep cuda
```

Si no aparecen, necesitas reinstalar FFmpeg con soporte NVIDIA o descargarlo de [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).

### Falla con "safe_mode=True" pero diferentes formatos

Si los videos tienen diferentes codecs/resoluciones, usa `safe_mode=False`:

```python
unir_archivos(["video1.mp4", "video2.avi"], "output.mp4", safe_mode=False)
```

Esto re-encodificará los videos (más lento) para compatibilidad.

### ImportError: No module named 'tqdm'

Instala las dependencias:

```bash
pip install tqdm
# o
pip install -e .
```

## 🚧 Roadmap

Ver `CLAUDE.md` para el roadmap completo. Funcionalidades futuras:

### Fase 3: Optimización
- [ ] Detección automática de duración de videos
- [ ] Métricas de rendimiento (tiempo de procesamiento)
- [ ] Soporte para más codecs GPU (HEVC, AV1)

### Fase 4: Sincronización Audio-Video
- [ ] Detectar duración de audio/video
- [ ] Ajustar velocidad automáticamente para match de duración
- [ ] Fade in/out de audio
- [ ] Normalización de volumen

## 📄 Licencia

[Especificar licencia]

## 🤝 Contribuciones

Para mantener el enfoque del proyecto, consulta la **Regla de Oro Antidistracción** en `CLAUDE.md` antes de proponer nuevas funcionalidades.

---

**Versión**: 0.3.0
**Última actualización**: 2025-10-23

## 🆕 Novedades v0.3.0

- ✅ **CLI completa** con argparse
- ✅ **Función `recortar_segmento()`** para extraer clips
- ✅ **Logging a archivo** configurable
- ✅ **Codecs GPU adicionales**: HEVC/H.265, VP9
- ✅ **Comando `media-stitcher info`** para verificar sistema
