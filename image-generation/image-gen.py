"""
# Create Image

> Use an image model to generate an image for a given prompt.

## OpenAPI

````yaml POST /images/generations
paths:
  path: /images/generations
  method: post
  servers:
    - url: https://api.together.xyz/v1
  request:
    security:
      - title: bearerAuth
        parameters:
          query: {}
          header:
            Authorization:
              type: http
              scheme: bearer
              x-default: default
          cookie: {}
    parameters:
      path: {}
      query: {}
      header: {}
      cookie: {}
    body:
      application/json:
        schemaArray:
          - type: object
            properties:
              prompt:
                allOf:
                  - type: string
                    description: >-
                      A description of the desired images. Maximum length varies
                      by model.
                    example: cat floating in space, cinematic
              model:
                allOf:
                  - type: string
                    description: >
                      The model to use for image generation.<br> <br> [See all
                      of Together AI's image
                      models](https://docs.together.ai/docs/serverless-models#image-models)
                    example: black-forest-labs/FLUX.1-schnell
                    anyOf:
                      - type: string
                        enum:
                          - black-forest-labs/FLUX.1-schnell-Free
                          - black-forest-labs/FLUX.1-schnell
                          - black-forest-labs/FLUX.1.1-pro
                      - type: string
              steps:
                allOf:
                  - type: integer
                    default: 20
                    description: Number of generation steps.
              image_url:
                allOf:
                  - type: string
                    description: URL of an image to use for image models that support it.
              seed:
                allOf:
                  - type: integer
                    description: >-
                      Seed used for generation. Can be used to reproduce image
                      generations.
              'n':
                allOf:
                  - type: integer
                    default: 1
                    description: Number of image results to generate.
              height:
                allOf:
                  - type: integer
                    default: 1024
                    description: Height of the image to generate in number of pixels.
              width:
                allOf:
                  - type: integer
                    default: 1024
                    description: Width of the image to generate in number of pixels.
              negative_prompt:
                allOf:
                  - type: string
                    description: The prompt or prompts not to guide the image generation.
              response_format:
                allOf:
                  - type: string
                    description: >-
                      Format of the image response. Can be either a base64
                      string or a URL.
                    enum:
                      - base64
                      - url
              guidance_scale:
                allOf:
                  - type: number
                    description: >-
                      Adjusts the alignment of the generated image with the
                      input prompt. Higher values (e.g., 8-10) make the output
                      more faithful to the prompt, while lower values (e.g.,
                      1-5) encourage more creative freedom.
                    default: 3.5
              output_format:
                allOf:
                  - type: string
                    description: >-
                      The format of the image response. Can be either be `jpeg`
                      or `png`. Defaults to `jpeg`.
                    default: jpeg
                    enum:
                      - jpeg
                      - png
              image_loras:
                allOf:
                  - description: >-
                      An array of objects that define LoRAs (Low-Rank
                      Adaptations) to influence the generated image.
                    type: array
                    items:
                      type: object
                      required:
                        - path
                        - scale
                      properties:
                        path:
                          type: string
                          description: >-
                            The URL of the LoRA to apply (e.g.
                            https://huggingface.co/strangerzonehf/Flux-Midjourney-Mix2-LoRA).
                        scale:
                          type: number
                          description: >-
                            The strength of the LoRA's influence. Most LoRA's
                            recommend a value of 1.
              disable_safety_checker:
                allOf:
                  - type: boolean
                    description: If true, disables the safety checker for image generation.
            required: true
            requiredProperties:
              - prompt
              - model
        examples:
          example:
            value:
              prompt: cat floating in space, cinematic
              model: black-forest-labs/FLUX.1-schnell
              steps: 20
              image_url: <string>
              seed: 123
              'n': 1
              height: 1024
              width: 1024
              negative_prompt: <string>
              response_format: base64
              guidance_scale: 3.5
              output_format: jpeg
              image_loras:
                - path: <string>
                  scale: 123
              disable_safety_checker: true
    codeSamples:
      - label: Together AI SDK (Python)
        lang: Python
        source: |
          from together import Together
          import os

          client = Together(
              api_key=os.environ.get("TOGETHER_API_KEY"),
          )

          response = client.images.generate(
              model="black-forest-labs/FLUX.1-schnell",
              steps=4,
              prompt="A cartoon of an astronaut riding a horse on the moon",
          )

          print(response.data[0].url)
      - label: Together AI SDK (TypeScript)
        lang: TypeScript
        source: |
          import Together from "together-ai";

          const client = new Together({
            apiKey: process.env.TOGETHER_API_KEY,
          });

          const response = await client.images.create({
            model: "black-forest-labs/FLUX.1-schnell",
            prompt: "A cartoon of an astronaut riding a horse on the moon",
          });

          console.log(response.data[0].url);
      - label: Together AI SDK (JavaScript)
        lang: JavaScript
        source: |
          import Together from "together-ai";

          const client = new Together({
            apiKey: process.env.TOGETHER_API_KEY,
          });

          const response = await client.images.create({
            model: "black-forest-labs/FLUX.1-schnell",
            prompt: "A cartoon of an astronaut riding a horse on the moon",
          });

          console.log(response.data[0].url);
      - label: cURL
        lang: Shell
        source: |
          curl -X POST "https://api.together.xyz/v1/images/generations" \
               -H "Authorization: Bearer $TOGETHER_API_KEY" \
               -H "Content-Type: application/json" \
               -d '{
                 "model": "black-forest-labs/FLUX.1-schnell",
                 "prompt": "A cartoon of an astronaut riding a horse on the moon"
               }'
  response:
    '200':
      application/json:
        schemaArray:
          - type: object
            properties:
              id:
                allOf:
                  - type: string
              model:
                allOf:
                  - type: string
              object:
                allOf:
                  - enum:
                      - list
                    example: list
              data:
                allOf:
                  - type: array
                    items:
                      oneOf:
                        - $ref: '#/components/schemas/ImageResponseDataB64'
                        - $ref: '#/components/schemas/ImageResponseDataUrl'
                      discriminator:
                        propertyName: type
            refIdentifier: '#/components/schemas/ImageResponse'
            requiredProperties:
              - id
              - model
              - object
              - data
        examples:
          example:
            value:
              id: <string>
              model: <string>
              object: list
              data:
                - index: 123
                  b64_json: <string>
                  type: b64_json
        description: Image generated successfully
  deprecated: false
  type: path
components:
  schemas:
    ImageResponseDataB64:
      type: object
      required:
        - index
        - b64_json
        - type
      properties:
        index:
          type: integer
        b64_json:
          type: string
        type:
          type: string
          enum:
            - b64_json
    ImageResponseDataUrl:
      type: object
      required:
        - index
        - url
        - type
      properties:
        index:
          type: integer
        url:
          type: string
        type:
          type: string
          enum:
            - url

````
"""

