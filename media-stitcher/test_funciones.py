"""
Script de prueba para validar las 3 funciones core
"""
import logging
from media_stitcher import unir_archivos, integrar_audio_a_video, ajustar_velocidad_audio

# Configurar logging
logging.basicConfig(level=logging.INFO)

print("\n" + "="*70)
print("PRUEBA 1: unir_archivos() - Concatenar intro + cuerpo + outro")
print("="*70)

resultado1 = unir_archivos(
    lista_paths=[
        "video-samples/intro.mp4",
        "video-samples/cuerpo.mp4",
        "video-samples/outro.mp4"
    ],
    output_path="video-samples/TEST_video_completo.mp4",
    safe_mode=True
)

print(f"\nResultado: {'✓ ÉXITO' if resultado1 else '✗ FALLO'}")

print("\n" + "="*70)
print("PRUEBA 2: integrar_audio_a_video() - Agregar audio a video")
print("="*70)

resultado2 = integrar_audio_a_video(
    video_path="video-samples/background.mp4",
    audio_path="video-samples/narration.mp3",
    output_path="video-samples/TEST_video_con_audio.mp4",
    reemplazar_audio=True
)

print(f"\nResultado: {'✓ ÉXITO' if resultado2 else '✗ FALLO'}")

print("\n" + "="*70)
print("PRUEBA 3: ajustar_velocidad_audio() - Velocidad 1.5x")
print("="*70)

resultado3 = ajustar_velocidad_audio(
    audio_path="video-samples/audio_original.mp3",
    factor_velocidad=1.5,
    output_path="video-samples/TEST_audio_1.5x.mp3"
)

print(f"\nResultado: {'✓ ÉXITO' if resultado3 else '✗ FALLO'}")

print("\n" + "="*70)
print("RESUMEN DE PRUEBAS")
print("="*70)
print(f"1. unir_archivos():           {'✓' if resultado1 else '✗'}")
print(f"2. integrar_audio_a_video():  {'✓' if resultado2 else '✗'}")
print(f"3. ajustar_velocidad_audio(): {'✓' if resultado3 else '✗'}")
print(f"\nTotal: {sum([resultado1, resultado2, resultado3])}/3 pruebas exitosas")
print("="*70 + "\n")
