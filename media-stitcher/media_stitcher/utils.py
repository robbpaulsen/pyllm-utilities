"""
Utilidades y helpers para Media-Stitcher
"""

import logging
import subprocess
import os
import re
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Callable
from contextlib import contextmanager

# Logger global (se configura con configurar_logging())
logger = logging.getLogger(__name__)

# Configuración por defecto
_logging_configurado = False


def configurar_logging(level: int = logging.INFO,
                      log_file: Optional[str] = None,
                      format_string: Optional[str] = None) -> None:
    """
    Configura el sistema de logging para Media-Stitcher.

    Por defecto, loguea a consola. Si se proporciona log_file, también
    loguea a archivo.

    Args:
        level: Nivel de logging (logging.INFO, logging.DEBUG, etc)
        log_file: Ruta al archivo de log (opcional). Si None, solo consola
        format_string: Formato personalizado de logs (opcional)

    Ejemplo:
        >>> configurar_logging(logging.DEBUG, "logs/media-stitcher.log")
        >>> # Logs irán a consola y a logs/media-stitcher.log
    """
    global _logging_configurado

    if _logging_configurado:
        logger.warning("Logging ya configurado, reconfigurando...")

    # Formato por defecto
    if format_string is None:
        format_string = '[%(levelname)s] %(message)s'

    # Obtener el root logger de media_stitcher
    root_logger = logging.getLogger('media_stitcher')
    root_logger.setLevel(level)

    # Limpiar handlers existentes
    root_logger.handlers.clear()

    # Handler para consola (siempre)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(format_string)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Handler para archivo (opcional)
    if log_file:
        try:
            # Crear directorio de logs si no existe
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)

            # Formato más detallado para archivo
            file_format = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
            file_formatter = logging.Formatter(file_format)
            file_handler.setFormatter(file_formatter)

            root_logger.addHandler(file_handler)

            root_logger.info(f"Logging configurado - Archivo: {log_file}")

        except Exception as e:
            root_logger.error(f"Error configurando log a archivo: {e}")

    _logging_configurado = True


# Configurar logging por defecto al importar
if not _logging_configurado:
    configurar_logging()


def verificar_ffmpeg_disponible() -> bool:
    """
    Verifica que FFmpeg esté instalado y disponible en el PATH.

    Returns:
        bool: True si FFmpeg está disponible, False en caso contrario
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if result.returncode == 0:
            logger.info("FFmpeg detectado correctamente")
            return True
        else:
            logger.error("FFmpeg no respondió correctamente")
            return False
    except FileNotFoundError:
        logger.error("FFmpeg no encontrado en PATH. Por favor instala FFmpeg.")
        return False
    except Exception as e:
        logger.error(f"Error verificando FFmpeg: {e}")
        return False


def validar_archivo_existe(file_path: str) -> bool:
    """
    Valida que un archivo exista en el sistema.

    Args:
        file_path: Ruta al archivo

    Returns:
        bool: True si existe, False en caso contrario
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Archivo no encontrado: {file_path}")
        return False
    if not path.is_file():
        logger.error(f"La ruta no es un archivo: {file_path}")
        return False
    return True


def validar_archivos_existen(file_paths: List[str]) -> bool:
    """
    Valida que todos los archivos en una lista existan.

    Args:
        file_paths: Lista de rutas a archivos

    Returns:
        bool: True si todos existen, False si alguno falta
    """
    for file_path in file_paths:
        if not validar_archivo_existe(file_path):
            return False
    return True


