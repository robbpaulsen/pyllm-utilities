"""
Tests unitarios para las funciones core de Media-Stitcher

Usa archivos de video-samples/ para pruebas de integración real.
"""

import pytest
from pathlib import Path
import os
import sys

# Agregar el directorio padre al path para importar media_stitcher
sys.path.insert(0, str(Path(__file__).parent.parent))

from media_stitcher import unir_archivos, integrar_audio_a_video, ajustar_velocidad_audio


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def video_samples_dir():
    """Directorio con archivos de muestra"""
    return Path("video-samples")


@pytest.fixture
def output_dir(video_samples_dir):
    """Directorio para outputs de tests"""
    output = video_samples_dir / "test_outputs"
    output.mkdir(exist_ok=True)
    return output


@pytest.fixture
def intro_video(video_samples_dir):
    """Video de intro"""
    path = video_samples_dir / "intro.mp4"
    if not path.exists():
        pytest.skip(f"Archivo no encontrado: {path}")
    return str(path)


@pytest.fixture
def cuerpo_video(video_samples_dir):
    """Video de cuerpo"""
    path = video_samples_dir / "cuerpo.mp4"
    if not path.exists():
        pytest.skip(f"Archivo no encontrado: {path}")
    return str(path)


@pytest.fixture
def outro_video(video_samples_dir):
    """Video de outro"""
    path = video_samples_dir / "outro.mp4"
    if not path.exists():
        pytest.skip(f"Archivo no encontrado: {path}")
    return str(path)


@pytest.fixture
def background_video(video_samples_dir):
    """Video de background"""
    path = video_samples_dir / "background.mp4"
    if not path.exists():
        pytest.skip(f"Archivo no encontrado: {path}")
    return str(path)


@pytest.fixture
def narration_audio(video_samples_dir):
    """Audio de narración"""
    path = video_samples_dir / "narration.mp3"
    if not path.exists():
        pytest.skip(f"Archivo no encontrado: {path}")
    return str(path)


@pytest.fixture
def audio_original(video_samples_dir):
    """Audio original para tests de velocidad"""
    path = video_samples_dir / "audio_original.mp3"
    if not path.exists():
        pytest.skip(f"Archivo no encontrado: {path}")
    return str(path)


# ============================================================================
# TESTS: unir_archivos()
# ============================================================================

def test_unir_archivos_basico(intro_video, cuerpo_video, outro_video, output_dir):
    """Test básico de unir_archivos con safe_mode=True (concat demuxer)"""
    output = output_dir / "test_unir_basico.mp4"

    resultado = unir_archivos(
        lista_paths=[intro_video, cuerpo_video, outro_video],
        output_path=str(output),
        safe_mode=True
    )

    assert resultado is True, "unir_archivos debería retornar True"
    assert output.exists(), "Archivo de salida debería existir"
    assert output.stat().st_size > 0, "Archivo de salida no debería estar vacío"


def test_unir_archivos_con_filter(intro_video, cuerpo_video, output_dir):
    """Test de unir_archivos con safe_mode=False (concat filter)"""
    output = output_dir / "test_unir_filter.mp4"

    resultado = unir_archivos(
        lista_paths=[intro_video, cuerpo_video],
        output_path=str(output),
        safe_mode=False
    )

    assert resultado is True
    assert output.exists()
    assert output.stat().st_size > 0


def test_unir_archivos_menos_de_dos():
    """Test que verifica validación de mínimo 2 archivos"""
    resultado = unir_archivos(
        lista_paths=["solo_un_archivo.mp4"],
        output_path="output.mp4"
    )

    assert resultado is False, "Debería fallar con menos de 2 archivos"


def test_unir_archivos_inexistentes():
    """Test que verifica validación de archivos inexistentes"""
    resultado = unir_archivos(
        lista_paths=["no_existe_1.mp4", "no_existe_2.mp4"],
        output_path="output.mp4"
    )

    assert resultado is False, "Debería fallar con archivos inexistentes"


# ============================================================================
# TESTS: integrar_audio_a_video()
# ============================================================================

def test_integrar_audio_basico(background_video, narration_audio, output_dir):
    """Test básico de integrar_audio_a_video"""
    output = output_dir / "test_integrar_audio.mp4"

    resultado = integrar_audio_a_video(
        video_path=background_video,
        audio_path=narration_audio,
        output_path=str(output),
        reemplazar_audio=True
    )

    assert resultado is True
    assert output.exists()
    assert output.stat().st_size > 0


