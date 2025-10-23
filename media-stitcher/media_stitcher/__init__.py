"""
Media-Stitcher: Wrapper de FFmpeg para post-producción de videos

Funciones principales:
- unir_archivos: Concatenar múltiples videos/audios
- integrar_audio_a_video: Incrustar audio en video
- ajustar_velocidad_audio: Cambiar velocidad sin alterar pitch
- recortar_segmento: Extraer segmento de video/audio por tiempo
"""

from .core import (
    unir_archivos,
    integrar_audio_a_video,
    ajustar_velocidad_audio,
    recortar_segmento
)

__version__ = "0.3.0"
__all__ = [
    "unir_archivos",
    "integrar_audio_a_video",
    "ajustar_velocidad_audio",
    "recortar_segmento"
]
