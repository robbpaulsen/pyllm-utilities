# Fast PyTranscriptor 🎤

Utilidad de transcripción de audio multi-idioma optimizada para GPU con procesamiento en paralelo.

## Características ✨

- **Multi-idioma**: Soporte para 100+ idiomas (especializado en español/inglés)
- **Procesamiento en paralelo**: Procesa múltiples archivos simultáneamente
- **Optimizado para GPU**: Aprovecha tu GPU con Flash Attention 2
- **Flexible**: Acepta archivos individuales o directorios completos
- **Múltiples formatos**: Salida en texto plano o subtítulos SRT
- **Traducción**: Puede traducir automáticamente al inglés

## Requisitos 📋

- **Python 3.10** (requerido para Flash Attention 2)
- **NVIDIA GPU** con CUDA 11.8+ (probado en RTX 3060 con CUDA 13.0)
- **12GB+ VRAM** recomendado para mejor rendimiento

## Instalación 🔧

### Opción 1: Script automático (Recomendado)
```bash
chmod +x instalar.sh
./instalar.sh
```

### Opción 2: Manual con uv
```bash
# 1. Crear entorno virtual con Python 3.10
uv venv .venv --python 3.10
source .venv/bin/activate

# 2. Instalar PyTorch (ajusta según tu versión de CUDA)
# Para CUDA 13.0:
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# Para CUDA 12.x:
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. Instalar dependencias base
uv pip install transformers accelerate optimum tqdm

# 4. Instalar Flash Attention 2 (opcional pero recomendado)
# Para CUDA 13.0 y Python 3.10:
uv pip install https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.4.18/flash_attn-2.8.3+cu130torch2.9-cp310-cp310-linux_x86_64.whl
```

### Instalación especial para CUDA 13.0

Si tienes CUDA 13.0 como yo, estos son los pasos exactos que funcionaron:

```bash
# 1. Asegúrate de usar Python 3.10 (no 3.11)
python --version  # Debe mostrar 3.10.x

# 2. Instalar PyTorch para CUDA 13.0
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# 3. Instalar Flash Attention pre-compilado
uv pip install https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.4.18/flash_attn-2.8.3+cu130torch2.9-cp310-cp310-linux_x86_64.whl

# 4. Instalar el resto de dependencias
uv pip install transformers accelerate optimum tqdm
```

## Uso 🚀

### Ejemplos básicos

**Transcribir un archivo:**
```bash
uv run python main.py audio.mp3 -o ./salida
```

**Transcribir un directorio completo:**
```bash
uv run python main.py ./videos -o ./transcripciones --workers 4
```

**Especificar idioma y traducir:**
```bash
uv run python main.py video.mp4 -o ./salida --idioma es --traducir
```

**Generar subtítulos SRT:**
```bash
uv run python main.py video.mp4 -o ./salida --formato srt
```

### Opciones disponibles

| Opción | Descripción | Default |
|--------|-------------|---------|
| `entrada` | Archivo o directorio a procesar | Requerido |
| `-o, --salida` | Directorio donde guardar resultados | `./transcripciones` |
| `--idioma` | Código de idioma (es, en, fr, etc.) | Auto-detecta |
| `--traducir` | Traducir al inglés | No |
| `--formato` | Formato de salida (txt, srt) | `txt` |
| `--workers` | Número de archivos a procesar en paralelo | `2` |
| `--gpu` | ID de GPU a usar | `0` |
| `--no-flash-attention` | Desactivar Flash Attention 2 | No |

## Formatos soportados 🎵

- Audio: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.opus`
- Video: `.mp4`, `.avi`, `.mkv`, `.webm`

## Optimización GPU 🎮

El script detecta automáticamente tu GPU y aplica las siguientes optimizaciones:

1. **Flash Attention 2**: Reduce uso de memoria y aumenta velocidad
2. **Mixed Precision (FP16)**: Procesamiento más rápido
3. **Torch Compile**: Optimización adicional del modelo
4. **Batch Processing**: Procesa múltiples segmentos simultáneamente

### Verificar configuración
```bash
# Verificar GPU
nvidia-smi

