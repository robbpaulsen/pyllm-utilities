"""
Funcionalidades core de Media-Stitcher

Implementa las 3 operaciones esenciales:
1. unir_archivos - Concatenar múltiples videos/audios
2. integrar_audio_a_video - Incrustar audio en video
3. ajustar_velocidad_audio - Cambiar velocidad sin alterar pitch
"""

import os
import tempfile
from pathlib import Path
from typing import List, Union, Optional

from .utils import (
    verificar_ffmpeg_disponible,
    validar_archivo_existe,
    validar_archivos_existen,
    ejecutar_ffmpeg,
    ejecutar_ffmpeg_con_progreso,
    obtener_directorio_salida,
    detectar_gpu_nvidia,
    GestorTemporales,
    logger
)


def unir_archivos(lista_paths: List[str], output_path: str,
                  safe_mode: bool = True, use_gpu: bool = False,
                  show_progress: bool = False) -> bool:
    """
    Concatena múltiples archivos de video o audio en secuencia.

    Esta es la función CRÍTICA del proyecto. Une intro + cuerpo + outro
    para generar el video final de YouTube.

    Args:
        lista_paths: Lista de rutas a archivos a unir (en orden)
        output_path: Ruta del archivo de salida
        safe_mode: Si True, usa concat demuxer (más rápido, requiere mismo formato).
                   Si False, usa concat filter (más lento, acepta formatos mixtos)
        use_gpu: Si True, intenta usar aceleración GPU NVIDIA (solo en safe_mode=False)
        show_progress: Si True, muestra barra de progreso con tqdm

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario

    Ejemplo:
        >>> unir_archivos(
        ...     ["intro.mp4", "cuerpo.mp4", "outro.mp4"],
        ...     "video_final.mp4"
        ... )
        True

        >>> # Con GPU y progreso
        >>> unir_archivos(
        ...     ["video1.mp4", "video2.mp4"],
        ...     "output.mp4",
        ...     safe_mode=False,
        ...     use_gpu=True,
        ...     show_progress=True
        ... )
        True
    """
    # Validaciones iniciales
    if not verificar_ffmpeg_disponible():
        return False

    if not lista_paths or len(lista_paths) < 2:
        logger.error("Se requieren al menos 2 archivos para unir")
        return False

    if not validar_archivos_existen(lista_paths):
        return False

    # Asegurar que el directorio de salida existe
    if not obtener_directorio_salida(output_path):
        return False

    # Método 1: concat demuxer (safe_mode=True)
    # Más rápido, sin re-encoding, pero requiere mismo formato/codec
    # GPU no se usa en demuxer (no hay encoding)
    if safe_mode:
        return _unir_con_concat_demuxer(lista_paths, output_path, show_progress)
    else:
        # Método 2: concat filter (safe_mode=False)
        # Más lento, re-encoding, pero acepta diferentes formatos
        # GPU se puede usar aquí
        return _unir_con_concat_filter(lista_paths, output_path, use_gpu, show_progress)


def _unir_con_concat_demuxer(lista_paths: List[str], output_path: str,
                             show_progress: bool = False) -> bool:
    """
    Une archivos usando concat demuxer (rápido, sin re-encoding).

    Crea un archivo temporal con la lista de archivos y usa el demuxer concat.
    Requiere que todos los archivos tengan el mismo formato/codec.
    """
    try:
        # Crear archivo temporal con lista de archivos
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                         delete=False, encoding='utf-8') as temp_file:
            for file_path in lista_paths:
                # FFmpeg requiere paths absolutos y escapados
                abs_path = Path(file_path).resolve()
                # Escapar caracteres especiales (principalmente ' en Windows)
                escaped_path = str(abs_path).replace("'", "'\\''")
                temp_file.write(f"file '{escaped_path}'\n")

            temp_file_path = temp_file.name

        logger.info(f"Uniendo {len(lista_paths)} archivos con concat demuxer")

        # Comando FFmpeg: -f concat -safe 0 -i lista.txt -c copy output
        args = [
            "-f", "concat",
            "-safe", "0",
            "-i", temp_file_path,
            "-c", "copy",  # Sin re-encoding
            "-y",  # Sobrescribir output si existe
            output_path
        ]

        # Ejecutar con o sin progreso
        ejecutor = ejecutar_ffmpeg_con_progreso if show_progress else ejecutar_ffmpeg
        resultado = ejecutor(args, f"Unir archivos -> {Path(output_path).name}")

        # Limpiar archivo temporal
        try:
            os.unlink(temp_file_path)
        except:
            pass

        return resultado

    except Exception as e:
        logger.error(f"Error en unir_archivos (demuxer): {e}")
        return False