import time
import os 
from pathlib import Path
import requests # Necesario para descargar la imagen de la URL
from together import Together

# --- 1. Configuración Hardcodeada y Constantes ---

API_KEY_TOGETHER = 'YOUR_API_KEY'
MODEL_NAME = "black-forest-labs/FLUX.1-schnell-Free" 
WIDTH = 1024
HEIGHT = 1024
STEPS = 4
NEGATIVE_PROMPT = 'worst quality, low quality, normal quality, lowres, low details, grayscale, bad photo, bad photography, watermark, signature, text font, username, error, logo, words, letters, digits, autograph, trademark, name:1.2, subtitle, deformed iris, deformed pupils, bad teeth, deformed teeth, deformed lips, poorly drawn fingers, fused fingers, extra fingers, worst hand, poorly drawn hands, poorly drawn body, bad anatomy, bad proportions, extra limbs, malformed, mutated, mutilated, deformities:1.3, morbid, ugly'
MAX_IMAGES = 4
DELAY_SECONDS = 12 

# --- CONFIGURACIÓN DE LA MEJORA DE CALIDAD Y RUTA DE DESCARGA ---

# Carpeta donde se guardarán todas las imágenes generadas
DESCARGA_FOLDER = "imagenes_generadas_flux" 

# --- 2. Función de Descarga ---

