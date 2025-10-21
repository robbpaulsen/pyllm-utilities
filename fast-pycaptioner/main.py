#!/usr/bin/env python3
"""
Fast PyTranscriptor - Utilidad de Transcripción de Audio MVP
- Multi-idioma (100+ idiomas soportados)
- Procesamiento en paralelo
- Optimizado para GPU con Flash Attention 2
- Diseñado para RTX 3060 con CUDA 13.0
"""

import argparse
import torch
from pathlib import Path
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp
from tqdm import tqdm
import os
import sys
import logging
from traductor_bidireccional import agregar_traduccion_bidireccional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TranscriptorGPU:
    def __init__(self, device_id=0, enable_flash_attention=True):
        """Inicializa el transcriptor con optimizaciones para RTX 3060"""
        self.device = f"cuda:{device_id}" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        # Verificar GPU
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(device_id)
            logger.info(f"🎮 GPU detectada: {gpu_name}")
            logger.info(f"💾 VRAM disponible: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            logger.warning("⚠️  No se detectó GPU, usando CPU")
        
        # Modelo optimizado
        self.model_id = "openai/whisper-large-v3-turbo"
        
        # Cargar modelo con optimizaciones
        logger.info("📥 Cargando modelo Whisper Large v3 Turbo...")
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id,
            torch_dtype=self.torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True,
            attn_implementation="flash_attention_2" if enable_flash_attention and self.device != "cpu" else "eager"
        )
        
        # Optimizaciones adicionales
        if self.device != "cpu":
            self.model = self.model.to(self.device)
            # Compilar modelo para mayor velocidad (PyTorch 2.0+)
            if hasattr(torch, 'compile'):
                logger.info("🚀 Compilando modelo con torch.compile()...")
                self.model = torch.compile(self.model, mode="reduce-overhead")
        
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        
        # Pipeline optimizado
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16 if self.device != "cpu" else 1,  # Mayor batch para GPU
            torch_dtype=self.torch_dtype,
            device=self.device,
        )
        
        logger.info("✅ Modelo cargado y optimizado")
    
    def transcribir_archivo(self, archivo_path, idioma_origen=None, traducir=False, traducir_a=None):
        """Transcribe un solo archivo"""
        try:
            logger.info(f"🎤 Procesando: {archivo_path}")
            
            generate_kwargs = {}
            if idioma_origen:
                generate_kwargs["language"] = idioma_origen
            
            # Si traducir_a == 'en', usar la traducción nativa de Whisper
            if traducir or traducir_a == 'en':
                generate_kwargs["task"] = "translate"
            
            resultado = self.pipe(
                str(archivo_path),
                generate_kwargs=generate_kwargs,
                return_timestamps=True
            )
            
            texto_final = resultado["text"]
            
            # Si se pidió traducir a un idioma diferente de inglés, necesitamos un traductor adicional
            if traducir_a and traducir_a != 'en':
                logger.warning(f"⚠️  Whisper solo traduce a inglés. Para traducir a {traducir_a} se necesita un traductor adicional.")
                # Aquí podrías agregar otro modelo de traducción
            
            return {
                "archivo": str(archivo_path),
                "texto": texto_final,
                "chunks": resultado.get("chunks", []),
                "idioma": idioma_origen or "auto",
                "traducido": traducir or bool(traducir_a),
                "idioma_destino": traducir_a if traducir_a else ("en" if traducir else None)
            }
        except Exception as e:
            logger.error(f"❌ Error procesando {archivo_path}: {e}")
            return {
                "archivo": str(archivo_path),
                "error": str(e)
            }

def obtener_archivos_audio(ruta):
    """Obtiene todos los archivos de audio de una ruta"""
    extensiones_audio = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.opus', '.webm', '.mp4', '.avi', '.mkv'}
    ruta = Path(ruta)
    
    if ruta.is_file():
        return [ruta] if ruta.suffix.lower() in extensiones_audio else []
    elif ruta.is_dir():
        archivos = []
        for ext in extensiones_audio:
            archivos.extend(ruta.rglob(f"*{ext}"))
        return sorted(archivos)
    return []

def procesar_archivos_paralelo(transcriptor, archivos, idioma, traducir, num_workers=2):
    """Procesa múltiples archivos en paralelo usando threads"""
    resultados = []
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Crear tareas
        futuros = {
            executor.submit(
                transcriptor.transcribir_archivo, 
                archivo, 
                idioma, 
                traducir
            ): archivo for archivo in archivos
        }
        
        # Procesar con barra de progreso
        with tqdm(total=len(archivos), desc="🔄 Transcribiendo") as pbar:
            for futuro in futuros:
                resultado = futuro.result()
                resultados.append(resultado)
                pbar.update(1)
    
    return resultados

