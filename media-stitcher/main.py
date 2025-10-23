"""
Script de ejemplo para Media-Stitcher

Demuestra el uso de las 3 funciones core:
1. unir_archivos
2. integrar_audio_a_video
3. ajustar_velocidad_audio

Asegúrate de tener archivos de prueba en la carpeta 'video-samples/'
"""

import logging
from pathlib import Path
from media_stitcher import unir_archivos, integrar_audio_a_video, ajustar_velocidad_audio

# Configurar logging para ver el progreso
logging.basicConfig(level=logging.INFO)


def ejemplo_unir_videos():
    """
    Ejemplo: Unir intro + cuerpo + outro en un video final.

    Caso de uso: Pipeline de generación de videos de YouTube
    """
    print("\n" + "=" * 60)
    print("EJEMPLO 1: Unir múltiples videos")
    print("=" * 60)

    # Archivos de entrada (ajusta las rutas según tus archivos)
    archivos = [
        "video-samples/intro.mp4",
        "video-samples/cuerpo.mp4",
        "video-samples/outro.mp4"
    ]

    output = "video-samples/output_video_completo.mp4"

    # Verificar que los archivos existen
    archivos_faltantes = [f for f in archivos if not Path(f).exists()]
    if archivos_faltantes:
        print(f"\n⚠️  Archivos faltantes: {archivos_faltantes}")
        print("   Crea archivos de prueba en la carpeta 'video-samples/' o ajusta las rutas")
        return False

    # Unir con concat demuxer (rápido, sin re-encoding)
    resultado = unir_archivos(
        lista_paths=archivos,
        output_path=output,
        safe_mode=True  # Requiere mismo formato/codec
    )

    if resultado:
        print(f"\n✓ Video unido exitosamente: {output}")
    else:
        print("\n✗ Error al unir videos")
        print("   Si los videos tienen formatos diferentes, intenta con safe_mode=False")

    return resultado


def ejemplo_integrar_audio():
    """
    Ejemplo: Agregar audio TTS a un video de background.

    Caso de uso: Incrustar narración generada en video de fondo
    """
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Integrar audio a video")
    print("=" * 60)

    video = "video-samples/background.mp4"
    audio = "video-samples/narration.mp3"
    output = "video-samples/output_video_con_audio.mp4"

    # Verificar archivos
    if not Path(video).exists():
        print(f"\n⚠️  Video no encontrado: {video}")
        return False

    if not Path(audio).exists():
        print(f"\n⚠️  Audio no encontrado: {audio}")
        return False

    # Integrar audio
    resultado = integrar_audio_a_video(
        video_path=video,
        audio_path=audio,
        output_path=output,
        reemplazar_audio=True  # Reemplaza audio existente del video
    )

    if resultado:
        print(f"\n✓ Audio integrado exitosamente: {output}")
    else:
        print("\n✗ Error al integrar audio")

    return resultado


def ejemplo_ajustar_velocidad():
    """
    Ejemplo: Acelerar audio para reducir duración del video.

    Caso de uso: Ajustar guiones largos sin cambiar el tono de voz
    """
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Ajustar velocidad de audio")
    print("=" * 60)

    audio = "video-samples/audio_original.mp3"

    # Verificar archivo
    if not Path(audio).exists():
        print(f"\n⚠️  Audio no encontrado: {audio}")
        print("   Ajusta la ruta o crea un archivo de prueba")
        return False

    # Probar diferentes velocidades
    velocidades = [
        (0.75, "video-samples/output_audio_lento.mp3"),     # 75% - más lento
        (1.25, "video-samples/output_audio_rapido.mp3"),    # 125% - más rápido
        (1.5, "video-samples/output_audio_muy_rapido.mp3")  # 150% - mucho más rápido
    ]

    resultados = []

    for factor, output in velocidades:
        print(f"\n→ Ajustando velocidad a {factor}x...")
        resultado = ajustar_velocidad_audio(
            audio_path=audio,
            factor_velocidad=factor,
            output_path=output
        )
        resultados.append(resultado)

        if resultado:
            print(f"  ✓ Creado: {output}")
        else:
            print(f"  ✗ Error al crear {output}")

    if all(resultados):
        print(f"\n✓ Todas las variantes de velocidad creadas exitosamente")
        return True
    else:
        print(f"\n⚠️  Algunas variantes fallaron")
        return False