def descargar_imagen(url: str, prompt_base: str, index: int) -> str:
    """
    Descarga la imagen de la URL temporal a una carpeta local.

    Args:
        url: La URL temporal de la imagen generada.
        prompt_base: El prompt del usuario (para nombrar el archivo).
        index: El número de imagen en el lote (para evitar sobrescribir).

    Returns:
        La ruta completa del archivo descargado o una cadena vacía en caso de error.
    """
    # Crear la carpeta de descarga si no existe
    ruta_carpeta = Path(DESCARGA_FOLDER)
    ruta_carpeta.mkdir(exist_ok=True) 

    try:
        # 1. Realizar la petición HTTP para obtener el contenido de la imagen
        response = requests.get(url, stream=True)
        response.raise_for_status() # Lanza una excepción para códigos de error HTTP

        # 2. Crear un nombre de archivo limpio y único
        # Tomamos las primeras 5 palabras del prompt para el nombre
        nombre_base = "_".join(prompt_base.lower().split()[:5])
        
        # El nombre final incluye el prompt, el índice y la extensión.
        # Asumimos .png o .jpg;Together.ai a menudo genera PNG.
        nombre_archivo = f"{nombre_base}_img{index+1}.png" 
        ruta_archivo = ruta_carpeta / nombre_archivo

        # 3. Guardar el contenido binario de la imagen en el archivo local
        with open(ruta_archivo, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return str(ruta_archivo.resolve()) # Devuelve la ruta absoluta
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR al descargar la imagen de {url}: {e}")
        return ""
    except Exception as e:
        print(f"❌ ERROR inesperado al guardar el archivo: {e}")
        return ""


# --- 3. Inicialización del Cliente ---
try:
    client = Together(api_key=API_KEY_TOGETHER)
except Exception as e:
    print(f"❌ ERROR al inicializar el cliente de Together: {e}")
    exit()


# --- 4. Función Principal de la Utilidad ---

def generar_imagenes_flux():
    # ... (Se mantiene la impresión de inicio y la lógica de entrada del usuario)
    print("✨ Iniciando la utilidad de generación y descarga de imágenes FLUX.1-schnell-Free (Gratuito) ✨")
    print(f"Modelo: {MODEL_NAME}")
    print(f"Las imágenes se guardarán en la carpeta: './{DESCARGA_FOLDER}'")
    print("-" * 50)
    
    # 3.1 Solicitar Prompt
    user_prompt = input("🖼️ Introduce el 'prompt' para generar la imagen: ").strip()
    if not user_prompt:
        print("🛑 El prompt no puede estar vacío. ¡Inténtalo de nuevo!")
        return

    # 🚨 IMPLEMENTACIÓN DE LA TRIGGER WORD
    final_prompt = f"{user_prompt}" 

    # 3.2 Solicitar Número de Imágenes
    while True:
        try:
            num_images = int(input(f"🔢 ¿Cuántas imágenes quieres generar (1 a {MAX_IMAGES})?: ").strip())
            if 1 <= num_images <= MAX_IMAGES:
                break
            else:
                print(f"⚠️ Por favor, introduce un número entre 1 y {MAX_IMAGES}.")
        except ValueError:
            print("🚫 Entrada inválida. Por favor, introduce un número entero.")

    # 3.3 Bucle de Generación
    archivos_descargados = [] # Lista para guardar las rutas locales
    for i in range(num_images):
        print(f"\n⏳ Generando imagen {i + 1} de {num_images}...")

        try:
            response = client.images.generate(
                model=MODEL_NAME,
                width=WIDTH,
                height=HEIGHT,
                steps=STEPS,
                prompt=final_prompt,
                negative_prompt=NEGATIVE_PROMPT
            )

            if response.data and len(response.data) > 0:
                url_imagen = response.data[0].url
                print(f"✅ Imagen {i + 1} generada en URL temporal.")

                # 🚀 NUEVO PASO: Descargar la imagen
                ruta_descarga = descargar_imagen(url_imagen, user_prompt, i)
                
                if ruta_descarga:
                    archivos_descargados.append(ruta_descarga)
                    print(f"💾 Imagen {i + 1} descargada y guardada en: {ruta_descarga}")
                else:
                    print(f"⚠️ No se pudo descargar la imagen {i + 1}.")

            else:
                print(f"❌ La respuesta de la API para la imagen {i + 1} no contiene datos de imagen.")

        except TogetherClientError as e:
            print(f"🚨 ERROR de la API de Together en la imagen {i + 1}: {e}")
        except Exception as e:
            print(f"🚨 Ocurrió un error inesperado en la imagen {i + 1}: {e}")

        # Aplicar la Limitante de Tiempo
        if i < num_images - 1:
            print(f"😴 Esperando {DELAY_SECONDS} segundos antes de la siguiente petición (limitante requerida)...")
            time.sleep(DELAY_SECONDS)

    # 3.4 Resultados Finales
    print("\n" + "=" * 50)
    print("🎉 Proceso de Generación y Descarga Terminado 🎉")
    print(f"Se descargaron {len(archivos_descargados)} archivo(s):")
    for j, ruta in enumerate(archivos_descargados):
        print(f"[{j + 1}] {ruta}")
    print("=" * 50)

# --- 5. Ejecución de la Utilidad ---
if __name__ == "__main__":
    generar_imagenes_flux()
