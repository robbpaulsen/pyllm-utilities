#!/usr/bin/env bash
# Script de instalación para Fast PyTranscriptor con Flash Attention 2
# Optimizado para CUDA 13.0 y Python 3.10

clear
echo "🚀 Instalando Fast PyTranscriptor (Transcriptor de Audio MVP)"
echo "======================================="

# Verificar uv
if ! command -v uv &> /dev/null; then
    echo "❌ uv no está instalado"
    echo "📦 Instala con: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Verificar versión de Python
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "🐍 Python detectado: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" != "3.10" ]]; then
    echo "⚠️  ADVERTENCIA: Se requiere Python 3.10 para Flash Attention"
    echo "   Tu versión: Python $PYTHON_VERSION"
    echo "   Flash Attention puede no instalarse correctamente"
    read -p "¿Deseas continuar de todas formas? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Detectar CUDA
CUDA_VERSION=$(nvidia-smi | grep -oP "CUDA Version: \K[0-9]+\.[0-9]+" | head -1)
echo "🎮 CUDA detectado: $CUDA_VERSION"

# Crear entorno virtual
echo "📦 Creando entorno virtual con Python 3.10..."
uv venv .venv --python 3.10
source .venv/bin/activate || . .venv/Scripts/activate

# Actualizar pip
echo "📦 Actualizando pip y setuptools..."
uv pip install --upgrade pip setuptools wheel

# Instalar PyTorch con CUDA
echo "🔧 Instalando PyTorch con soporte CUDA..."
if [[ "$CUDA_VERSION" == "13.0" ]]; then
    echo "   Instalando PyTorch para CUDA 13.0..."
    uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
elif [[ "$CUDA_VERSION" == "12."* ]]; then
    echo "   Instalando PyTorch para CUDA 12.x..."
    uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
else
    echo "   Instalando PyTorch para CUDA 11.8..."
    uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
fi

# Instalar dependencias base
echo "📦 Instalando dependencias base..."
uv pip install transformers accelerate optimum tqdm

# Instalar Flash Attention 2
echo "⚡ Instalando Flash Attention 2..."
echo "   (Esto puede tardar varios minutos...)"

# Función para instalar Flash Attention
install_flash_attention() {
    local success=0
    
    # Para CUDA 13.0 y Python 3.10
    if [[ "$CUDA_VERSION" == "13.0" && "$PYTHON_VERSION" == "3.10" ]]; then
        echo "   Usando wheel pre-compilado para CUDA 13.0..."
        if uv pip install https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.4.18/flash_attn-2.8.3+cu130torch2.9-cp310-cp310-linux_x86_64.whl; then
            success=1
        fi
    fi
    
    # Si no funcionó el anterior, intentar otros wheels
    if [[ $success -eq 0 ]]; then
        echo "   Intentando wheel alternativo..."
        # Detectar versión de PyTorch
        TORCH_VERSION=$(python -c "import torch; print(torch.__version__.split('+')[0])" 2>/dev/null)
        
        if [[ -n "$TORCH_VERSION" ]]; then
            # Intentar descargar wheel apropiado
            WHEEL_URL=""
            if [[ "$TORCH_VERSION" == "2.4"* && "$PYTHON_VERSION" == "3.10" ]]; then
                WHEEL_URL="https://github.com/Dao-AILab/flash-attention/releases/download/v2.6.3/flash_attn-2.6.3+cu123torch2.4cxx11abiFALSE-cp310-cp310-linux_x86_64.whl"
            elif [[ "$TORCH_VERSION" == "2.3"* && "$PYTHON_VERSION" == "3.10" ]]; then
                WHEEL_URL="https://github.com/Dao-AILab/flash-attention/releases/download/v2.6.3/flash_attn-2.6.3+cu123torch2.3cxx11abiFALSE-cp310-cp310-linux_x86_64.whl"
            fi
            
            if [[ -n "$WHEEL_URL" ]]; then
                if wget -q "$WHEEL_URL" -O flash_attn.whl && uv pip install --no-deps flash_attn.whl; then
                    rm flash_attn.whl
                    success=1
                fi
            fi
        fi
    fi
    
    # Último intento: compilar desde source
    if [[ $success -eq 0 ]]; then
        echo "   Intentando compilar desde source..."
        uv pip install ninja
        if uv pip install flash-attn --no-build-isolation; then
            success=1
        fi
    fi
    
    return $((1 - success))
}

# Intentar instalar Flash Attention
if install_flash_attention; then
    echo "✅ Flash Attention 2 instalado correctamente"
else
    echo "⚠️  Flash Attention 2 no se pudo instalar"
    echo "   El script funcionará sin él (un poco más lento)"
fi

# Verificar instalación
echo ""
echo "🔍 Verificando instalación..."
uv run python -c "
import sys
print(f'🐍 Python: {sys.version}')
try:
    import torch
    print(f'✅ PyTorch: {torch.__version__}')
    print(f'✅ CUDA disponible: {torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'✅ GPU: {torch.cuda.get_device_name(0)}')
        print(f'✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB')
        print(f'✅ CUDA version (PyTorch): {torch.version.cuda}')
except ImportError:
    print('❌ PyTorch no instalado')
    
try:
    import flash_attn
    print(f'✅ Flash Attention 2 disponible: v{flash_attn.__version__}')
except ImportError:
    print('⚠️  Flash Attention 2 no disponible (usando atención estándar)')
    
try:
    import transformers
    print(f'✅ Transformers: v{transformers.__version__}')
except ImportError:
    print('❌ Transformers no instalado')
"

echo ""
echo "✅ Instalación completada!"
echo ""
echo "📖 Uso básico:"
echo "   uv run python main.py audio.mp3 -o ./salida"
echo ""
echo "📖 Ver más opciones:"
echo "   uv run python main.py --help"
echo ""
echo "💡 Tip: Si usas Python 3.11+, Flash Attention no funcionará"
echo "        pero el script seguirá siendo funcional."