def _unir_con_concat_filter(lista_paths: List[str], output_path: str,
                            use_gpu: bool = False, show_progress: bool = False) -> bool:
    """
    Une archivos usando concat filter (compatible con formatos mixtos).

    Re-encodifica el video, más lento pero más flexible.
    Puede usar GPU NVIDIA si está disponible.
    """
    try:
        logger.info(f"Uniendo {len(lista_paths)} archivos con concat filter")

        # Detectar GPU si se solicita
        gpu_info = detectar_gpu_nvidia() if use_gpu else {'disponible': False}
        usar_gpu = use_gpu and gpu_info['disponible']

        if usar_gpu:
            logger.info("Usando aceleración GPU NVIDIA para encoding")

        # Construir inputs con hwaccel si GPU está disponible
        inputs = []
        if usar_gpu and gpu_info.get('cuvid'):
            # Decoding acelerado
            for file_path in lista_paths:
                inputs.extend(["-hwaccel", "cuda", "-hwaccel_output_format", "cuda",
                              "-i", file_path])
        else:
            for file_path in lista_paths:
                inputs.extend(["-i", file_path])

        # Construir filtro concat
        # Ejemplo para 3 videos: [0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[outv][outa]
        n = len(lista_paths)
        filter_inputs = "".join([f"[{i}:v][{i}:a]" for i in range(n)])
        filter_spec = f"{filter_inputs}concat=n={n}:v=1:a=1[outv][outa]"

        args = inputs + [
            "-filter_complex", filter_spec,
            "-map", "[outv]",
            "-map", "[outa]",
        ]

        # Configurar encoder según GPU
        if usar_gpu and gpu_info.get('nvenc'):
            args.extend(["-c:v", "h264_nvenc", "-preset", "fast"])
        else:
            if usar_gpu:
                logger.warning("nvenc no disponible, usando encoder CPU")
            args.extend(["-c:v", "libx264", "-preset", "medium"])

        args.extend(["-y", output_path])

        # Ejecutar con o sin progreso
        ejecutor = ejecutar_ffmpeg_con_progreso if show_progress else ejecutar_ffmpeg
        return ejecutor(args, f"Unir archivos (filter) -> {Path(output_path).name}")

    except Exception as e:
        logger.error(f"Error en unir_archivos (filter): {e}")
        return False


def integrar_audio_a_video(video_path: str, audio_path: str,
                           output_path: str, reemplazar_audio: bool = True,
                           use_gpu: bool = False, show_progress: bool = False) -> bool:
    """
    Incrusta un archivo de audio en un video.

    Caso de uso típico: agregar audio TTS generado a un video de background
    o imagen estática.

    Args:
        video_path: Ruta al archivo de video (o imagen)
        audio_path: Ruta al archivo de audio a incrustar
        output_path: Ruta del archivo de salida
        reemplazar_audio: Si True, reemplaza audio existente.
                          Si False, mezcla con audio existente.
        use_gpu: Si True, intenta usar aceleración GPU NVIDIA
        show_progress: Si True, muestra barra de progreso con tqdm

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario

    Ejemplo:
        >>> integrar_audio_a_video(
        ...     "background.mp4",
        ...     "narration_tts.mp3",
        ...     "video_final.mp4"
        ... )
        True

        >>> # Con GPU y progreso
        >>> integrar_audio_a_video(
        ...     "background.mp4",
        ...     "audio.mp3",
        ...     "output.mp4",
        ...     use_gpu=True,
        ...     show_progress=True
        ... )
        True
    """
    # Validaciones
    if not verificar_ffmpeg_disponible():
        return False

    if not validar_archivo_existe(video_path):
        return False

    if not validar_archivo_existe(audio_path):
        return False

    if not obtener_directorio_salida(output_path):
        return False

    logger.info(f"Integrando audio '{Path(audio_path).name}' a video '{Path(video_path).name}'")

    # Detectar GPU si se solicita
    gpu_info = detectar_gpu_nvidia() if use_gpu else {'disponible': False}
    usar_gpu = use_gpu and gpu_info['disponible']

    if usar_gpu:
        logger.info("Usando aceleración GPU NVIDIA")

    # Comando básico con soporte GPU opcional
    args = []

    # Input de video con hwaccel si GPU disponible
    if usar_gpu and gpu_info.get('cuvid'):
        args.extend(["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"])

    args.extend(["-i", video_path, "-i", audio_path])

    # Configurar codec de video
    if usar_gpu and gpu_info.get('nvenc'):
        # Usar nvenc para encoding (solo si no estamos copiando)
        # En este caso, por defecto copiamos el video, pero si necesitamos
        # re-encoding (por incompatibilidad), usamos nvenc
        args.extend(["-c:v", "copy"])  # Intentar copiar primero
    else:
        args.extend(["-c:v", "copy"])  # Copiar video sin re-encoding

    args.extend(["-c:a", "aac"])  # Encodear audio a AAC (compatible)

    if reemplazar_audio:
        # Mapear solo video del input 0 y audio del input 1
        args.extend([
            "-map", "0:v:0",  # Video del primer input
            "-map", "1:a:0",  # Audio del segundo input
        ])
    else:
        # TODO: Implementar mezcla de audio (amerge filter)
        logger.warning("Mezcla de audio no implementada aún, reemplazando...")
        args.extend([
            "-map", "0:v:0",
            "-map", "1:a:0",
        ])

    # Ajustar duración del video a la del audio (shortest)
    args.extend([
        "-shortest",  # Terminar cuando el stream más corto termine
        "-y",
        output_path
    ])

    # Ejecutar con o sin progreso
    ejecutor = ejecutar_ffmpeg_con_progreso if show_progress else ejecutar_ffmpeg
    return ejecutor(args, f"Integrar audio -> {Path(output_path).name}")


