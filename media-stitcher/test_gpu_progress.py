"""
Demo rápido de GPU y progress bars
"""

from media_stitcher import unir_archivos, integrar_audio_a_video
from media_stitcher.utils import detectar_gpu_nvidia

print("\n" + "="*70)
print("DEMO: GPU Y PROGRESS BARS")
print("="*70)

# Detectar GPU
print("\n→ Detectando GPU NVIDIA...")
gpu_info = detectar_gpu_nvidia()
print(f"   GPU disponible: {gpu_info['disponible']}")
print(f"   nvenc: {gpu_info['nvenc']}")
print(f"   cuvid: {gpu_info['cuvid']}")
print(f"   cuda_filters: {gpu_info['cuda_filters']}")

# Test 1: Unir con GPU y progress
print("\n→ Test 1: Unir videos con GPU y progress bar")
print("-" * 70)

resultado1 = unir_archivos(
    lista_paths=[
        "video-samples/intro.mp4",
        "video-samples/cuerpo.mp4"
    ],
    output_path="video-samples/DEMO_union_gpu.mp4",
    safe_mode=False,  # Necesario para GPU
    use_gpu=True,
    show_progress=True
)

print(f"   Resultado: {'✓ ÉXITO' if resultado1 else '✗ FALLO'}")

# Test 2: Integrar audio con progress
print("\n→ Test 2: Integrar audio con progress bar")
print("-" * 70)

resultado2 = integrar_audio_a_video(
    video_path="video-samples/background.mp4",
    audio_path="video-samples/narration.mp3",
    output_path="video-samples/DEMO_audio_progress.mp4",
    use_gpu=gpu_info['disponible'],  # Usar GPU si está disponible
    show_progress=True
)

print(f"   Resultado: {'✓ ÉXITO' if resultado2 else '✗ FALLO'}")

print("\n" + "="*70)
print("DEMO COMPLETADO")
print("="*70 + "\n")
