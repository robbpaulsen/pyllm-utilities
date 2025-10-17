# Pyllm Utilities

> [!NOTE]
>
> Se pronuncia:
> _Paeei~yyllmm_
>

Es un set de utilidades que integran grandes modelos de lenguaje como palanca u apoyo para 
realizar tareas cotidianas. Al menos cotidianas para mi.

## Image Generation

Utilidad que integra la api gratuita de [Together AI](https://together.ai),
esta API permite a usuarios registrados en la plataoforma usar el modelo
[FLUX.1\[schnell\]](https://www.together.ai/models/flux-1-schnell) para generar
imagenes de un tamaxo maximo de 1024x1024 en base a un prompt de texto, tiene 
un RLM (Rate Limit) de 6 imagenes maximo por minuto, mas peticiones que eso 
se impodrian limitaciones al cliente por 15 minutos. La utilidad es interactiva
y su uso es auto explanatorio y guiado por prompts al usuario.

### Datos de FLUX.1 Schnell

Creado por los desarolladores y equipo de investigacion de "Black Forest Labs",
este modelo es una interacion de su modelo original "FLUX" con el enfoque 
en rapidez y balance de calidad de imagenes. Es un modelo del tipo `SOTA` o 
mejor conocidos como "Jack of All Trades" en espanol la mejor traduccion es
"El Caballo de Batalla".

* `SAMPLE CODE:`
    ```python
    from together import Together

    client = Together()

    imageCompletion = client.images.generate(
        model="black-forest-labs/FLUX.1-schnell-Free",
        width=1024,
        height=1024,
        steps=4,
        prompt="Draw an anime style version of this image.",
        image_url="https://huggingface.co/datasets/patrickvonplaten/random_img/resolve/main/yosemite.png",
    )

    print(imageCompletion.data[0].url)
    ```

###### Aqui hay que recalcar que esta linea `client = Together()` esta declarando que asume que el valor de la llave
si este no es el caso se tendria que declarar en la forma `client = Together(api_key="YOUR_API_KEY")` :

    ```python
    from together import Together
    
    client = Together(api_key="YOUR_API_KEY")

    imageCompletion = client.images.generate(
        model="black-forest-labs/FLUX.1-schnell-Free",
        width=1024,
        height=768,
        steps=4,
        prompt="Draw an anime style version of this image.",
        image_url="https://huggingface.co/datasets/patrickvonplaten/random_img/resolve/main/yosemite.png",
    )

    print(imageCompletion.data[0].url)
    ```

