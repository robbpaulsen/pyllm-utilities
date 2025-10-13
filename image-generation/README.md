# 🖼️ Generador de Imágenes FLUX.1-schnell (Together.ai)

## 🌟 Descripción del Proyecto

Esta es una mini utilidad en Python diseñada para automatizar la generación de imágenes de alta calidad utilizando el modelo gratuito **FLUX.1-schnell-Free** de Together.ai.

La herramienta está optimizada para la eficiencia al:

1.  **Gestionar límites:** Realiza las peticiones a la API en intervalos de **12 segundos** para cumplir con las políticas de uso del *endpoint* gratuito.
2.  **Descarga automática:** Guarda las imágenes generadas directamente en una carpeta local.

-----

## 🛠️ Requisitos e Instalación

### Requisitos

  * Python 3.10 o superior.
  * Una clave de API de Together.ai (aunque la del ejemplo funciona para pruebas).

### Instalación de Dependencias

Necesitas instalar las librerías `together` y `requests`. Si usas **Poetry** (el sistema sugerido en el `pyproject.toml`):

```bash
# Instalar dependenicas
uv venv --python cp310 
source .venv/bin/activate
uv sync
```

Si prefieres usar `pip` directamente:

```bash
pip install together requests
```

-----

## ⚙️ Configuración del Proyecto

### Archivos

Este proyecto consta de un único archivo principal:

  * **`generador_flux.py`**: Contiene todo el código de la utilidad (cliente de Together.ai, lógica de *prompt*, bucle de espera y función de descarga).

### Parámetros Hardcodeados

La configuración del modelo está definida al inicio del script para facilitar su gestión. No es necesario modificar estos valores para el uso básico:

| Parámetro | Valor | Notas |
| :--- | :--- | :--- |
| **`MODEL_NAME`** | `black-forest-labs/FLUX.1-schnell-Free` | Endpoint gratuito. |
| **`API_KEY_TOGETHER`** | (Tu clave) | Reemplazar la clave de ejemplo por la tuya. |
| **`DELAY_SECONDS`** | `12` | Intervalo obligatorio entre peticiones a la API. |
| **`MAX_IMAGES`** | `4` | Límite de imágenes por ejecución. |
| **`DESCARGA_FOLDER`** | `imagenes_generadas_flux` | Carpeta local donde se guardarán las imágenes. |

-----

## 🚀 Modo de Uso

Simplemente ejecuta el script de Python:

```bash
uv run image-gen.py
```

### Pasos de la Utilidad

1.  **Prompt:** El programa te pedirá que ingreses la descripción de la imagen.
      * *Ejemplo de entrada:* `un gato cósmico volando sobre un planeta de dona, estilo ilustración digital`
2.  **Imágenes:** Se te preguntará cuántas imágenes deseas generar (entre 1 y 4).
3.  **Generación y Espera:** Por cada imagen:
      * Se descarga la imagen a la carpeta **`imagenes_generadas_flux`**.
      * Si queda más de una imagen por generar, el script **pausará la ejecución por 12 segundos**.
4.  **Resultado:** Al finalizar, el programa mostrará la lista de rutas de los archivos descargados.

-----

## 📂 Estructura de Archivos Descargados

Las imágenes se guardan en la carpeta **`imagenes_generadas_flux`** y el nombre del archivo se construye usando las primeras cinco palabras de tu *prompt* base, más el índice de la imagen:

  * **`imagenes_generadas_flux/`**
      * `un_gato_cósmico_volando_sobre_img1.png`
      * `un_gato_cósmico_volando_sobre_img2.png`
      * ...etc.

-----

## 🚧 Manejo de Errores

El script incluye bloques `try...except` para manejar fallos comunes, como errores de conexión, errores de la API (`TogetherClientError`) o problemas durante la descarga (`requests.exceptions.RequestException`). En caso de fallo, se imprime un mensaje de error y el script intenta continuar con la siguiente imagen (si aplica).