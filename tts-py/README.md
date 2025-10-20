# TTS-py 🎙️

**Síntesis de Voz con Clonación Basada en Referencia de Audio**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/package%20manager-uv-blueviolet)](https://github.com/astral-sh/uv)

TTS-py es una utilidad de línea de comandos ligera y potente para **convertir texto a audio con clonación de voz**. Utiliza Chatterbox TTS de ResembleAI para generar audio natural con la capacidad de imitar voces a partir de muestras de referencia.

---

## ✨ Características

- 🎯 **CLI Simple y Directa** - Interfaz de línea de comandos intuitiva
- 🎙️ **Clonación de Voz** - Genera audio imitando cualquier voz de referencia
- 🚀 **Aceleración GPU** - Detección automática de NVIDIA CUDA
- 📝 **Múltiples Entradas** - Texto directo o archivos de guion
- 🎵 **Formatos Soportados** - WAV, MP3, FLAC para audio de referencia
- 💾 **Cache de Voces** - Sistema inteligente para reutilizar voces procesadas
- 📊 **Barra de Progreso** - Indicador visual en tiempo real
- 💻 **Workflow Moderno** - Gestión de paquetes con `uv`
- 🔧 **Robusto** - Manejo de errores y validaciones completas

---

## 🎯 Casos de Uso

- 📖 **Audiolibros personalizados** - Convierte tus notas o textos a audio
- 🎬 **Producción de videos** - Narraciones con voces personalizadas
- 🎭 **Historias multi-personaje** - Genera voces distintas para cada personaje
- 🎙️ **Podcasts** - Producción de contenido de audio
- 📝 **Documentos a audio** - Escucha tus apuntes mientras haces otras cosas
- 🎮 **Voces para juegos** - Crea voces para personajes de proyectos creativos

---

## 🚀 Instalación

### Requisitos

- **Python 3.11+**
- **uv** (gestor de paquetes moderno)
- **GPU NVIDIA con CUDA** (recomendado, funciona en CPU también)
- **~8GB de espacio en disco** (para modelos)

### Paso 1: Instalar uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Paso 2: Clonar el Repositorio

```bash
git clone https://github.com/pyllm-utilities/tts-py.git
cd tts-py
```

### Paso 3: Instalar Dependencias

```bash
# uv creará automáticamente el entorno virtual e instalará todo
uv sync
```

**Nota para WSL2:** Si estás en WSL2 y tienes problemas de red, ejecuta:
```bash
# Deshabilitar IPv6 (solo si tienes errores de conexión)
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1
```

---

## 📖 Uso

### Sintaxis Básica

```bash
uv run main.py [OPCIONES]
```

### Ejemplos

#### 1. Texto Simple

Genera audio a partir de texto directamente:

```bash
uv run main.py --text "Hola, bienvenido a TTS-py" --output salida.wav
```

#### 2. Desde Archivo de Guion

Lee el texto desde un archivo:

```bash
uv run main.py --script creative-scripts/mi_guion.txt --output salida.wav
```

#### 3. Con Voz de Referencia (Clonación)

Usa una muestra de audio para clonar la voz:

```bash
uv run main.py \
  --text "Este audio usará la voz de referencia" \
  --voice audio-samples/mi_voz.wav \
  --output salida.wav
```

#### 4. Guion + Voz de Referencia

Combina un guion extenso con voz personalizada:

```bash
uv run main.py \
  --script creative-scripts/audiolibro.txt \
  --voice audio-samples/narrador.wav \
  --output audiolibro.wav
```

#### 5. Con Cache de Voz (Recomendado)

Guarda la voz procesada para reutilización:

```bash
# Primera vez: procesa y guarda en cache
uv run main.py \
  --text "Primer uso de esta voz" \
  --voice audio-samples/narrador.wav \
  --voice-name "narrador" \
  --output salida1.wav

# Siguientes usos: más rápido (usa cache)
uv run main.py \
  --text "Reutilizando la misma voz" \
  --voice audio-samples/narrador.wav \
  --voice-name "narrador" \
  --output salida2.wav
```

#### 6. Forzar Uso de CPU

Si no tienes GPU o quieres usar CPU:

```bash
uv run main.py --text "Texto aquí" --output salida.wav --cpu
```

---

## 🎛️ Opciones de Línea de Comandos

| Opción | Descripción |
|--------|-------------|
| `-t, --text TEXT` | Texto a sintetizar directamente desde CLI |
| `-s, --script PATH` | Ruta a archivo .txt con el guion |
| `-v, --voice PATH` | Ruta a audio de referencia para clonar voz (WAV/MP3/FLAC) |
| `--voice-name NAME` | Nombre para guardar/cargar voz desde cache (mejora rendimiento) |
| `-o, --output PATH` | Ruta donde guardar el audio generado (default: `output-dir/output.wav`) |
| `--cpu` | Forzar uso de CPU en lugar de GPU |
| `-h, --help` | Mostrar ayuda completa |

**Notas:**
- `--text` y `--script` son mutuamente excluyentes (usa uno u otro)
- `--voice-name` solo funciona con `--voice`
- El cache se guarda en `~/.cache/tts-py/voices/`

---

## 📁 Estructura del Proyecto

```
tts-py/
├── main.py                 # Script principal
├── test_simple.py          # Script de prueba
├── pyproject.toml          # Configuración del proyecto
├── README.md               # Este archivo
├── CHANGELOG.md            # Registro de cambios
├── TODO.md                 # Roadmap y tareas pendientes
├── CLAUDE.md               # Contexto para desarrollo
├── creative-scripts/       # 📝 Coloca aquí tus guiones
│   ├── ejemplo.txt         # Ejemplo incluido
│   └── README.md           # Guía de uso
├── audio-samples/          # 🎙️ Coloca aquí tus muestras de voz
│   └── README.md           # Guía de grabación
├── output-dir/             # 🎵 Audio generado se guarda aquí
└── .venv/                  # Entorno virtual (auto-generado)
```

---

## 🎙️ Guía de Muestras de Audio

Para obtener mejores resultados con clonación de voz:

### ✅ Características de Buena Muestra

- **Duración:** 10-30 segundos mínimo
- **Calidad:** Audio limpio, sin ruido de fondo
- **Contenido:** Habla natural, entonación normal
- **Formato:** WAV sin comprimir (44.1kHz o 48kHz recomendado)
- **Voz única:** Solo una persona hablando

### ❌ Evitar

- ❌ Audio con música de fondo
- ❌ Ruido ambiental excesivo
- ❌ Susurros o gritos
- ❌ Múltiples voces sobrepuestas
- ❌ Compresión excesiva (MP3 de baja calidad)

### 📝 Texto Recomendado para Grabar

> "Hola, mi nombre es [tu nombre]. Me gusta leer libros, escuchar música y aprender cosas nuevas. Hoy hace un día soleado y espero que tengas un excelente día. Gracias por escuchar."

Más detalles en: [`audio-samples/README.md`](audio-samples/README.md)

---

## ⚙️ Requisitos Técnicos

### Hardware Recomendado

- **GPU:** NVIDIA con CUDA (RTX 2060 o superior)
- **VRAM:** 6GB mínimo, 8GB+ recomendado
- **RAM:** 16GB recomendado
- **Disco:** 10GB libres (modelos + cache)

### Hardware Mínimo

- **CPU:** Procesador moderno multi-core
- **RAM:** 8GB mínimo
- **Disco:** 10GB libres

**Nota:** Sin GPU, la generación será significativamente más lenta (10-20x más tiempo).

---

## 🔧 Solución de Problemas

### Error: "No module named 'chatterbox'"

```bash
# Reinstalar dependencias
uv sync
```

### Error: "CUDA not available" (teniendo GPU NVIDIA)

1. Verifica drivers NVIDIA: `nvidia-smi`
2. Reinstala PyTorch con CUDA:
   ```bash
   uv add torch torchaudio --index-url https://download.pytorch.org/whl/cu124
   ```

### Error: "RuntimeError: Data processing error: CAS service error"

Esto es un problema conocido de HuggingFace XET. Ya está solucionado en el código con `HF_HUB_DISABLE_XET=1`.

### Error de conexión en WSL2

```bash
# Deshabilitar IPv6
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1
```

### Audio generado con mala calidad

- Usa una mejor muestra de referencia (ver guía arriba)
- Asegúrate de tener GPU habilitada
- Verifica que el texto no tenga caracteres raros

Más detalles en: [CHANGELOG.md](CHANGELOG.md) sección "Fixes Críticos"

---

## 📊 Rendimiento

Probado en **NVIDIA RTX 3060 12GB** con **CUDA 12.4**:

| Tipo de Texto | Duración Audio | Tiempo Generación |
|---------------|----------------|-------------------|
| Frase corta (10 palabras) | ~3 segundos | ~6 segundos |
| Párrafo (100 palabras) | ~30 segundos | ~30 segundos |
| Guion largo (500 palabras) | ~3 minutos | ~2.5 minutos |

**Ratio promedio:** ~1:1 (genera audio casi en tiempo real con GPU)

---

## 🛣️ Roadmap

### ✅ Fase 1: MVP (Completado - v0.2.0)
- [x] CLI funcional
- [x] Síntesis de texto básica
- [x] Clonación de voz con referencia
- [x] Detección automática de GPU
- [x] Manejo robusto de errores

### ✅ Fase 2.1: UX y Performance (Completado - v0.3.0)
- [x] Barra de progreso visual
- [x] Cache de voces procesadas
- [x] Estimación de tiempo de generación

### 🚧 Fase 2.2: Features Avanzadas (Próximo)
- [ ] Soporte multilingüe (23 idiomas)
- [ ] Modo batch (múltiples archivos)
- [ ] Detección de calidad de audio de referencia

### 📅 Fase 3: Avanzado (Futuro)
- [ ] Modo interactivo
- [ ] Presets de voces
- [ ] Control de velocidad/tono
- [ ] Detección automática de capítulos

Ver roadmap completo en: [TODO.md](TODO.md)

---

## ⚖️ Ética y Legalidad

⚠️ **IMPORTANTE:** Este proyecto está diseñado para uso **ético y legal** solamente.

### ✅ Usos Permitidos
- Crear audiolibros con tu propia voz
- Generar voces para proyectos personales/creativos
- Producir contenido donde tienes derechos de la voz
- Experimentación y aprendizaje

### ❌ Usos Prohibidos
- ❌ **Suplantación de identidad**
- ❌ **Uso de voces sin consentimiento**
- ❌ **Engaño o fraude**
- ❌ **Deepfakes maliciosos**

**Responsabilidad:** El uso de esta herramienta es responsabilidad del usuario. Respeta siempre la privacidad y derechos de las personas.

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas, encuentras bugs, o quieres mejorar el proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: Amazing feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- **ResembleAI** - Por el modelo Chatterbox TTS de código abierto
- **HuggingFace** - Por la infraestructura de modelos
- **uv** (Astral) - Por el gestor de paquetes moderno
- **PyTorch** - Por el framework de deep learning

---

## 📧 Contacto

**Mantenedor:** developer
**Repositorio:** [github.com/pyllm-utilities/tts-py](https://github.com/pyllm-utilities/tts-py)
**Issues:** [github.com/pyllm-utilities/tts-py/issues](https://github.com/pyllm-utilities/tts-py/issues)

---

## 🔗 Enlaces Útiles

- [Documentación de Chatterbox](https://huggingface.co/ResembleAI/chatterbox)
- [uv Documentation](https://github.com/astral-sh/uv)
- [PyTorch CUDA Setup](https://pytorch.org/get-started/locally/)
- [Troubleshooting WSL2 CUDA](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)

---

<div align="center">

**⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub ⭐**

Made with ❤️ by the TTS-py team

</div>
