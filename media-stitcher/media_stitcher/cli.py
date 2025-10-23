"""
CLI para Media-Stitcher

Interfaz de línea de comandos para las funciones de Media-Stitcher.
"""

import argparse
import sys
import logging
from pathlib import Path

from .core import (
    unir_archivos,
    integrar_audio_a_video,
    ajustar_velocidad_audio,
    recortar_segmento
)
from .utils import configurar_logging, detectar_gpu_nvidia


def cmd_unir(args):
    """Comando: unir archivos"""
    resultado = unir_archivos(
        lista_paths=args.inputs,
        output_path=args.output,
        safe_mode=not args.filter_mode,
        use_gpu=args.gpu,
        show_progress=args.progress
    )

    if resultado:
        print(f"✓ Archivos unidos exitosamente: {args.output}")
        return 0
    else:
        print("✗ Error al unir archivos", file=sys.stderr)
        return 1


def cmd_integrar(args):
    """Comando: integrar audio a video"""
    resultado = integrar_audio_a_video(
        video_path=args.video,
        audio_path=args.audio,
        output_path=args.output,
        reemplazar_audio=not args.mezclar,
        use_gpu=args.gpu,
        show_progress=args.progress
    )

    if resultado:
        print(f"✓ Audio integrado exitosamente: {args.output}")
        return 0
    else:
        print("✗ Error al integrar audio", file=sys.stderr)
        return 1


def cmd_ajustar(args):
    """Comando: ajustar velocidad de audio"""
    resultado = ajustar_velocidad_audio(
        audio_path=args.input,
        factor_velocidad=args.factor,
        output_path=args.output
    )

    if resultado:
        print(f"✓ Velocidad ajustada exitosamente: {args.output}")
        return 0
    else:
        print("✗ Error al ajustar velocidad", file=sys.stderr)
        return 1


def cmd_recortar(args):
    """Comando: recortar segmento"""
    resultado = recortar_segmento(
        input_path=args.input,
        start_time=args.start,
        end_time=args.end,
        output_path=args.output,
        stream_copy=not args.reencode,
        use_gpu=args.gpu,
        show_progress=args.progress
    )

    if resultado:
        print(f"✓ Segmento recortado exitosamente: {args.output}")
        return 0
    else:
        print("✗ Error al recortar segmento", file=sys.stderr)
        return 1


def cmd_info(args):
    """Comando: mostrar información del sistema"""
    print("="*60)
    print("MEDIA-STITCHER - Información del Sistema")
    print("="*60)

    # Información de GPU
    print("\n→ GPU NVIDIA:")
    gpu_info = detectar_gpu_nvidia()

    if gpu_info['disponible']:
        print("   ✓ GPU disponible")
        codecs = []
        if gpu_info['nvenc']:
            codecs.append('H.264')
        if gpu_info.get('hevc_nvenc'):
            codecs.append('HEVC/H.265')
        if gpu_info.get('vp9_nvenc'):
            codecs.append('VP9')

        print(f"   Codecs: {', '.join(codecs)}")
        print(f"   cuvid (decoding): {gpu_info['cuvid']}")
        print(f"   CUDA filters: {gpu_info['cuda_filters']}")
    else:
        print("   ✗ GPU no disponible")

    print("\n" + "="*60 + "\n")
    return 0


