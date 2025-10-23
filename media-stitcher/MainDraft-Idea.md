## 💡 Boceto de Idea Central: Wrapper Multimedia de FFmpeg

Esta utilidad será tu **caja de herramientas** personal para el post-procesamiento multimedia, asegurando que el paso final de generación de video de guiones para contenido en `YT` sea completamente independiente.

### 1. Núcleo de la Utilidad (La Brújula)

- **Nombre de la Utilidad:** **"MediaForge"**

- **Problema que Resuelve:** Eliminar la dependencia de servicios o contenedores de terceros para tareas esenciales de manipulación de archivos multimedia (unir, cortar, incrustar, ajustar velocidad), asegurando la **continuidad operativa** del flujo de creación de contenido.
    
- **Propósito/Objetivo Principal (El "MUST HAVE"):** **Ofrecer una interfaz programática (API/CLI) sencilla y fiable para ejecutar las operaciones más comunes de post-producción de video y audio utilizando comandos `ffmpeg` internos.**
    
---

### 2. El Filtro de Funcionalidad (La Regla de Oro Antidistracción)

Esta frase será tu filtro estricto. Cualquier funcionalidad que no pase esta prueba debe ser pospuesta.

> **"Cualquier nueva funcionalidad debe ser una manipulación directa de archivos multimedia (video/audio) que pueda ser resuelta mediante la ejecución de uno o más comandos de FFmpeg, priorizando las operaciones necesarias para ensamblar un video de YouTube."**

- _Ejemplo:_ **"Cualquier nueva funcionalidad debe ser una manipulación directa de archivos multimedia (video/audio) que pueda ser resuelta mediante la ejecución de uno o más comandos de FFmpeg, priorizando las operaciones necesarias para ensamblar un video de YouTube."**
    
---

### 3. Puntos de Inicio para el MVP (Las 3 Operaciones Esenciales)

Para evitar la distracción, enfócate solo en la implementación de las funcionalidades que te permitirán reemplazar al servidor actual para tus videos.

#### A. Funcionalidad de Alto Valor (Core)

|**Operación Requerida**|**¿Por qué es esencial para el MVP?**|**Módulo/Función Inicial**|
|---|---|---|
|**Integrar Audio a Video**|La función principal: incrustar el audio generado por TTS (que ahora será propio) a tu _background_ de video o imagen estática.|`integrar_audio_a_video(video_path, audio_path, output_path)`|
|**Unir o Concatenar**|Esencial para unir la introducción, el cuerpo del video y el _outro_ (o unir varios segmentos de audio si el TTS lo genera por partes).|`unir_archivos(lista_de_paths, output_path)`|
|**Ajustar Velocidad de Audio**|Necesario para controlar la duración final de los guiones largos (@AburrirseParaDormir) sin afectar el _pitch_ o tono (usando el filtro `atempo` de FFmpeg).|`ajustar_velocidad_audio(audio_path, factor_velocidad, output_path)`|

#### B. Estructura de Proyecto con `uv`

1. **Inicialización:** Crea tu proyecto y tu entorno virtual con `uv`.

    - `uv venv`
    - `.venv/Scripts/activate.ps1`
        
2. **Organización del Código:** Empieza con una estructura simple en Python.

    - `mediaforge/`
        - `__init__.py`
        - `main.py` (Manejará la entrada de la línea de comandos).
        - `ffmpeg_wrapper.py` (Contendrá las funciones principales que construyen y ejecutan los comandos `ffmpeg` usando la librería `subprocess` de Python).

#### C. Dependencia Clave

- Asegúrate de que el ejecutable de **`ffmpeg`** esté disponible en el `PATH` del sistema operativo (o contenedor) donde correrá tu utilidad. Tu wrapper de Python solo llamará a este ejecutable.
