# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2025-10-19

### Cambiado
- **Refactorización Mayor de Funcionalidad:** Se reemplazó la extracción de texto basada en OCR con Tesseract por un enfoque de análisis multimodal utilizando el modelo Gemini 2.0 Flash de Google.
- El script ahora envía los archivos de video directamente a la API de Gemini para obtener un resumen completo del contenido, que luego se utiliza para generar los metadatos SEO.
- Este cambio elimina las dependencias de `pytesseract` y `opencv-python`.
- El nuevo método proporciona metadatos más ricos, con mayor contexto y evita los artefactos y errores relacionados con el OCR.

### Eliminado
- Se eliminaron `pytesseract` y `opencv-python` de las dependencias del proyecto.