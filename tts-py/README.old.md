# TTS-py

> Micro utilidad de línea de comandos para **síntesis de voz basada en referencia de audio**

TTS-py es una herramienta ligera y potente que genera audio a partir de texto, usando una muestra de voz como referencia para crear audio con esa voz específica.

## Casos de Uso

- 📖 **Audiolibros personalizados** - Convierte tus notas y textos a audio con tu propia voz
- 🎬 **Producción de videos** - Genera narraciones y doblajes con voces personalizadas
- 🎭 **Personajes con voces únicas** - Crea diferentes voces para historias y proyectos creativos
- 🎙️ **Podcasts** - Produce episodios con voces consistentes y de calidad
- 📝 **Notas a audio** - Escucha tus apuntes mientras haces otras cosas

## Estado del Proyecto

**Versión actual:** 0.1.0 (Inicialización)
**Estado:** 🚧 En desarrollo activo - MVP en construcción

Consulta [TODO.md](TODO.md) para ver el roadmap completo y [CHANGELOG.md](CHANGELOG.md) para el historial de cambios.

## Requisitos

- Python 3.11 o superior
- [uv](https://github.com/astral-sh/uv) - Gestor de paquetes de Python
- GPU NVIDIA (recomendado, no obligatorio) para mejor rendimiento
- Windows/Linux/MacOS

## Instalación

### 1. Clonar el repositorio
```bash
git clone <repo-url>
cd tts-py
```

### 2. Instalar uv (si no lo tienes)
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Crear entorno virtual e instalar dependencias
```bash
uv sync
```

## Uso Rápido

> ⚠️ **Nota:** La funcionalidad completa aún está en desarrollo. Esta sección se actualizará cuando el MVP esté listo.

```bash
# Forma básica (futura)
uv run main.py --script creative-scripts/mi-guion.txt --reference audio-samples/mi-voz.wav

# Con opciones (futuro)
uv run main.py -s creative-scripts/historia.txt -r audio-samples/voz-personaje.wav -o output-dir/capitulo1.wav
```

## Estructura del Proyecto

```
tts-py/
├── main.py                # Script principal
├── pyproject.toml         # Configuración del proyecto
├── .python-version        # Versión de Python requerida
├── README.md              # Este archivo
├── CLAUDE.md              # Contexto para desarrollo asistido
├── CHANGELOG.md           # Historial de cambios
├── TODO.md                # Roadmap y tareas pendientes
├── project-description.md # Idea original del proyecto
├── .venv/                 # Entorno virtual (no commitear)
├── creative-scripts/      # 📝 Tus guiones de texto (input)
├── audio-samples/         # 🎤 Muestras de voz de referencia (input)
└── output-dir/            # 🔊 Audio generado (output)
```

## Tecnologías

- **Python 3.11+** - Lenguaje base
- **[uv](https://github.com/astral-sh/uv)** - Gestor de paquetes moderno y rápido
- **Chatterbox Multilingual TTS** (ResembleAi) - Modelo de síntesis de voz (~23 idiomas)
- **Whisper/faster-whisper** - Procesamiento y análisis de audio de referencia

## Filosofía del Proyecto

> **"Hecho es Mejor que Perfecto"**

Este proyecto prioriza entregar funcionalidad práctica y usable sobre perfección técnica. Iteramos rápido, aprendemos rápido, mejoramos rápido.

## Ética y Uso Responsable

Esta herramienta está diseñada para **uso legal y ético** de síntesis de voz:

### ✅ Usos Permitidos y Éticos
- Crear audiolibros con tu propia voz
- Generar voces para proyectos creativos personales
- Producir contenido donde tienes derechos de la voz usada
- Experimentación y aprendizaje

### ❌ Usos NO Permitidos
- Suplantar identidad de otras personas
- Crear contenido engañoso o fraudulento
- Usar voces de personas sin su consentimiento explícito
- Cualquier uso malicioso o ilegal

**Responsabilidad:** El uso de esta herramienta es responsabilidad del usuario. Úsala éticamente y respeta los derechos de los demás.

## Contribuir

Este es un proyecto personal, pero las contribuciones son bienvenidas:

1. Revisa [TODO.md](TODO.md) para ver tareas pendientes
2. Abre un issue para discutir cambios grandes
3. Haz un fork y crea un pull request
4. Asegúrate de documentar tu código (docstrings en español)

## Roadmap

Consulta [TODO.md](TODO.md) para el roadmap completo. Fases principales:

- ✅ **Fase 0:** Fundación y documentación
- 📅 **Fase 1:** MVP - Funcionalidad básica de TTS con voz de referencia
- 📅 **Fase 2:** Mejoras de usabilidad y robustez
- 📅 **Fase 3:** Características avanzadas (batch processing, proyectos, etc.)
- 📅 **Fase 4:** Testing y calidad
- 📅 **Fase 5:** Distribución y empaquetado

## Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para el historial completo de cambios.

## Licencia

_Por definir_

## Contacto

- **Issues:** Abre un issue en GitHub para bugs o sugerencias
- **Documentación:** Consulta [CLAUDE.md](CLAUDE.md) para contexto técnico completo

---

**Última actualización:** 2025-10-19 | **Versión:** 0.1.0
