# TODO - TTS-py Roadmap

## Leyenda
- 🔴 Crítico/Bloqueante
- 🟡 Importante
- 🟢 Nice to have
- ✅ Completado
- 🚧 En progreso
- ⏸️ En pausa
- 📅 Planificado

---

## Fase 0: Fundación y Configuración ✅
**Objetivo:** Establecer la base del proyecto con documentación y estructura

- [✅] Inicializar proyecto con uv
- [✅] Crear pyproject.toml
- [✅] Crear README.md básico
- [✅] Crear CLAUDE.md con contexto completo
- [✅] Crear TODO.md (este archivo)
- [✅] Crear CHANGELOG.md
- [🚧] Actualizar README.md con instrucciones completas

---

## Fase 1: MVP Funcional ✅ **COMPLETADA**
**Objetivo:** Crear MVP funcional que convierta texto a audio con voz de referencia

### 1.1 Configuración del Entorno ✅
- [✅] Investigar y documentar instalación de Chatterbox TTS
- [✅] Agregar dependencias necesarias a pyproject.toml
  - [✅] Chatterbox TTS 0.1.3
  - [✅] PyTorch 2.6.0 con CUDA 12.4
  - [✅] torchaudio 2.6.0
  - [✅] Librería de procesamiento de audio (soundfile, librosa)
  - [✅] argparse para CLI (built-in Python)
- [✅] Crear estructura de directorios (`creative-scripts/`, `audio-samples/`, `output-dir/`)
- [✅] Crear `.gitignore` apropiado

### 1.2 Funcionalidad Core ✅
- [✅] Implementar carga de archivo de audio de referencia
  - [✅] Validar formato de audio (WAV, MP3, FLAC)
  - [✅] Validar existencia de archivo
- [✅] Implementar carga de guión de texto
  - [✅] Soportar .txt plano
  - [✅] Validar encoding (UTF-8)
- [✅] Integrar modelo Chatterbox TTS
  - [✅] Cargar modelo con detección automática de GPU
  - [✅] Procesar audio de referencia
  - [✅] Generar síntesis de voz
- [✅] Implementar guardado de audio generado
  - [✅] Formato WAV
  - [✅] Rutas personalizables

### 1.3 CLI Básica ✅
- [✅] Implementar argumentos de línea de comandos
  - [✅] `--text` o `-t`: Texto directo desde CLI
  - [✅] `--script` o `-s`: Ruta al guión
  - [✅] `--voice` o `-v`: Ruta al audio de referencia
  - [✅] `--output` o `-o`: Ruta de salida
  - [✅] `--cpu`: Forzar uso de CPU
- [✅] Implementar logging básico
  - [✅] Progreso del procesamiento
  - [✅] Errores descriptivos
- [✅] Agregar mensajes de ayuda (`--help`)
- [✅] Manejo robusto de errores

### 1.4 Fixes Críticos ✅
- [✅] Solución problema IPv6 en WSL2
- [✅] Workaround XET HuggingFace (HF_HUB_DISABLE_XET=1)
- [✅] Patch Perth Watermarker (DummyWatermarker)

---

## Fase 2: Mejoras y Usabilidad 🚧
**Objetivo:** Hacer la herramienta más robusta y fácil de usar

### 2.1 UX y Performance 🟡 **PRÓXIMO**
- [ ] 📊 Barra de progreso visual con tqdm
  - [ ] Mostrar progreso durante generación
  - [ ] Estimación de tiempo restante
  - [ ] Mejora visual de la experiencia
- [ ] 💾 Cache de voces procesadas
  - [ ] Guardar voces de referencia procesadas
  - [ ] Evitar reprocesar la misma voz
  - [ ] Comando `--voice-name` para reutilizar
  - [ ] Almacenar en `~/.cache/tts-py/voices/`
- [ ] 🌍 Soporte para Chatterbox Multilingual
  - [ ] Agregar parámetro `--language es/en/fr/zh/etc`
  - [ ] Soportar 23 idiomas disponibles
  - [ ] Documentar idiomas soportados

### 2.2 Manejo de Errores ✅ (Parcialmente Completado)
- [✅] Validación de archivos de entrada
  - [✅] Verificar existencia de archivos
  - [✅] Validar formatos soportados
  - [✅] Mensajes de error claros y accionables
- [✅] Manejo de GPU/CPU
  - [✅] Detectar disponibilidad de GPU NVIDIA
  - [✅] Fallback a CPU si no hay GPU
  - [✅] Mensajes informativos sobre hardware usado

### 2.2 Optimización de Audio 🟡
- [ ] Implementar pre-procesamiento de audio de referencia con Whisper
  - [ ] Reducción de ruido
  - [ ] Normalización de volumen
- [ ] Implementar post-procesamiento de audio generado
  - [ ] Normalización
  - [ ] Eliminar silencios largos (opcional)

### 2.3 Formatos y Opciones 🟢
- [ ] Soportar múltiples formatos de salida
  - [ ] MP3
  - [ ] FLAC
  - [ ] OGG
- [ ] Opciones de calidad de audio
  - [ ] Bitrate configurable
  - [ ] Sample rate configurable

---

## Fase 3: Características Avanzadas 📅
**Objetivo:** Funcionalidades que eleven la utilidad de la herramienta

