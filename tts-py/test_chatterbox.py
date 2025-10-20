#!/usr/bin/env python3
"""
Script de prueba para verificar la instalación de Chatterbox TTS.

Este script prueba:
1. Importación de bibliotecas necesarias
2. Detección de GPU CUDA
3. Carga del modelo Chatterbox
4. Generación de audio de prueba básico

Uso:
    python test_chatterbox.py
"""

import torch
import sys
from pathlib import Path


def verificar_entorno():
    """Verifica que el entorno esté configurado correctamente."""
    print("=" * 60)
    print("VERIFICACIÓN DEL ENTORNO")
    print("=" * 60)

    print(f"\n✓ Python version: {sys.version}")
    print(f"✓ PyTorch version: {torch.__version__}")
    print(f"✓ CUDA disponible: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"✓ CUDA version: {torch.version.cuda}")
        print(f"✓ GPU count: {torch.cuda.device_count()}")
        print(f"✓ GPU name: {torch.cuda.get_device_name(0)}")
        print(f"✓ GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("⚠ WARNING: CUDA no disponible, se usará CPU (será más lento)")

    print()


def probar_chatterbox():
    """Prueba la importación y carga básica de Chatterbox."""
    print("=" * 60)
    print("PROBANDO CHATTERBOX TTS")
    print("=" * 60)

    try:
        print("\n[1/3] Importando Chatterbox...")
        from chatterbox import ChatterboxTTS
        print("✓ Chatterbox importado correctamente")

        print("\n[2/3] Inicializando modelo...")
        print("(Esto puede tardar la primera vez que descarga el modelo)")

        # Determinar dispositivo
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"✓ Usando dispositivo: {device}")

        # Inicializar modelo usando from_pretrained
        tts = ChatterboxTTS.from_pretrained(device=device)
        print("✓ Modelo Chatterbox inicializado correctamente")

        print("\n[3/3] Generando audio de prueba...")
        # Texto de prueba simple
        texto_prueba = "Hola, esto es una prueba de síntesis de voz con Chatterbox."

        # Generar audio (sin referencia por ahora, usará voz default)
        output_path = Path("output-dir") / "test_output.wav"
        output_path.parent.mkdir(exist_ok=True)

        print(f"✓ Generando: '{texto_prueba}'")
        print(f"✓ Guardando en: {output_path}")

        # Generar audio
        import torchaudio as ta
        wav = tts.generate(texto_prueba)
        ta.save(str(output_path), wav, tts.sr)

        print(f"✓ Audio generado exitosamente en: {output_path}")

        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        print("\nEl entorno está listo para usar TTS-py")

    except ImportError as e:
        print(f"\n❌ ERROR: No se pudo importar Chatterbox")
        print(f"Detalle: {e}")
        print("\nAsegúrate de haber instalado: uv add chatterbox-tts")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Función principal del script de prueba."""
    verificar_entorno()
    probar_chatterbox()


if __name__ == "__main__":
    main()