def main():
    """Punto de entrada principal de la CLI"""
    parser = argparse.ArgumentParser(
        prog='media-stitcher',
        description='Wrapper de FFmpeg para post-producción de videos',
        epilog='Ejemplos: media-stitcher unir intro.mp4 cuerpo.mp4 -o final.mp4 --gpu'
    )

    # Argumentos globales
    parser.add_argument(
        '--version',
        action='version',
        version='media-stitcher 0.3.0'
    )

    parser.add_argument(
        '--log-file',
        type=str,
        metavar='FILE',
        help='Guardar logs en archivo (además de consola)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo verbose (DEBUG logging)'
    )

    # Subcomandos
    subparsers = parser.add_subparsers(
        title='comandos',
        description='Operaciones disponibles',
        dest='command',
        required=True
    )

    # ========================================================================
    # Comando: unir
    # ========================================================================
    parser_unir = subparsers.add_parser(
        'unir',
        help='Unir múltiples archivos de video/audio',
        description='Concatena múltiples archivos en secuencia'
    )

    parser_unir.add_argument(
        'inputs',
        nargs='+',
        metavar='INPUT',
        help='Archivos a unir (en orden)'
    )

    parser_unir.add_argument(
        '-o', '--output',
        required=True,
        metavar='FILE',
        help='Archivo de salida'
    )

    parser_unir.add_argument(
        '-f', '--filter-mode',
        action='store_true',
        help='Usar concat filter (acepta formatos diferentes, más lento)'
    )

    parser_unir.add_argument(
        '-g', '--gpu',
        action='store_true',
        help='Usar aceleración GPU NVIDIA'
    )

    parser_unir.add_argument(
        '-p', '--progress',
        action='store_true',
        help='Mostrar barra de progreso'
    )

    parser_unir.set_defaults(func=cmd_unir)

    # ========================================================================
    # Comando: integrar
    # ========================================================================
    parser_integrar = subparsers.add_parser(
        'integrar',
        help='Integrar audio a video',
        description='Incrusta un archivo de audio en un video'
    )

    parser_integrar.add_argument(
        'video',
        metavar='VIDEO',
        help='Archivo de video'
    )

    parser_integrar.add_argument(
        'audio',
        metavar='AUDIO',
        help='Archivo de audio'
    )

    parser_integrar.add_argument(
        '-o', '--output',
        required=True,
        metavar='FILE',
        help='Archivo de salida'
    )

    parser_integrar.add_argument(
        '-m', '--mezclar',
        action='store_true',
        help='Mezclar con audio existente (en lugar de reemplazar)'
    )

    parser_integrar.add_argument(
        '-g', '--gpu',
        action='store_true',
        help='Usar aceleración GPU NVIDIA'
    )

    parser_integrar.add_argument(
        '-p', '--progress',
        action='store_true',
        help='Mostrar barra de progreso'
    )

    parser_integrar.set_defaults(func=cmd_integrar)

    # ========================================================================
    # Comando: ajustar
    # ========================================================================
    parser_ajustar = subparsers.add_parser(
        'ajustar',
        help='Ajustar velocidad de audio',
        description='Cambia la velocidad sin alterar el pitch'
    )

    parser_ajustar.add_argument(
        'input',
        metavar='AUDIO',
        help='Archivo de audio'
    )

    parser_ajustar.add_argument(
        'factor',
        type=float,
        metavar='FACTOR',
        help='Factor de velocidad (ej: 1.5 = 50%% más rápido)'
    )

    parser_ajustar.add_argument(
        '-o', '--output',
        required=True,
        metavar='FILE',
        help='Archivo de salida'
    )

    parser_ajustar.set_defaults(func=cmd_ajustar)

    # ========================================================================
    # Comando: recortar
    # ========================================================================
    parser_recortar = subparsers.add_parser(
        'recortar',
        help='Recortar segmento de video/audio',
        description='Extrae un segmento especificando tiempo de inicio y fin'
    )

    parser_recortar.add_argument(
        'input',
        metavar='INPUT',
        help='Archivo de entrada'
    )

    parser_recortar.add_argument(
        'start',
        metavar='START',
        help='Tiempo de inicio (ej: 00:01:30 o 90)'
    )

    parser_recortar.add_argument(
        'end',
        nargs='?',
        metavar='END',
        default=None,
        help='Tiempo de fin (opcional, si omite corta hasta el final)'
    )

    parser_recortar.add_argument(
        '-o', '--output',
        required=True,
        metavar='FILE',
        help='Archivo de salida'
    )

    parser_recortar.add_argument(
        '-r', '--reencode',
        action='store_true',
        help='Re-encodificar (más lento, más preciso)'
    )

    parser_recortar.add_argument(
        '-g', '--gpu',
        action='store_true',
        help='Usar aceleración GPU NVIDIA (solo con --reencode)'
    )

    parser_recortar.add_argument(
        '-p', '--progress',
        action='store_true',
        help='Mostrar barra de progreso'
    )

    parser_recortar.set_defaults(func=cmd_recortar)

    # ========================================================================
    # Comando: info
    # ========================================================================
    parser_info = subparsers.add_parser(
        'info',
        help='Mostrar información del sistema',
        description='Muestra capacidades GPU y configuración'
    )

    parser_info.set_defaults(func=cmd_info)

    # ========================================================================
    # Parsear argumentos y ejecutar
    # ========================================================================
    args = parser.parse_args()

    # Configurar logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    configurar_logging(level=log_level, log_file=args.log_file if hasattr(args, 'log_file') and args.log_file else None)

    # Ejecutar comando
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrumpido por usuario", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
