# Creative Scripts

Coloca aquí tus guiones de texto que quieras convertir a audio.

## Formato

Los archivos deben ser texto plano (`.txt`) codificados en UTF-8.

## Ejemplo

Ver `ejemplo.txt` en este directorio para una plantilla básica.

## Consejos

- **Longitud:** Puedes usar desde frases cortas hasta documentos largos
- **Puntuación:** Usa puntos, comas y signos de exclamación para mejorar la entonación
- **Párrafos:** Separa ideas con saltos de línea para mejor ritmo
- **Idioma:** Chatterbox soporta múltiples idiomas, aunque la versión actual usa el modelo en inglés por defecto

## Uso

```bash
# Procesar un guion
uv run main.py --script creative-scripts/ejemplo.txt --output mi_audio.wav

# Con voz de referencia
uv run main.py --script creative-scripts/ejemplo.txt --voice audio-samples/mi_voz.wav --output mi_audio.wav
```