def ajustar_velocidad_audio(audio_path: str, factor_velocidad: float,
                            output_path: str) -> bool:
    """
    Ajusta la velocidad de reproducción de un audio sin cambiar el pitch (tono).

    Usa el filtro 'atempo' de FFmpeg, que mantiene el tono original.

    Args:
        audio_path: Ruta al archivo de audio
        factor_velocidad: Factor de velocidad (0.5 = 50% velocidad, 2.0 = 200% velocidad)
                          Rango soportado: 0.5 - 100.0 (se encadena automáticamente)
        output_path: Ruta del archivo de salida

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario

    Ejemplo:
        >>> ajustar_velocidad_audio("audio.mp3", 1.25, "audio_rapido.mp3")
        True

    Notas:
        - atempo acepta factores entre 0.5 y 2.0 por instancia
        - Para factores mayores, se encadenan múltiples filtros atempo
        - Ejemplo: factor 4.0 = atempo=2.0,atempo=2.0
    """
    # Validaciones
    if not verificar_ffmpeg_disponible():
        return False

    if not validar_archivo_existe(audio_path):
        return False

    if factor_velocidad <= 0:
        logger.error(f"Factor de velocidad debe ser positivo (recibido: {factor_velocidad})")
        return False

    if factor_velocidad < 0.5 or factor_velocidad > 100.0:
        logger.warning(f"Factor de velocidad {factor_velocidad} está fuera del rango recomendado (0.5-100.0)")

    if not obtener_directorio_salida(output_path):
        return False

    logger.info(f"Ajustando velocidad de audio a {factor_velocidad}x")

    # Construir cadena de filtros atempo
    # atempo acepta solo valores entre 0.5 y 2.0
    filtros = _construir_filtros_atempo(factor_velocidad)

    if not filtros:
        logger.error("No se pudo construir filtros atempo válidos")
        return False

    # Comando FFmpeg: -i input -filter:a "atempo=X,atempo=Y" output
    args = [
        "-i", audio_path,
        "-filter:a", filtros,
        "-y",
        output_path
    ]

    return ejecutar_ffmpeg(args, f"Ajustar velocidad {factor_velocidad}x -> {Path(output_path).name}")


def _construir_filtros_atempo(factor: float) -> str:
    """
    Construye una cadena de filtros atempo para el factor deseado.

    atempo solo acepta valores entre 0.5 y 2.0, por lo que factores
    mayores requieren encadenar múltiples filtros.

    Args:
        factor: Factor de velocidad deseado

    Returns:
        str: Cadena de filtros (ej: "atempo=2.0,atempo=1.5")
    """
    if factor == 1.0:
        return "atempo=1.0"  # Sin cambios

    filtros = []
    factor_restante = factor

    # Para aceleración (factor > 1.0)
    if factor > 1.0:
        while factor_restante > 1.0:
            if factor_restante >= 2.0:
                filtros.append("atempo=2.0")
                factor_restante /= 2.0
            else:
                filtros.append(f"atempo={factor_restante:.2f}")
                factor_restante = 1.0

    # Para desaceleración (factor < 1.0)
    else:
        while factor_restante < 1.0:
            if factor_restante <= 0.5:
                filtros.append("atempo=0.5")
                factor_restante /= 0.5
            else:
                filtros.append(f"atempo={factor_restante:.2f}")
                factor_restante = 1.0

    return ",".join(filtros)