def ejemplo_flujo_completo():
    """
    Ejemplo de flujo completo para un video de YouTube:

    1. Acelerar audio narrado (si es muy largo)
    2. Integrar audio acelerado a video de background
    3. Unir intro + video con audio + outro
    """
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Flujo completo de producción")
    print("=" * 60)

    # Archivos necesarios
    archivos_necesarios = [
        "video-samples/intro.mp4",
        "video-samples/background.mp4",
        "video-samples/outro.mp4",
        "video-samples/narration_original.mp3"
    ]

    faltantes = [f for f in archivos_necesarios if not Path(f).exists()]
    if faltantes:
        print(f"\n⚠️  Este ejemplo requiere los siguientes archivos:")
        for archivo in archivos_necesarios:
            estado = "✓" if Path(archivo).exists() else "✗"
            print(f"   {estado} {archivo}")
        print("\n   Crea los archivos de prueba o ajusta las rutas")
        return False

    # Paso 1: Ajustar velocidad del audio (125% para reducir duración)
    print("\n→ Paso 1: Ajustando velocidad de audio...")
    audio_acelerado = "video-samples/temp_narration_rapido.mp3"

    if not ajustar_velocidad_audio(
        "video-samples/narration_original.mp3",
        1.25,
        audio_acelerado
    ):
        print("✗ Error en paso 1")
        return False

    # Paso 2: Integrar audio a background
    print("\n→ Paso 2: Integrando audio a video de background...")
    video_con_audio = "video-samples/temp_background_con_audio.mp4"

    if not integrar_audio_a_video(
        "video-samples/background.mp4",
        audio_acelerado,
        video_con_audio
    ):
        print("✗ Error en paso 2")
        return False

    # Paso 3: Unir intro + cuerpo + outro
    print("\n→ Paso 3: Uniendo segmentos finales...")
    video_final = "video-samples/output_video_youtube_final.mp4"

    if not unir_archivos(
        [
            "video-samples/intro.mp4",
            video_con_audio,
            "video-samples/outro.mp4"
        ],
        video_final
    ):
        print("✗ Error en paso 3")
        return False

    print("\n" + "=" * 60)
    print(f"✓ FLUJO COMPLETO EXITOSO")
    print(f"✓ Video final: {video_final}")
    print("=" * 60)

    # Opcional: Limpiar archivos temporales
    # Path(audio_acelerado).unlink(missing_ok=True)
    # Path(video_con_audio).unlink(missing_ok=True)

    return True


def main():
    """
    Ejecuta los ejemplos de uso.

    Descomenta los ejemplos que quieras probar.
    """
    print("\n" + "=" * 60)
    print("MEDIA-STITCHER - Ejemplos de Uso")
    print("=" * 60)

    # Crear carpeta de samples si no existe
    Path("video-samples").mkdir(exist_ok=True)
    print(f"\n📁 Carpeta de muestras: video-samples/")
    print("   (Coloca aquí tus archivos de prueba)\n")

    # Descomentar los ejemplos que quieras ejecutar:

    # ejemplo_unir_videos()
    # ejemplo_integrar_audio()
    # ejemplo_ajustar_velocidad()
    # ejemplo_flujo_completo()

    print("\n💡 Tip: Descomenta los ejemplos en main() para ejecutarlos")
    print("   O importa las funciones en tu propio script:\n")
    print("   from media_stitcher import unir_archivos, integrar_audio_a_video, ajustar_velocidad_audio")
    print()


if __name__ == "__main__":
    main()