def ejecutar_ffmpeg(args: List[str], descripcion: str = "Operación FFmpeg") -> bool:
    """
    Ejecuta un comando de FFmpeg con los argumentos proporcionados.

    Args:
        args: Lista de argumentos para FFmpeg (sin incluir 'ffmpeg')
        descripcion: Descripción de la operación para logs

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    comando = ["ffmpeg"] + args

    logger.info(f"Iniciando: {descripcion}")
    logger.debug(f"Comando FFmpeg: {' '.join(comando)}")

    try:
        result = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300  # 5 minutos timeout
        )

        if result.returncode == 0:
            logger.info(f"✓ {descripcion} completada exitosamente")
            return True
        else:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            logger.error(f"✗ {descripcion} falló")
            logger.error(f"Error FFmpeg: {error_msg[-500:]}")  # Últimas 500 chars
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"✗ {descripcion} excedió el tiempo límite (5 min)")
        return False
    except Exception as e:
        logger.error(f"✗ Error ejecutando {descripcion}: {e}")
        return False


def obtener_directorio_salida(output_path: str) -> Optional[Path]:
    """
    Obtiene el directorio de salida y lo crea si no existe.

    Args:
        output_path: Ruta del archivo de salida

    Returns:
        Path: Objeto Path del directorio, o None si hay error
    """
    try:
        path = Path(output_path)
        directorio = path.parent

        if not directorio.exists():
            directorio.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio de salida creado: {directorio}")

        return directorio
    except Exception as e:
        logger.error(f"Error creando directorio de salida: {e}")
        return None


# ============================================================================
# SOPORTE GPU NVIDIA
# ============================================================================

_GPU_CACHE: Optional[Dict[str, bool]] = None


def detectar_gpu_nvidia() -> Dict[str, bool]:
    """
    Detecta si FFmpeg tiene soporte para aceleración GPU NVIDIA.

    Verifica la disponibilidad de:
    - nvenc (encoding acelerado H.264)
    - hevc_nvenc (encoding acelerado H.265/HEVC)
    - vp9_nvenc (encoding acelerado VP9)
    - cuvid (decoding acelerado)
    - CUDA filters (filtros acelerados)

    El resultado se cachea para evitar verificaciones repetidas.

    Returns:
        dict: {
            'disponible': bool,
            'nvenc': bool,          # H.264 nvenc
            'hevc_nvenc': bool,     # H.265/HEVC nvenc
            'vp9_nvenc': bool,      # VP9 nvenc
            'cuvid': bool,
            'cuda_filters': bool
        }
    """
    global _GPU_CACHE

    if _GPU_CACHE is not None:
        return _GPU_CACHE

    resultado = {
        'disponible': False,
        'nvenc': False,
        'hevc_nvenc': False,
        'vp9_nvenc': False,
        'cuvid': False,
        'cuda_filters': False
    }

    try:
        # Verificar encoders nvenc
        result_encoders = subprocess.run(
            ["ffmpeg", "-encoders"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )

        if result_encoders.returncode == 0:
            output = result_encoders.stdout.decode('utf-8', errors='ignore')
            if 'h264_nvenc' in output:
                resultado['nvenc'] = True
            if 'hevc_nvenc' in output or 'h265_nvenc' in output:
                resultado['hevc_nvenc'] = True
            if 'vp9_nvenc' in output:
                resultado['vp9_nvenc'] = True

        # Verificar decoders cuvid
        result_decoders = subprocess.run(
            ["ffmpeg", "-decoders"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )

        if result_decoders.returncode == 0:
            output = result_decoders.stdout.decode('utf-8', errors='ignore')
            if 'cuvid' in output or 'h264_cuvid' in output:
                resultado['cuvid'] = True

        # Verificar hwaccels
        result_hwaccels = subprocess.run(
            ["ffmpeg", "-hwaccels"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )

        if result_hwaccels.returncode == 0:
            output = result_hwaccels.stdout.decode('utf-8', errors='ignore')
            if 'cuda' in output:
                resultado['cuda_filters'] = True

        # GPU disponible si tiene al menos un encoder nvenc o cuvid
        resultado['disponible'] = (resultado['nvenc'] or resultado['hevc_nvenc'] or
                                   resultado['vp9_nvenc'] or resultado['cuvid'])

        if resultado['disponible']:
            codecs_disponibles = []
            if resultado['nvenc']:
                codecs_disponibles.append('H.264')
            if resultado['hevc_nvenc']:
                codecs_disponibles.append('HEVC')
            if resultado['vp9_nvenc']:
                codecs_disponibles.append('VP9')

            logger.info(f"GPU NVIDIA detectada - Codecs: {', '.join(codecs_disponibles)}, "
                       f"cuvid={resultado['cuvid']}, cuda={resultado['cuda_filters']}")
        else:
            logger.info("GPU NVIDIA no disponible o no soportada por FFmpeg")

    except Exception as e:
        logger.warning(f"Error detectando GPU: {e}")

    _GPU_CACHE = resultado
    return resultado


# ============================================================================
# PARSING DE PROGRESO CON TQDM
# ============================================================================

def ejecutar_ffmpeg_con_progreso(
    args: List[str],
    descripcion: str = "Operación FFmpeg",
    show_progress: bool = True,
    duracion_esperada: Optional[float] = None
) -> bool:
    """
    Ejecuta un comando de FFmpeg mostrando una barra de progreso.

    Parsea el stderr de FFmpeg para extraer información de progreso
    y mostrarla usando tqdm.

    Args:
        args: Lista de argumentos para FFmpeg (sin incluir 'ffmpeg')
        descripcion: Descripción de la operación para logs
        show_progress: Si True, muestra barra de progreso con tqdm
        duracion_esperada: Duración esperada en segundos (opcional, mejora precisión)

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    comando = ["ffmpeg"] + args

    logger.info(f"Iniciando: {descripcion}")
    logger.debug(f"Comando FFmpeg: {' '.join(comando)}")

    if not show_progress:
        # Fallback a ejecución sin progreso
        return ejecutar_ffmpeg(args, descripcion)

    try:
        from tqdm import tqdm

        # Iniciar proceso
        proceso = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # Configurar barra de progreso
        pbar = tqdm(
            total=100 if duracion_esperada is None else duracion_esperada,
            desc=descripcion,
            unit='%' if duracion_esperada is None else 's',
            ncols=80
        )

        # Patrón para parsear: time=00:01:23.45
        time_pattern = re.compile(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})')

        stderr_output = []

        # Leer stderr línea por línea
        for line in proceso.stderr:
            stderr_output.append(line)

            # Buscar información de tiempo
            match = time_pattern.search(line)
            if match:
                horas = int(match.group(1))
                minutos = int(match.group(2))
                segundos = float(match.group(3))
                tiempo_actual = horas * 3600 + minutos * 60 + segundos

                if duracion_esperada:
                    pbar.n = min(tiempo_actual, duracion_esperada)
                    pbar.refresh()
                else:
                    # Estimar porcentaje (sin duración conocida es menos preciso)
                    pbar.update(1)

        pbar.close()
        proceso.wait(timeout=300)

        if proceso.returncode == 0:
            logger.info(f"✓ {descripcion} completada exitosamente")
            return True
        else:
            error_msg = ''.join(stderr_output[-20:])  # Últimas 20 líneas
            logger.error(f"✗ {descripcion} falló")
            logger.error(f"Error FFmpeg: {error_msg[-500:]}")
            return False

    except ImportError:
        logger.warning("tqdm no disponible, ejecutando sin progreso")
        return ejecutar_ffmpeg(args, descripcion)
    except subprocess.TimeoutExpired:
        logger.error(f"✗ {descripcion} excedió el tiempo límite (5 min)")
        return False
    except Exception as e:
        logger.error(f"✗ Error ejecutando {descripcion}: {e}")
        return False