# Verificar instalación
uv run python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"
uv run python -c "import torch; print(f'CUDA: {torch.version.cuda}')"
uv run python -c "import flash_attn; print(f'Flash Attention: {flash_attn.__version__}')"
```

## Rendimiento esperado ⚡

Con RTX 3060 (12GB VRAM):
- **Velocidad**: ~5-10x tiempo real (1 hora de audio en 6-12 minutos)
- **Memoria**: ~4-6 GB VRAM en uso
- **Paralelo**: Hasta 4 archivos simultáneos recomendado

## Idiomas soportados 🌍

Algunos de los idiomas más comunes:
- Español (es)
- Inglés (en)
- Francés (fr)
- Alemán (de)
- Italiano (it)
- Portugués (pt)
- Ruso (ru)
- Chino (zh)
- Japonés (ja)
- Y 90+ más...

## Tips de uso 💡

1. **Para videos de YouTube largos**: Usa `--workers 1` para evitar saturar la VRAM
2. **Para muchos archivos cortos**: Aumenta `--workers` hasta 4
3. **Si falla Flash Attention**: Usa `--no-flash-attention` (será un poco más lento)
4. **Para mejor calidad**: Especifica el idioma con `--idioma es` en vez de auto-detectar
5. **Monitorea tu GPU**: Usa `watch -n 1 nvidia-smi` en otra terminal

## Solución de problemas 🔧

### "CUDA out of memory"
- Reduce `--workers` a 1
- Usa `--no-flash-attention`
- Cierra otras aplicaciones que usen GPU

### "Flash Attention no se pudo instalar"
- Verifica que uses Python 3.10 (no 3.11+)
- El script funciona sin Flash Attention, solo será más lento
- Para CUDA 13.0, usa el wheel de mjun0812

### "No detecta mi GPU"
```bash
# Verifica drivers NVIDIA
nvidia-smi

# Verifica versión de CUDA
nvidia-smi | grep "CUDA Version"

# Reinstala PyTorch con el índice correcto
uv pip uninstall torch torchvision torchaudio
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130  # o cu121, cu118
```

### "uv es muy estricto con dependencias"
- Limpia `pyproject.toml` y `requirements.txt` de dependencias conflictivas
- Instala PyTorch y Flash Attention manualmente antes que otras dependencias
- Usa `--no-deps` cuando sea necesario

## Estructura de salida 📁

```
salida/
├── video1_transcripcion.txt
├── video2_transcripcion.txt
└── video3.srt (si usaste --formato srt)
```

## Ejemplo de archivo de salida (txt)
```
Archivo: /path/to/audio.mp3
Idioma: es
Traducido: No
--------------------------------------------------
[Aquí aparece la transcripción completa del audio]
```

## Roadmap futuro 🗺️

Siguiendo la filosofía "Hecho es Mejor que Perfecto", estas son mejoras planeadas:

- [ ] API REST para integración con otros proyectos
- [ ] Soporte para diarización (identificar speakers)
- [ ] Interfaz web simple
- [ ] Exportar a más formatos (VTT, JSON, WebVTT)
- [ ] Integración con editores de video
- [ ] Procesamiento por lotes con archivo de configuración
- [ ] Detección automática de idioma mejorada
- [ ] Post-procesamiento de texto (puntuación, formato)

## Contribuir 🤝

¿Encontraste un bug o tienes una idea? ¡Abre un issue o PR!

## Licencia 📄

MIT - Úsalo como quieras para tus proyectos

---

#### **Filosofía del proyecto** 
*"Hecho es Mejor que Perfecto" - Este es un MVP funcional. ¡Empieza a usarlo y ve agregando features según las necesites!*

#### **Agradecimientos**
- OpenAI por el modelo Whisper
- mjun0812 por los wheels pre-compilados de Flash Attention
- La comunidad de Hugging Face