### 3.1 Procesamiento por Lotes 🟢
- [ ] Procesar múltiples guiones de una vez
- [ ] Procesar con múltiples voces de referencia
- [ ] Matriz de voz-guión (cada guión con cada voz)

### 3.2 Gestión de Proyectos 🟢
- [ ] Archivo de configuración de proyecto (YAML/JSON)
  - [ ] Mapeo de personajes a voces de referencia
  - [ ] Configuraciones por defecto
- [ ] Comando para crear proyecto nuevo
- [ ] Templates de proyectos (audiolibro, podcast, etc.)

### 3.3 Metadata y Organización 🟢
- [ ] Agregar metadata a archivos de audio
  - [ ] Título, artista, álbum
  - [ ] Información del modelo usado
- [ ] Generación de manifesto del proyecto
  - [ ] Lista de archivos generados
  - [ ] Configuración usada
  - [ ] Timestamps

---

## Fase 4: Testing y Calidad 📅

### 4.1 Tests 🟡
- [ ] Tests unitarios para funciones core
- [ ] Tests de integración
- [ ] Tests con diferentes formatos de audio
- [ ] Tests con diferentes idiomas

### 4.2 Documentación 🟡
- [ ] Documentación completa de API
- [ ] Ejemplos de uso
- [ ] Troubleshooting guide
- [ ] FAQ

---

## Fase 5: Distribución 📅

### 5.1 Empaquetado 🟢
- [ ] Configurar para publicación en PyPI
- [ ] Crear ejecutable standalone (PyInstaller/Nuitka)
- [ ] Docker image para fácil deployment

### 5.2 CI/CD 🟢
- [ ] GitHub Actions para testing
- [ ] Automatizar releases
- [ ] Automatizar building de ejecutables

---

## Ideas Futuras (Sin Prioridad Definida)

### Features Avanzadas Propuestas
- [ ] 🎙️ Modo streaming/chunk processing para textos largos
  - [ ] Dividir en párrafos automáticamente
  - [ ] Generar por partes para evitar timeouts
- [ ] 🔇 Detección de calidad de audio de referencia
  - [ ] Validar calidad antes de procesar
  - [ ] Alertar sobre ruido, volumen bajo, duración corta
- [ ] 🎭 Preset de voces (voices.json)
  - [ ] Guardar voces favoritas con nombres
  - [ ] `--preset narrator` carga automáticamente
- [ ] 📝 Modo interactivo
  - [ ] Guiar al usuario paso a paso
  - [ ] Ideal para usuarios no técnicos
- [ ] ⚙️ Archivo de configuración `.tts-py.yaml`
  - [ ] Configuraciones default del proyecto
  - [ ] GPU/CPU preference, formato, calidad
- [ ] 📖 Detección automática de capítulos
  - [ ] Parsear `# Capítulo 1` del texto
  - [ ] Generar archivos separados
- [ ] 🔄 Resume generation
  - [ ] Guardar progreso en `.progress.json`
  - [ ] Retomar si falla a mitad
- [ ] 🎚️ Control de prosodia básico
  - [ ] `--speed 0.9/1.1` para velocidad
  - [ ] `--pitch +2/-2` para tono
- [ ] 📊 Estadísticas post-generación
  - [ ] Duración, palabras/minuto, tamaño
  - [ ] Tiempo de procesamiento

### Features Muy Futuras
- [ ] Web UI simple (Gradio/Streamlit)
- [ ] API REST para integración con otros servicios
- [ ] Plugin para editores de video (DaVinci Resolve, Premiere)
- [ ] Soporte para SSML (Speech Synthesis Markup Language)
- [ ] Fine-tuning del modelo con voces propias
- [ ] Multi-speaker synthesis (diálogos automáticos)
- [ ] Efectos de audio (reverb, echo, etc.)

---

## Bugs Conocidos y Workarounds

### ✅ Resueltos
- [✅] **IPv6 roto en WSL2**: Deshabilitado con `sysctl disable_ipv6`
- [✅] **XET CAS Server error 500**: Workaround con `HF_HUB_DISABLE_XET=1`
- [✅] **Perth Watermarker TypeError**: Patch usando `DummyWatermarker`

### ⚠️ Limitaciones Conocidas
- **Watermark ausente**: Se usa `DummyWatermarker` en lugar de `PerthImplicitWatermarker` (requiere recompilación nativa)
- **Deprecation warnings**: Warnings de `LoRACompatibleLinear` y `torch.backends.cuda.sdp_kernel()` (no afectan funcionalidad)

---

## Notas de Desarrollo
- Priorizar siempre la experiencia del usuario en terminal
- Mantener el principio "Hecho es Mejor que Perfecto"
- Documentar decisiones importantes en CHANGELOG.md
- Cada feature debe ser funcional antes de pasar a la siguiente
- Usar `uv run` como workflow principal
- Todos los fixes críticos deben documentarse

---

## Estado del Proyecto
**Versión actual:** 0.2.0
**Estado:** ✅ MVP Funcional Completo
**Próximo hito:** Fase 2.1 (UX y Performance)
**Hardware probado:** NVIDIA RTX 3060 12GB, CUDA 12.4, WSL2 Ubuntu

---

**Última actualización:** 2025-10-20
**Próxima revisión:** Después de completar Fase 2.1
