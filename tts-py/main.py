#!/usr/bin/env python3
"""
TTS-py - Síntesis de Voz con Clonación Basada en Referencia

Utilidad CLI para generar audio a partir de texto usando Chatterbox TTS
con capacidad de clonación de voz mediante muestras de audio de referencia.

Uso:
    uv run main.py --text "Tu texto aquí" --output salida.wav
    uv run main.py --script creative-scripts/guion.txt --voice audio-samples/voz.wav --output salida.wav
    uv run main.py --help
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple
import torch
import torchaudio as ta
from tqdm import tqdm

# Fix 1: Deshabilitar XET para evitar errores de descarga
os.environ['HF_HUB_DISABLE_XET'] = '1'

# Fix 2: Parche para Perth watermarker
import perth
if perth.PerthImplicitWatermarker is None:
    perth.PerthImplicitWatermarker = perth.DummyWatermarker

from chatterbox.tts import ChatterboxTTS

# Directorio para cache de voces
VOICE_CACHE_DIR = Path.home() / ".cache" / "tts-py" / "voices"
VOICE_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def detectar_dispositivo() -> str:
    """
    Detecta el mejor dispositivo disponible para procesamiento.

    Returns:
        str: "cuda" si hay GPU NVIDIA, "cpu" en caso contrario

    Por qué existe:
        El modelo Chatterbox funciona mucho más rápido en GPU.
        Esta función detecta automáticamente el hardware disponible.
    """
    if torch.cuda.is_available():
        device = "cuda"
        gpu_name = torch.cuda.get_device_name(0)
        print(f"✓ Usando GPU: {gpu_name}")
    else:
        device = "cpu"
        print("⚠ Usando CPU (será más lento). Considera usar una GPU NVIDIA.")

    return device


def cargar_modelo(device: str) -> ChatterboxTTS:
    """
    Carga el modelo Chatterbox TTS desde HuggingFace.

    Args:
        device: Dispositivo a usar ("cuda" o "cpu")

    Returns:
        ChatterboxTTS: Modelo inicializado y listo para usar

    Por qué existe:
        Centraliza la lógica de carga del modelo para facilitar mantenimiento.
        La primera vez descargará ~2GB de modelos desde HuggingFace.
    """
    print("Cargando modelo Chatterbox TTS...")
    print("(Esto puede tardar la primera vez que descarga el modelo)")

    try:
        model = ChatterboxTTS.from_pretrained(device=device)
        print("✓ Modelo cargado exitosamente")
        return model
    except Exception as e:
        print(f"❌ Error al cargar el modelo: {e}")
        print("\nPosibles soluciones:")
        print("1. Verifica tu conexión a internet")
        print("2. Asegúrate de tener espacio en disco (~2GB)")
        print("3. Intenta de nuevo más tarde si HuggingFace tiene problemas")
        sys.exit(1)


def leer_texto_desde_archivo(ruta: Path) -> str:
    """
    Lee el contenido de un archivo de texto.

    Args:
        ruta: Ruta al archivo de texto

    Returns:
        str: Contenido del archivo

    Por qué existe:
        Permite procesar guiones largos desde archivos en lugar de CLI.
    """
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            texto = f.read().strip()

        if not texto:
            print(f"⚠ Advertencia: El archivo {ruta} está vacío")
            sys.exit(1)

        return texto
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {ruta}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        sys.exit(1)


def calcular_hash_audio(ruta_audio: Path) -> str:
    """
    Calcula un hash SHA256 del archivo de audio.

    Args:
        ruta_audio: Ruta al archivo de audio

    Returns:
        str: Hash hexadecimal del archivo

    Por qué existe:
        Identifica de forma única cada archivo de voz de referencia para el cache.
    """
    sha256 = hashlib.sha256()
    with open(ruta_audio, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]  # Primeros 16 caracteres son suficientes


def obtener_voz_desde_cache(ruta_audio: Path, voice_name: Optional[str] = None) -> Optional[Tuple[Path, dict]]:
    """
    Busca una voz procesada en el cache.

    Args:
        ruta_audio: Ruta al archivo de audio de referencia
        voice_name: Nombre opcional de la voz

    Returns:
        Tuple[Path, dict] si está en cache, None si no

    Por qué existe:
        Evita reprocesar el mismo audio de referencia múltiples veces.
        Mejora significativamente el rendimiento para voces usadas frecuentemente.
    """
    if voice_name:
        cache_file = VOICE_CACHE_DIR / f"{voice_name}.json"
    else:
        audio_hash = calcular_hash_audio(ruta_audio)
        cache_file = VOICE_CACHE_DIR / f"{audio_hash}.json"

    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            # Verificar que el archivo de audio original sigue existiendo y no cambió
            if Path(cache_data['original_path']).exists():
                current_hash = calcular_hash_audio(Path(cache_data['original_path']))
                if current_hash == cache_data['audio_hash']:
                    print(f"✓ Voz encontrada en cache: {cache_file.stem}")
                    return ruta_audio, cache_data
        except Exception:
            pass  # Si hay error leyendo cache, simplemente no lo usamos

    return None


def guardar_voz_en_cache(ruta_audio: Path, voice_name: Optional[str] = None):
    """
    Guarda información de una voz en el cache.

    Args:
        ruta_audio: Ruta al archivo de audio de referencia
        voice_name: Nombre opcional de la voz

    Por qué existe:
        Almacena metadata de voces procesadas para reutilización futura.
    """
    audio_hash = calcular_hash_audio(ruta_audio)

    if voice_name:
        cache_file = VOICE_CACHE_DIR / f"{voice_name}.json"
    else:
        cache_file = VOICE_CACHE_DIR / f"{audio_hash}.json"

    cache_data = {
        'original_path': str(ruta_audio.absolute()),
        'audio_hash': audio_hash,
        'cached_at': time.time(),
        'voice_name': voice_name
    }

    try:
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        print(f"✓ Voz guardada en cache: {cache_file.stem}")
    except Exception as e:
        # No es crítico si falla el cache
        print(f"⚠ No se pudo guardar en cache: {e}")


def generar_audio(
    modelo: ChatterboxTTS,
    texto: str,
    ruta_audio_referencia: Path | None = None,
    voice_name: Optional[str] = None,
) -> torch.Tensor:
    """
    Genera audio a partir de texto usando el modelo Chatterbox.

    Args:
        modelo: Modelo Chatterbox TTS cargado
        texto: Texto a sintetizar
        ruta_audio_referencia: Ruta opcional a audio de referencia para clonación
        voice_name: Nombre opcional para cachear la voz

    Returns:
        torch.Tensor: Audio generado como tensor

    Por qué existe:
        Encapsula la lógica de generación de audio, permitiendo uso con o sin
        referencia de voz, con soporte de cache.
    """
    print(f"\nGenerando audio...")
    print(f"Texto: '{texto[:100]}{'...' if len(texto) > 100 else ''}'")

    # Verificar cache si hay voz de referencia
    if ruta_audio_referencia:
        cache_result = obtener_voz_desde_cache(ruta_audio_referencia, voice_name)
        if cache_result:
            print("⚡ Usando voz desde cache (más rápido)")
        else:
            print(f"Procesando voz de referencia: {ruta_audio_referencia}")

    try:
        # Estimar duración basada en longitud del texto
        estimated_seconds = len(texto.split()) * 0.5  # ~0.5s por palabra

        print(f"⏳ Tiempo estimado: ~{int(estimated_seconds)}s")

        # Generar con barra de progreso
        with tqdm(total=100, desc="Generando", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
            start_time = time.time()

            if ruta_audio_referencia:
                wav = modelo.generate(texto, audio_prompt_path=str(ruta_audio_referencia))
                # Guardar en cache para próxima vez
                if not cache_result:
                    guardar_voz_en_cache(ruta_audio_referencia, voice_name)
            else:
                print("Usando voz por defecto (sin referencia)")
                wav = modelo.generate(texto)

            pbar.update(100)
            elapsed = time.time() - start_time

        print(f"✓ Audio generado en {elapsed:.1f}s")
        return wav

    except Exception as e:
        print(f"❌ Error durante la generación: {e}")
        sys.exit(1)


def guardar_audio(wav: torch.Tensor, ruta_salida: Path, sample_rate: int):
    """
    Guarda el audio generado en un archivo WAV.

    Args:
        wav: Tensor de audio
        ruta_salida: Ruta donde guardar el archivo
        sample_rate: Frecuencia de muestreo del audio

    Por qué existe:
        Centraliza la lógica de guardado de archivos con manejo de errores.
    """
    try:
        # Asegurar que el directorio de salida existe
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)

        # Guardar audio
        ta.save(str(ruta_salida), wav, sample_rate)
        print(f"✓ Audio guardado en: {ruta_salida}")

        # Mostrar información del archivo
        size_mb = ruta_salida.stat().st_size / (1024 * 1024)
        print(f"✓ Tamaño del archivo: {size_mb:.2f} MB")

    except Exception as e:
        print(f"❌ Error al guardar el audio: {e}")
        sys.exit(1)


def parsear_argumentos() -> argparse.Namespace:
    """
    Procesa los argumentos de línea de comandos.

    Returns:
        argparse.Namespace: Argumentos parseados

    Por qué existe:
        Define la interfaz CLI de la herramienta de forma clara y documentada.
    """
    parser = argparse.ArgumentParser(
        description="TTS-py - Síntesis de voz con clonación basada en referencia",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Generar audio de un texto simple
  uv run main.py --text "Hola mundo" --output salida.wav

  # Usar un guion desde archivo
  uv run main.py --script creative-scripts/mi_guion.txt --output salida.wav

  # Clonar una voz específica
  uv run main.py --text "Texto aquí" --voice audio-samples/mi_voz.wav --output salida.wav

  # Combinar guion y voz de referencia
  uv run main.py --script guion.txt --voice voz.wav --output salida.wav
        """
    )

    # Grupo de entrada de texto (mutuamente excluyentes)
    texto_group = parser.add_mutually_exclusive_group(required=True)
    texto_group.add_argument(
        "-t", "--text",
        type=str,
        help="Texto a sintetizar directamente desde la línea de comandos"
    )
    texto_group.add_argument(
        "-s", "--script",
        type=Path,
        help="Ruta a un archivo de texto con el guion a sintetizar"
    )

    # Voz de referencia (opcional)
    parser.add_argument(
        "-v", "--voice",
        type=Path,
        help="Ruta a archivo de audio de referencia para clonar la voz (WAV, MP3, FLAC)"
    )

    parser.add_argument(
        "--voice-name",
        type=str,
        help="Nombre para guardar la voz en cache (útil para reutilización)"
    )

    # Salida
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("output-dir/output.wav"),
        help="Ruta donde guardar el audio generado (default: output-dir/output.wav)"
    )

    # Opciones adicionales
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Forzar uso de CPU en lugar de GPU"
    )

    return parser.parse_args()