# ============================================================================
# GESTIÓN DE ARCHIVOS TEMPORALES
# ============================================================================

@contextmanager
def GestorTemporales(prefijo: str = "mediastitcher_", keep_on_error: bool = False):
    """
    Context manager para gestión automática de archivos temporales.

    Crea un directorio temporal que se limpia automáticamente al salir,
    a menos que ocurra un error y keep_on_error=True.

    Args:
        prefijo: Prefijo para el directorio temporal
        keep_on_error: Si True, mantiene archivos si hay excepción

    Yields:
        Path: Ruta al directorio temporal

    Ejemplo:
        >>> with GestorTemporales() as temp_dir:
        ...     temp_file = temp_dir / "archivo.txt"
        ...     temp_file.write_text("contenido")
        ...     # temp_dir se elimina automáticamente al salir
    """
    temp_dir = None
    error_ocurrido = False

    try:
        temp_dir = Path(tempfile.mkdtemp(prefix=prefijo))
        logger.debug(f"Directorio temporal creado: {temp_dir}")
        yield temp_dir

    except Exception as e:
        error_ocurrido = True
        logger.error(f"Error en operación con temporales: {e}")
        raise

    finally:
        if temp_dir and temp_dir.exists():
            if error_ocurrido and keep_on_error:
                logger.warning(f"Archivos temporales conservados (error): {temp_dir}")
            else:
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Directorio temporal eliminado: {temp_dir}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar directorio temporal: {e}")
