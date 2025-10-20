#!/usr/bin/env python3
"""
Test simple de Chatterbox TTS con workaround para Perth watermarker.
"""

import os
os.environ['HF_HUB_DISABLE_XET'] = '1'

import torch
import torchaudio as ta
from pathlib import Path

# Patch para resolver el problema del watermarker
import perth
if perth.PerthImplicitWatermarker is None:
    print("⚠ PerthImplicitWatermarker no disponible, usando DummyWatermarker")
    perth.PerthImplicitWatermarker = perth.DummyWatermarker

from chatterbox.tts import ChatterboxTTS

print("=" * 60)
print("TEST SIMPLE DE CHATTERBOX TTS")
print("=" * 60)

# Detectar dispositivo
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\n✓ Usando dispositivo: {device}")

if torch.cuda.is_available():
    print(f"✓ GPU: {torch.cuda.get_device_name(0)}")

# Cargar modelo
print("\nCargando modelo Chatterbox...")
model = ChatterboxTTS.from_pretrained(device=device)
print("✓ Modelo cargado exitosamente")

# Generar audio de prueba
texto = "Hola, esto es una prueba de Chatterbox TTS. La instalación fue exitosa."
print(f"\nGenerando audio: '{texto}'")

wav = model.generate(texto)
print("✓ Audio generado")

# Guardar
output_path = Path("output-dir/test_simple.wav")
output_path.parent.mkdir(exist_ok=True)
ta.save(str(output_path), wav, model.sr)

size_mb = output_path.stat().st_size / (1024 * 1024)
print(f"✓ Audio guardado en: {output_path}")
print(f"✓ Tamaño: {size_mb:.2f} MB")

print("\n" + "=" * 60)
print("✅ TEST COMPLETADO EXITOSAMENTE")
print("=" * 60)
