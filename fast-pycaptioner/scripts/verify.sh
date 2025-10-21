#!/usr/bin/env bash
# Script de verificación rápida de instalación

echo "🔍 Verificando instalación de Fast PyTranscriptor..."
echo "================================================"

# Verificar Python
echo -n "Python: "
python --version

# Verificar CUDA
echo -n "CUDA: "
nvidia-smi | grep -oP "CUDA Version: \K[0-9]+\.[0-9]+" | head -1

# Verificar librerías Python
echo ""
echo "📦 Verificando librerías instaladas:"
uv run python -c "
import sys
print(f'  Python en venv: {sys.executable}')

try:
    import torch
    print(f'  ✅ PyTorch: {torch.__version__}')
    if torch.cuda.is_available():
        print(f'     - GPU: {torch.cuda.get_device_name(0)}')
        print(f'     - CUDA (PyTorch): {torch.version.cuda}')
    else:
        print('     ⚠️  GPU no disponible')
except ImportError:
    print('  ❌ PyTorch no instalado')

try:
    import flash_attn
    print(f'  ✅ Flash Attention: {flash_attn.__version__}')
except ImportError:
    print('  ⚠️  Flash Attention no instalado (opcional)')

try:
    import transformers
    print(f'  ✅ Transformers: {transformers.__version__}')
except ImportError:
    print('  ❌ Transformers no instalado')

try:
    import accelerate
    print(f'  ✅ Accelerate: {accelerate.__version__}')
except ImportError:
    print('  ❌ Accelerate no instalado')
"

echo ""
echo "💡 Para una prueba completa, ejecuta:"
echo "   uv run python main.py --help"