def main():
    """
    Función principal del programa.

    Por qué existe:
        Orquesta todo el flujo de trabajo: parsear args, cargar modelo,
        generar audio, y guardar resultado.
    """
    print("=" * 60)
    print("TTS-py - Text to Speech con Clonación de Voz")
    print("=" * 60)
    print()

    # Parsear argumentos
    args = parsear_argumentos()

    # Detectar dispositivo
    if args.cpu:
        device = "cpu"
        print("✓ Forzando uso de CPU (según parámetro --cpu)")
    else:
        device = detectar_dispositivo()

    # Cargar modelo
    modelo = cargar_modelo(device)

    # Obtener texto
    if args.script:
        texto = leer_texto_desde_archivo(args.script)
    else:
        texto = args.text

    # Validar audio de referencia si se proporcionó
    if args.voice and not args.voice.exists():
        print(f"❌ Error: No se encontró el archivo de audio de referencia: {args.voice}")
        sys.exit(1)

    # Validar que voice-name solo se use con --voice
    if args.voice_name and not args.voice:
        print("⚠ Advertencia: --voice-name solo funciona con --voice, se ignorará")
        args.voice_name = None

    # Generar audio
    wav = generar_audio(modelo, texto, args.voice, args.voice_name)

    # Guardar audio
    guardar_audio(wav, args.output, modelo.sr)

    print()
    print("=" * 60)
    print("✅ Proceso completado exitosamente")
    print("=" * 60)


if __name__ == "__main__":
    main()