def recortar_segmento(input_path: str,
                     start_time: Union[str, float, int],
                     end_time: Optional[Union[str, float, int]],
                     output_path: str,
                     stream_copy: bool = True,
                     use_gpu: bool = False,
                     show_progress: bool = False) -> bool:
    """
    Recorta un segmento de video o audio especificando tiempo de inicio y fin.

    Args:
        input_path: Ruta al archivo de entrada
        start_time: Tiempo de inicio. Puede ser:
                    - String: "00:01:30" (HH:MM:SS)
                    - Número: 90 (segundos)
        end_time: Tiempo de fin (mismo formato que start_time).
                  Si None, corta hasta el final.
        output_path: Ruta del archivo de salida
        stream_copy: Si True, usa stream copy (rápido, sin re-encoding).
                     Si False, re-encodifica (más lento, más preciso).
        use_gpu: Si True, usa aceleración GPU para re-encoding (solo si stream_copy=False)
        show_progress: Si True, muestra barra de progreso

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario

    Ejemplo:
        >>> # Extraer segmento de 1:30 a 2:45
        >>> recortar_segmento("video.mp4", "00:01:30", "00:02:45", "clip.mp4")
        True

        >>> # Extraer desde 10 segundos hasta el final
        >>> recortar_segmento("video.mp4", 10, None, "sin_intro.mp4")
        True

        >>> # Extraer con re-encoding y GPU
        >>> recortar_segmento(
        ...     "video.mp4", 30, 120, "clip.mp4",
        ...     stream_copy=False, use_gpu=True
        ... )
        True
    """
    # Validaciones
    if not verificar_ffmpeg_disponible():
        return False

    if not validar_archivo_existe(input_path):
        return False

    if not obtener_directorio_salida(output_path):
        return False

    # Convertir tiempos a formato FFmpeg
    start = _convertir_tiempo(start_time)
    end = _convertir_tiempo(end_time) if end_time is not None else None

    logger.info(f"Recortando segmento: {start} -> {end if end else 'fin'}")

    # Detectar GPU si se solicita
    gpu_info = detectar_gpu_nvidia() if use_gpu and not stream_copy else {'disponible': False}
    usar_gpu = use_gpu and not stream_copy and gpu_info['disponible']

    if usar_gpu:
        logger.info("Usando aceleración GPU para re-encoding")

    # Construir comando FFmpeg
    args = []

    # Opciones de entrada
    if usar_gpu and gpu_info.get('cuvid'):
        args.extend(["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"])

    # Seek to start (más eficiente ponerlo antes de -i)
    args.extend(["-ss", str(start)])

    # Input
    args.extend(["-i", input_path])

    # End time (duración o tiempo absoluto)
    if end is not None:
        args.extend(["-to", str(end)])

    # Codec selection
    if stream_copy:
        # Stream copy (rápido, sin re-encoding)
        args.extend(["-c", "copy"])
    else:
        # Re-encoding
        if usar_gpu and gpu_info.get('nvenc'):
            args.extend(["-c:v", "h264_nvenc", "-preset", "fast"])
        else:
            args.extend(["-c:v", "libx264", "-preset", "medium"])

        args.extend(["-c:a", "aac"])

    # Opciones adicionales
    args.extend([
        "-avoid_negative_ts", "make_zero",  # Evitar problemas de timestamp
        "-y",
        output_path
    ])

    # Ejecutar con o sin progreso
    ejecutor = ejecutar_ffmpeg_con_progreso if show_progress else ejecutar_ffmpeg
    return ejecutor(args, f"Recortar segmento -> {Path(output_path).name}")


def _convertir_tiempo(tiempo: Union[str, float, int]) -> str:
    """
    Convierte tiempo a formato FFmpeg.

    Args:
        tiempo: Tiempo como string "HH:MM:SS" o número (segundos)

    Returns:
        str: Tiempo en formato FFmpeg

    Ejemplo:
        >>> _convertir_tiempo(90)
        '90'
        >>> _convertir_tiempo("00:01:30")
        '00:01:30'
    """
    if isinstance(tiempo, str):
        # Ya es string, asumimos formato correcto
        return tiempo
    else:
        # Número (segundos), FFmpeg acepta directamente
        return str(tiempo)