def guardar_resultados(resultados, directorio_salida, formato='txt'):
    """Guarda los resultados en archivos"""
    directorio_salida = Path(directorio_salida)
    directorio_salida.mkdir(parents=True, exist_ok=True)
    
    for resultado in resultados:
        if "error" in resultado:
            continue
        
        archivo_original = Path(resultado["archivo"])
        nombre_salida = archivo_original.stem
        
        if formato == 'txt':
            archivo_salida = directorio_salida / f"{nombre_salida}_transcripcion.txt"
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                f.write(f"Archivo: {resultado['archivo']}\n")
                f.write(f"Idioma: {resultado['idioma']}\n")
                f.write(f"Traducido: {'Sí' if resultado['traducido'] else 'No'}\n")
                f.write("-" * 50 + "\n")
                f.write(resultado['texto'])
        
        elif formato == 'srt':
            archivo_salida = directorio_salida / f"{nombre_salida}.srt"
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                for i, chunk in enumerate(resultado.get('chunks', []), 1):
                    inicio = chunk['timestamp'][0]
                    fin = chunk['timestamp'][1]
                    f.write(f"{i}\n")
                    f.write(f"{formato_tiempo_srt(inicio)} --> {formato_tiempo_srt(fin)}\n")
                    f.write(f"{chunk['text'].strip()}\n\n")
        
        logger.info(f"💾 Guardado: {archivo_salida}")

def formato_tiempo_srt(segundos):
    """Convierte segundos a formato SRT (HH:MM:SS,mmm)"""
    if segundos is None:
        return "00:00:00,000"
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    secs = segundos % 60
    return f"{horas:02d}:{minutos:02d}:{secs:06.3f}".replace('.', ',')

def main():
    parser = argparse.ArgumentParser(
        description='Transcriptor de Audio MVP - Multi-idioma con GPU',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Transcribir un archivo
  python transcriptor_mvp.py audio.mp3 -o ./salida
  
  # Transcribir un directorio completo en paralelo
  python transcriptor_mvp.py ./videos -o ./transcripciones --workers 4
  
  # Transcribir y traducir al inglés
  python transcriptor_mvp.py video.mp4 -o ./salida --idioma es --traducir
  
  # Generar subtítulos SRT
  python transcriptor_mvp.py video.mp4 -o ./salida --formato srt
        """
    )
    
    parser.add_argument('entrada', 
                       help='Archivo o directorio de entrada')
    parser.add_argument('-o', '--salida', 
                       default='./transcripciones',
                       help='Directorio de salida (default: ./transcripciones)')
    parser.add_argument('--idioma', 
                       help='Código de idioma (es, en, fr, etc.). Auto-detecta si no se especifica')
    parser.add_argument('--traducir', 
                       action='store_true',
                       help='Activar traducción')
    parser.add_argument('--idioma-destino', 
                       default='en',
                       help='Idioma destino para traducción (default: en). Whisper solo soporta traducción a inglés')
    parser.add_argument('--formato', 
                       choices=['txt', 'srt'],
                       default='txt',
                       help='Formato de salida (default: txt)')
    parser.add_argument('--workers', 
                       type=int, 
                       default=2,
                       help='Número de workers paralelos (default: 2)')
    parser.add_argument('--no-flash-attention', 
                       action='store_true',
                       help='Desactivar Flash Attention 2')
    parser.add_argument('--gpu', 
                       type=int, 
                       default=0,
                       help='ID de GPU a usar (default: 0)')
    
    args = parser.parse_args()
    
    # Verificar entrada
    entrada = Path(args.entrada)
    if not entrada.exists():
        logger.error(f"❌ No existe: {args.entrada}")
        sys.exit(1)
    
    # Obtener archivos
    archivos = obtener_archivos_audio(entrada)
    if not archivos:
        logger.error("❌ No se encontraron archivos de audio")
        sys.exit(1)
    
    logger.info(f"📁 Encontrados {len(archivos)} archivo(s)")
    
    # Inicializar transcriptor
    transcriptor = TranscriptorGPU(
        device_id=args.gpu,
        enable_flash_attention=not args.no_flash_attention
    )
    
    # Procesar archivos
    if len(archivos) == 1:
        # Un solo archivo - procesamiento directo
        resultado = transcriptor.transcribir_archivo(
            archivos[0], 
            args.idioma, 
            args.traducir
        )
        resultados = [resultado]
    else:
        # Múltiples archivos - procesamiento paralelo
        resultados = procesar_archivos_paralelo(
            transcriptor,
            archivos,
            args.idioma,
            args.traducir,
            num_workers=args.workers
        )
    
    # Guardar resultados
    guardar_resultados(resultados, args.salida, args.formato)
    
    # Resumen
    exitosos = sum(1 for r in resultados if "error" not in r)
    logger.info(f"\n✅ Procesados exitosamente: {exitosos}/{len(archivos)}")
    
    if exitosos < len(archivos):
        errores = [r for r in resultados if "error" in r]
        logger.warning("\n⚠️  Archivos con errores:")
        for error in errores:
            logger.warning(f"  - {error['archivo']}: {error['error']}")

if __name__ == "__main__":
    # Configurar para mejor rendimiento en GPU
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
    
    main()