def test_integrar_audio_archivo_inexistente(output_dir):
    """Test que verifica validación de archivos inexistentes"""
    output = output_dir / "test_integrar_fail.mp4"

    resultado = integrar_audio_a_video(
        video_path="no_existe.mp4",
        audio_path="no_existe.mp3",
        output_path=str(output)
    )

    assert resultado is False, "Debería fallar con archivos inexistentes"


# ============================================================================
# TESTS: ajustar_velocidad_audio()
# ============================================================================

@pytest.mark.parametrize("factor,descripcion", [
    (0.75, "más lento"),
    (1.5, "más rápido"),
    (2.0, "doble velocidad"),
])
def test_ajustar_velocidad_parametrizado(audio_original, output_dir, factor, descripcion):
    """Test parametrizado de ajustar_velocidad_audio con diferentes factores"""
    output = output_dir / f"test_audio_{factor}x.mp3"

    resultado = ajustar_velocidad_audio(
        audio_path=audio_original,
        factor_velocidad=factor,
        output_path=str(output)
    )

    assert resultado is True, f"Debería funcionar con factor {factor} ({descripcion})"
    assert output.exists()
    assert output.stat().st_size > 0


def test_ajustar_velocidad_factor_invalido(audio_original, output_dir):
    """Test que verifica validación de factor negativo"""
    output = output_dir / "test_audio_invalido.mp3"

    resultado = ajustar_velocidad_audio(
        audio_path=audio_original,
        factor_velocidad=-1.0,  # Factor inválido
        output_path=str(output)
    )

    assert resultado is False, "Debería fallar con factor negativo"


def test_ajustar_velocidad_archivo_inexistente(output_dir):
    """Test que verifica validación de archivo inexistente"""
    output = output_dir / "test_audio_fail.mp3"

    resultado = ajustar_velocidad_audio(
        audio_path="no_existe.mp3",
        factor_velocidad=1.5,
        output_path=str(output)
    )

    assert resultado is False, "Debería fallar con archivo inexistente"


# ============================================================================
# TESTS: Funcionalidades GPU (condicionales)
# ============================================================================

def test_unir_archivos_con_gpu_si_disponible(intro_video, cuerpo_video, output_dir):
    """Test de unir_archivos con GPU (skip si GPU no disponible)"""
    from media_stitcher.utils import detectar_gpu_nvidia

    gpu_info = detectar_gpu_nvidia()
    if not gpu_info['disponible']:
        pytest.skip("GPU NVIDIA no disponible")

    output = output_dir / "test_unir_gpu.mp4"

    resultado = unir_archivos(
        lista_paths=[intro_video, cuerpo_video],
        output_path=str(output),
        safe_mode=False,  # Necesario para usar GPU
        use_gpu=True
    )

    assert resultado is True
    assert output.exists()


def test_integrar_audio_con_gpu_si_disponible(background_video, narration_audio, output_dir):
    """Test de integrar_audio_a_video con GPU (skip si GPU no disponible)"""
    from media_stitcher.utils import detectar_gpu_nvidia

    gpu_info = detectar_gpu_nvidia()
    if not gpu_info['disponible']:
        pytest.skip("GPU NVIDIA no disponible")

    output = output_dir / "test_integrar_gpu.mp4"

    resultado = integrar_audio_a_video(
        video_path=background_video,
        audio_path=narration_audio,
        output_path=str(output),
        use_gpu=True
    )

    assert resultado is True
    assert output.exists()


# ============================================================================
# TESTS: Gestión de Temporales
# ============================================================================

def test_gestor_temporales():
    """Test del context manager GestorTemporales"""
    from media_stitcher.utils import GestorTemporales

    temp_path = None

    with GestorTemporales() as temp_dir:
        temp_path = temp_dir
        assert temp_dir.exists(), "Directorio temporal debería existir"

        # Crear un archivo temporal
        test_file = temp_dir / "test.txt"
        test_file.write_text("contenido de prueba")
        assert test_file.exists()

    # Después del context manager, el directorio debería estar eliminado
    assert not temp_path.exists(), "Directorio temporal debería estar eliminado"


# ============================================================================
# CLEANUP
# ============================================================================

def test_cleanup_outputs(output_dir):
    """Test que limpia archivos de salida antiguos (último test)"""
    # Este test se ejecuta al final y opcionalmente limpia outputs
    # Por ahora solo verifica que el directorio existe
    assert output_dir.exists()


if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, "-v", "--tb=short"])
