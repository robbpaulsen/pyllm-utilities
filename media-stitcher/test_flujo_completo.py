"""
Script de prueba del flujo completo de producción de video
Simula el pipeline real para generar un video de YouTube
"""
import logging
from pathlib import Path
from media_stitcher import unir_archivos, integrar_audio_a_video, ajustar_velocidad_audio

# Configurar logging
logging.basicConfig(level=logging.INFO)

print("\n" + "="*70)
print("FLUJO COMPLETO DE PRODUCCIÓN - Pipeline de Video YouTube")
print("="*70)

# PASO 1: Ajustar velocidad del audio (acelerar narración)
print("\n→ PASO 1/3: Ajustando velocidad de audio (1.25x más rápido)")
print("-" * 70)

audio_acelerado = "video-samples/TEMP_audio_acelerado.mp3"
paso1 = ajustar_velocidad_audio(
    audio_path="video-samples/audio_original.mp3",
    factor_velocidad=1.25,
    output_path=audio_acelerado
)

if not paso1:
    print("✗ Error en paso 1 - Abortando")
    exit(1)
print("✓ Paso 1 completado")

# PASO 2: Integrar audio acelerado a video de background
print("\n→ PASO 2/3: Integrando audio acelerado a video de background")
print("-" * 70)

video_con_audio = "video-samples/TEMP_background_con_audio.mp4"
paso2 = integrar_audio_a_video(
    video_path="video-samples/background.mp4",
    audio_path=audio_acelerado,
    output_path=video_con_audio
)

if not paso2:
    print("✗ Error en paso 2 - Abortando")
    exit(1)
print("✓ Paso 2 completado")

# PASO 3: Unir intro + cuerpo con audio + outro
print("\n→ PASO 3/3: Uniendo intro + cuerpo + outro")
print("-" * 70)

video_final = "video-samples/FINAL_video_youtube.mp4"
paso3 = unir_archivos(
    lista_paths=[
        "video-samples/intro.mp4",
        video_con_audio,
        "video-samples/outro.mp4"
    ],
    output_path=video_final
)

if not paso3:
    print("✗ Error en paso 3 - Abortando")
    exit(1)
print("✓ Paso 3 completado")

# Resumen
print("\n" + "="*70)
print("✓✓✓ FLUJO COMPLETO EXITOSO ✓✓✓")
print("="*70)
print(f"\n📹 Video final generado: {video_final}")

# Mostrar info del video final
from pathlib import Path
tamaño = Path(video_final).stat().st_size / 1024 / 1024
print(f"   Tamaño: {tamaño:.2f} MB")

print("\nArchivos intermedios generados:")
print(f"   - {audio_acelerado}")
print(f"   - {video_con_audio}")

print("\n💡 Tip: Puedes eliminar los archivos TEMP_* si no los necesitas")
print("="*70 + "\n")
