# CLAUDE.md - Contexto del Proyecto TTS-py

## Filosofía del Proyecto
"Hecho es Mejor que Perfecto" - Este proyecto prioriza funcionalidad práctica sobre perfección técnica.

## Propósito
TTS-py es una utilidad de línea de comandos para **síntesis de voz basada en referencia de audio** (Text-to-Speech con clonación de voz). Es una herramienta ligera, enfocada y potente para crear contenido de audio con voces personalizadas.

## Casos de Uso
- 📖 Crear audiolibros personalizados de tus notas o textos
- 🎬 Producción de videos con narraciones personalizadas
- 🎭 Generar múltiples personajes con voces distintas para historias
- 🎙️ Producción de podcasts
- 📝 Convertir documentos y apuntes a audio
- 🎮 Crear voces para personajes de videojuegos o proyectos creativos

## Stack Tecnológico

### Core
- **Python 3.11+** - Lenguaje base
- **uv** - Gestor de paquetes y entornos virtuales (reemplazo moderno de pip/venv)
- **Chatterbox Multilingual TTS** (ResembleAi) - Modelo principal de síntesis de voz
  - Soporta ~23 idiomas
  - Capacidad de síntesis basada en referencia de audio
  - Modelo de código abierto de ResembleAi

### Procesamiento de Audio
- **Whisper/faster-whisper** - Para análisis y procesamiento de audio de referencia
  - Se prefiere la versión que mejor aproveche GPU NVIDIA disponible
  - Usado para mejorar la calidad de las muestras de referencia

## Arquitectura del Proyecto

### Estructura de Directorios
```
tts-py/
├── main.py                  # Punto de entrada principal
├── pyproject.toml          # Configuración del proyecto (uv/pip)
├── .python-version         # Versión de Python para pyenv/uv
├── README.md               # Documentación de usuario
├── CLAUDE.md               # Este archivo - contexto para Claude
├── CHANGELOG.md            # Registro de cambios entre versiones
├── TODO.md                 # Tareas pendientes y roadmap
├── .venv/                  # Entorno virtual (no commitear)
├── creative-scripts/       # Input: Guiones de texto para convertir
├── audio-samples/          # Input: Muestras de audio para referencia de voz
└── output-dir/            # Output: Audio generado
```

### Flujo de Trabajo Esperado
1. Usuario coloca guiones de texto en `creative-scripts/`
2. Usuario proporciona muestras de voz en `audio-samples/`
3. Usuario ejecuta `uv run main.py` con argumentos apropiados
4. El script procesa el texto usando el modelo Chatterbox
5. El modelo genera audio imitando la voz de referencia
6. Audio final se guarda en `output-dir/`

## Principios de Desarrollo

### Documentación de Código
- **TODA función debe tener docstring** explicando:
  - Qué hace
  - Por qué existe (contexto/razón)
  - Parámetros esperados
  - Valor de retorno
  - Ejemplo de uso si no es obvio

### Estándares de Código
- Usar type hints en todas las funciones
- Nombres descriptivos en español (variables, funciones, comentarios)
- Mantener funciones pequeñas y con responsabilidad única
- Comentarios que explican el "por qué", no el "qué"

### Gestión de Dependencias
- Usar `uv add <paquete>` para agregar dependencias
- Documentar en CHANGELOG.md cuando se agregue una dependencia importante
- Preferir bibliotecas bien mantenidas y con buena documentación

## Estado Actual del Proyecto
**Versión:** 0.1.0 (Inicialización)
**Estado:** Proyecto nuevo, solo estructura básica
**Última actualización:** 2025-10-19

## Notas Importantes

### Ética y Legalidad
Este proyecto está diseñado para uso **legal y ético** de síntesis de voz:
- ✅ Crear tus propios audiolibros con tu voz
- ✅ Generar voces para proyectos personales/creativos
- ✅ Producción de contenido donde tienes derechos de la voz
- ❌ NO usar para suplantar identidad
- ❌ NO usar para engañar o defraudar
- ❌ NO usar voces de personas sin su consentimiento explícito

### Consideraciones Técnicas
- El modelo requiere GPU para mejor rendimiento (NVIDIA preferida)
- Las muestras de audio de mejor calidad producen mejores resultados
- Se recomienda audio de referencia de al menos 10-30 segundos
- Formatos soportados: WAV, MP3, FLAC (confirmar según implementación)

## Recursos y Referencias
- [Chatterbox Multilingual TTS](https://huggingface.co/ResembleAI) - Modelo base
- [Whisper OpenAI](https://github.com/openai/whisper) - Procesamiento de audio
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Versión optimizada

## Contacto y Mantenimiento
**Mantenedor:** developer
**Repositorio:** github.com/pyllm-utilities/tts-py

---
**Última actualización de este documento:** 2025-10-19
**Versión del documento:** 1.0
