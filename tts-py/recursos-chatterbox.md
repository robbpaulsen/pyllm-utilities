# PROYECTOS DE GITHUB CON CHATTERBOX (TODOS SON GUI's DE GRADIO)

- https://github.com/petermg/Chatterbox-TTS-Extended
- https://github.com/arifulislamat/local-voice-cloning-app
- https://github.com/devnen/Chatterbox-TTS-Server
- https://github.com/resemble-ai/chatterbox
- https://github.com/travisvn/chatterbox-tts-api

# CHATTERBOX HUGGINGFACE ARCHIVOS:
- https://huggingface.co/ResembleAI/chatterbox/tree/main

# CHATTERBOX HUGGINGFACE MODEL CARD:
- https://huggingface.co/ResembleAI/chatterbox

# SAMPLES SIMPLES:

## INSTALACION SEGUN RESEMBLEAI EN HUGGINGFACE:

### Installation
```
pip install chatterbox-tts
```

### Usage
```python
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

model = ChatterboxTTS.from_pretrained(device="cuda")

text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
wav = model.generate(text)
ta.save("test-1.wav", wav, model.sr)

## If you want to synthesize with a different voice, specify the audio prompt
AUDIO_PROMPT_PATH="YOUR_FILE.wav"
wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
ta.save("test-2.wav", wav, model.sr)
```

### Multilingual Quickstart
```python
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device="cuda")

french_text = "Bonjour, comment ça va? Ceci est le modèle de synthèse vocale multilingue Chatterbox, il prend en charge 23 langues."
wav_french = multilingual_model.generate(french_text, language_id="fr")
ta.save("test-french.wav", wav_french, model.sr)

chinese_text = "你好，今天天气真不错，希望你有一个愉快的周末。"
wav_chinese = multilingual_model.generate(chinese_text, language_id="zh")
ta.save("test-chinese.wav", wav_chinese, model.sr)
```

See `example_tts.py` for more examples.

### EJEMPLO SENCILLO `example_tts.py`
```python
import torchaudio as ta
import torch
from chatterbox.tts import ChatterboxTTS
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

# Automatically detect the best available device
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

print(f"Using device: {device}")

model = ChatterboxTTS.from_pretrained(device=device)

text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
wav = model.generate(text)
ta.save("test-1.wav", wav, model.sr)

multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device=device)
text = "Bonjour, comment ça va? Ceci est le modèle de synthèse vocale multilingue Chatterbox, il prend en charge 23 langues."
wav = multilingual_model.generate(text, language_id="fr")
ta.save("test-2.wav", wav, multilingual_model.sr)


# If you want to synthesize with a different voice, specify the audio prompt
AUDIO_PROMPT_PATH = "YOUR_FILE.wav"
wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
ta.save("test-3.wav", wav, model.sr)
```

### EJEMPLO `example_vc.py`
```python
import torch
import torchaudio as ta

from chatterbox.vc import ChatterboxVC

# Automatically detect the best available device
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

print(f"Using device: {device}")

AUDIO_PATH = "YOUR_FILE.wav"
TARGET_VOICE_PATH = "YOUR_FILE.wav"

model = ChatterboxVC.from_pretrained(device)
wav = model.generate(
    audio=AUDIO_PATH,
    target_voice_path=TARGET_VOICE_PATH,
)
ta.save("testvc.wav", wav, model.sr)
```

### APLICACION MULTI IDIOMA `multilingual_app.py`
```python
import random
import numpy as np
import torch
from chatterbox.mtl_tts import ChatterboxMultilingualTTS, SUPPORTED_LANGUAGES
import gradio as gr

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 Running on device: {DEVICE}")

# --- Global Model Initialization ---
MODEL = None

LANGUAGE_CONFIG = {
    "ar": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/ar_f/ar_prompts2.flac",
        "text": "في الشهر الماضي، وصلنا إلى معلم جديد بمليارين من المشاهدات على قناتنا على يوتيوب."
    },
    "da": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/da_m1.flac",
        "text": "Sidste måned nåede vi en ny milepæl med to milliarder visninger på vores YouTube-kanal."
    },
    "de": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/de_f1.flac",
        "text": "Letzten Monat haben wir einen neuen Meilenstein erreicht: zwei Milliarden Aufrufe auf unserem YouTube-Kanal."
    },
    "el": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/el_m.flac",
        "text": "Τον περασμένο μήνα, φτάσαμε σε ένα νέο ορόσημο με δύο δισεκατομμύρια προβολές στο κανάλι μας στο YouTube."
    },
    "en": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/en_f1.flac",
        "text": "Last month, we reached a new milestone with two billion views on our YouTube channel."
    },
    "es": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/es_f1.flac",
        "text": "El mes pasado alcanzamos un nuevo hito: dos mil millones de visualizaciones en nuestro canal de YouTube."
    },
    "fi": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/fi_m.flac",
        "text": "Viime kuussa saavutimme uuden virstanpylvään kahden miljardin katselukerran kanssa YouTube-kanavallamme."
    },
    "fr": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/fr_f1.flac",
        "text": "Le mois dernier, nous avons atteint un nouveau jalon avec deux milliards de vues sur notre chaîne YouTube."
    },
    "he": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/he_m1.flac",
        "text": "בחודש שעבר הגענו לאבן דרך חדשה עם שני מיליארד צפיות בערוץ היוטיוב שלנו."
    },
    "hi": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/hi_f1.flac",
        "text": "पिछले महीने हमने एक नया मील का पत्थर छुआ: हमारे YouTube चैनल पर दो अरब व्यूज़।"
    },
    "it": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/it_m1.flac",
        "text": "Il mese scorso abbiamo raggiunto un nuovo traguardo: due miliardi di visualizzazioni sul nostro canale YouTube."
    },
    "ja": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/ja/ja_prompts1.flac",
        "text": "先月、私たちのYouTubeチャンネルで二十億回の再生回数という新たなマイルストーンに到達しました。"
    },
    "ko": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/ko_f.flac",
        "text": "지난달 우리는 유튜브 채널에서 이십억 조회수라는 새로운 이정표에 도달했습니다."
    },
    "ms": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/ms_f.flac",
        "text": "Bulan lepas, kami mencapai pencapaian baru dengan dua bilion tontonan di saluran YouTube kami."
    },
    "nl": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/nl_m.flac",
        "text": "Vorige maand bereikten we een nieuwe mijlpaal met twee miljard weergaven op ons YouTube-kanaal."
    },
    "no": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/no_f1.flac",
        "text": "Forrige måned nådde vi en ny milepæl med to milliarder visninger på YouTube-kanalen vår."
    },
    "pl": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/pl_m.flac",
        "text": "W zeszłym miesiącu osiągnęliśmy nowy kamień milowy z dwoma miliardami wyświetleń na naszym kanale YouTube."
    },
    "pt": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/pt_m1.flac",
        "text": "No mês passado, alcançámos um novo marco: dois mil milhões de visualizações no nosso canal do YouTube."
    },
    "ru": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/ru_m.flac",
        "text": "В прошлом месяце мы достигли нового рубежа: два миллиарда просмотров на нашем YouTube-канале."
    },
    "sv": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/sv_f.flac",
        "text": "Förra månaden nådde vi en ny milstolpe med två miljarder visningar på vår YouTube-kanal."
    },
    "sw": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/sw_m.flac",
        "text": "Mwezi uliopita, tulifika hatua mpya ya maoni ya bilioni mbili kweny kituo chetu cha YouTube."
    },
    "tr": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/tr_m.flac",
        "text": "Geçen ay YouTube kanalımızda iki milyar görüntüleme ile yeni bir dönüm noktasına ulaştık."
    },
    "zh": {
        "audio": "https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/zh_f2.flac",
        "text": "上个月，我们达到了一个新的里程碑. 我们的YouTube频道观看次数达到了二十亿次，这绝对令人难以置信。"
    },
}

# --- UI Helpers ---
def default_audio_for_ui(lang: str) -> str | None:
    return LANGUAGE_CONFIG.get(lang, {}).get("audio")


def default_text_for_ui(lang: str) -> str:
    return LANGUAGE_CONFIG.get(lang, {}).get("text", "")


def get_supported_languages_display() -> str:
    """Generate a formatted display of all supported languages."""
    language_items = []
    for code, name in sorted(SUPPORTED_LANGUAGES.items()):
        language_items.append(f"**{name}** (`{code}`)")
    
    # Split into 2 lines
    mid = len(language_items) // 2
    line1 = " • ".join(language_items[:mid])
    line2 = " • ".join(language_items[mid:])
    
    return f"""
### 🌍 Supported Languages ({len(SUPPORTED_LANGUAGES)} total)
{line1}

{line2}
"""


def get_or_load_model():
    """Loads the ChatterboxMultilingualTTS model if it hasn't been loaded already,
    and ensures it's on the correct device."""
    global MODEL
    if MODEL is None:
        print("Model not loaded, initializing...")
        try:
            MODEL = ChatterboxMultilingualTTS.from_pretrained(DEVICE)
            if hasattr(MODEL, 'to') and str(MODEL.device) != DEVICE:
                MODEL.to(DEVICE)
            print(f"Model loaded successfully. Internal device: {getattr(MODEL, 'device', 'N/A')}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    return MODEL

# Attempt to load the model at startup.
try:
    get_or_load_model()
except Exception as e:
    print(f"CRITICAL: Failed to load model on startup. Application may not function. Error: {e}")

def set_seed(seed: int):
    """Sets the random seed for reproducibility across torch, numpy, and random."""
    torch.manual_seed(seed)
    if DEVICE == "cuda":
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    np.random.seed(seed)
    
def resolve_audio_prompt(language_id: str, provided_path: str | None) -> str | None:
    """
    Decide which audio prompt to use:
    - If user provided a path (upload/mic/url), use it.
    - Else, fall back to language-specific default (if any).
    """
    if provided_path and str(provided_path).strip():
        return provided_path
    return LANGUAGE_CONFIG.get(language_id, {}).get("audio")


def generate_tts_audio(
    text_input: str,
    language_id: str,
    audio_prompt_path_input: str = None,
    exaggeration_input: float = 0.5,
    temperature_input: float = 0.8,
    seed_num_input: int = 0,
    cfgw_input: float = 0.5
) -> tuple[int, np.ndarray]:
    """
    Generate high-quality speech audio from text using Chatterbox Multilingual model with optional reference audio styling.
    Supported languages: English, French, German, Spanish, Italian, Portuguese, and Hindi.
    
    This tool synthesizes natural-sounding speech from input text. When a reference audio file 
    is provided, it captures the speaker's voice characteristics and speaking style. The generated audio 
    maintains the prosody, tone, and vocal qualities of the reference speaker, or uses default voice if no reference is provided.

    Args:
        text_input (str): The text to synthesize into speech (maximum 300 characters)
        language_id (str): The language code for synthesis (eg. en, fr, de, es, it, pt, hi)
        audio_prompt_path_input (str, optional): File path or URL to the reference audio file that defines the target voice style. Defaults to None.
        exaggeration_input (float, optional): Controls speech expressiveness (0.25-2.0, neutral=0.5, extreme values may be unstable). Defaults to 0.5.
        temperature_input (float, optional): Controls randomness in generation (0.05-5.0, higher=more varied). Defaults to 0.8.
        seed_num_input (int, optional): Random seed for reproducible results (0 for random generation). Defaults to 0.
        cfgw_input (float, optional): CFG/Pace weight controlling generation guidance (0.2-1.0). Defaults to 0.5, 0 for language transfer. 

    Returns:
        tuple[int, np.ndarray]: A tuple containing the sample rate (int) and the generated audio waveform (numpy.ndarray)
    """
    current_model = get_or_load_model()

    if current_model is None:
        raise RuntimeError("TTS model is not loaded.")

    if seed_num_input != 0:
        set_seed(int(seed_num_input))

    print(f"Generating audio for text: '{text_input[:50]}...'")
    
    # Handle optional audio prompt
    chosen_prompt = audio_prompt_path_input or default_audio_for_ui(language_id)

    generate_kwargs = {
        "exaggeration": exaggeration_input,
        "temperature": temperature_input,
        "cfg_weight": cfgw_input,
    }
    if chosen_prompt:
        generate_kwargs["audio_prompt_path"] = chosen_prompt
        print(f"Using audio prompt: {chosen_prompt}")
    else:
        print("No audio prompt provided; using default voice.")
        
    wav = current_model.generate(
        text_input[:300],  # Truncate text to max chars
        language_id=language_id,
        **generate_kwargs
    )
    print("Audio generation complete.")
    return (current_model.sr, wav.squeeze(0).numpy())

with gr.Blocks() as demo:
    gr.Markdown(
        """
        # Chatterbox Multilingual Demo
        Generate high-quality multilingual speech from text with reference audio styling, supporting 23 languages.
        """
    )
    
    # Display supported languages
    gr.Markdown(get_supported_languages_display())
    with gr.Row():
        with gr.Column():
            initial_lang = "fr"
            text = gr.Textbox(
                value=default_text_for_ui(initial_lang),
                label="Text to synthesize (max chars 300)",
                max_lines=5
            )
            
            language_id = gr.Dropdown(
                choices=list(ChatterboxMultilingualTTS.get_supported_languages().keys()),
                value=initial_lang,
                label="Language",
                info="Select the language for text-to-speech synthesis"
            )
            
            ref_wav = gr.Audio(
                sources=["upload", "microphone"],
                type="filepath",
                label="Reference Audio File (Optional)",
                value=default_audio_for_ui(initial_lang)
            )
            
            gr.Markdown(
                "💡 **Note**: Ensure that the reference clip matches the specified language tag. Otherwise, language transfer outputs may inherit the accent of the reference clip's language. To mitigate this, set the CFG weight to 0.",
                elem_classes=["audio-note"]
            )
            
            exaggeration = gr.Slider(
                0.25, 2, step=.05, label="Exaggeration (Neutral = 0.5, extreme values can be unstable)", value=.5
            )
            cfg_weight = gr.Slider(
                0.2, 1, step=.05, label="CFG/Pace", value=0.5
            )

            with gr.Accordion("More options", open=False):
                seed_num = gr.Number(value=0, label="Random seed (0 for random)")
                temp = gr.Slider(0.05, 5, step=.05, label="Temperature", value=.8)

            run_btn = gr.Button("Generate", variant="primary")

        with gr.Column():
            audio_output = gr.Audio(label="Output Audio")

        def on_language_change(lang, current_ref, current_text):
            return default_audio_for_ui(lang), default_text_for_ui(lang)

        language_id.change(
            fn=on_language_change,
            inputs=[language_id, ref_wav, text],
            outputs=[ref_wav, text],
            show_progress=False
        )

    run_btn.click(
        fn=generate_tts_audio,
        inputs=[
            text,
            language_id,
            ref_wav,
            exaggeration,
            temp,
            seed_num,
            cfg_weight,
        ],
        outputs=[audio_output],
    )

demo.launch(mcp_server=True)
```

---

### ESTE PROYECTO YA LO BORRARON PERO TENGO DOS VERSIONES DE EL,
EL AUTOR LO BORRO PARA EMPEZAR A VENDERLO, ES UN MCP QUE GENERA
YOUTUBE SHORTS INTEGRANDO `together.ai` su modelo flux schnell, 
chatterbox, ffmpeg, fastapi, docker y n8n


## Estrucutra de proyecto:
```bash
 api_server
 assets
 utils
 video
 .dockerignore
 .gitignore
 cuda.Dockerfile
 Dockerfile
 LICENSE
 README.md
󰌠 requirements.txt
 server.py
```

```bash
 video
├──  builder.py
├──  caption.py
├──  config.py
├──  media.py
├──  storage.py
├──  stt.py
├──  tts.py
└──  tts_chatterbox.py
```

**tts_chatterbox.py**
```python
import os
import time
import traceback
import warnings
from loguru import logger
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from video.config import device
import nltk
import torch
from typing import List, Optional

# Suppress PyTorch warnings
warnings.filterwarnings("ignore")

class TTSChatterbox:
    def __init__(self):
        """Initialize ChatterboxTTS and ensure NLTK data is available."""
        self.ensure_nltk_data()
        logger.debug("ChatterboxTTS initialized")

    def ensure_nltk_data(self):
        """Ensure NLTK punkt tokenizer is available."""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('tokenizers/punkt_tab')
            logger.debug("NLTK punkt tokenizer found")
        except LookupError:
            logger.debug("Downloading NLTK punkt tokenizer...")
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('punkt_tab', quiet=True)
                logger.debug("NLTK punkt tokenizer downloaded successfully")
            except Exception as e:
                logger.error(f"Failed to download NLTK punkt tokenizer: {e}")
                raise        

    def split_text_into_chunks(self, text: str, max_chars_per_chunk: int = 300) -> List[str]:
        """Split text into chunks respecting sentence boundaries without breaking sentences."""
        try:
            sentences = nltk.sent_tokenize(text)
            # Filter out empty sentences and strip whitespace
            sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
            
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                # If adding this sentence would exceed the limit, finalize current chunk
                if current_chunk and len(current_chunk) + len(sentence) + 1 > max_chars_per_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Add sentence to current chunk
                    if current_chunk:
                        current_chunk += " " + sentence
                    else:
                        current_chunk = sentence
            
            # Add the last chunk if it's not empty
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            logger.debug(f"Text split into {len(chunks)} chunks (max {max_chars_per_chunk} chars each, preserving sentences)")
            return chunks
        except Exception as e:
            logger.error(f"Error splitting text: {e}")
            # Fallback: return original text as single chunk
            return [text]

    def generate_audio_chunk(
        self,
        text_chunk: str,
        model: ChatterboxTTS,
        audio_prompt_path: Optional[str] = None,
        temperature: float = 0.7,
        cfg_weight: float = 0.7,
        exaggeration: float = 0.75,
    ) -> Optional[torch.Tensor]:
        """Generate audio tensor for a single text chunk."""
        try:
            logger.debug(f"Generating audio for chunk: {text_chunk[:50]}...")

            
            # Check if audio prompt exists
            effective_prompt_path = None
            if audio_prompt_path and os.path.exists(audio_prompt_path):
                effective_prompt_path = audio_prompt_path
            elif audio_prompt_path:
                logger.warning(f"Audio prompt path not found: {audio_prompt_path}")
            
            # Generate audio
            wav_tensor = model.generate(
                text_chunk,
                audio_prompt_path=effective_prompt_path,
                temperature=temperature,
                cfg_weight=cfg_weight,
                exaggeration=exaggeration
            )
            
            # Ensure tensor is on CPU and properly shaped
            wav_tensor_cpu = wav_tensor.cpu().float()
            
            # Ensure tensor is 2D: [channels, samples]
            if wav_tensor_cpu.ndim == 1:
                wav_tensor_cpu = wav_tensor_cpu.unsqueeze(0)
            elif wav_tensor_cpu.ndim > 2:
                logger.warning(f"Unexpected tensor shape {wav_tensor_cpu.shape}, attempting to fix")
                wav_tensor_cpu = wav_tensor_cpu.squeeze()
                if wav_tensor_cpu.ndim == 1:
                    wav_tensor_cpu = wav_tensor_cpu.unsqueeze(0)
                elif wav_tensor_cpu.ndim != 2 or wav_tensor_cpu.shape[0] != 1:
                    logger.error(f"Could not reshape tensor {wav_tensor.shape} to [1, N]")
                    return None
            
            return wav_tensor_cpu
            
        except Exception as e:
            logger.error(f"Error generating audio chunk: {e}")
            logger.error(traceback.format_exc())
            return None

    def text_to_speech_pipeline(
        self,
        text: str,
        model: ChatterboxTTS,
        max_chars_per_chunk: int = 1024,
        inter_chunk_silence_ms: int = 350,
        audio_prompt_path: Optional[str] = None,
        temperature: float = 0.7,
        cfg_weight: float = 0.7,
        exaggeration: float = 0.75
    ) -> Optional[torch.Tensor]:
        """Convert text to speech with chunking support."""
        try:
            # Split text into chunks
            text_chunks = self.split_text_into_chunks(text, max_chars_per_chunk)
            
            if not text_chunks:
                logger.error("No text chunks to process")
                return None
            
            all_audio_tensors = []
            sample_rate = model.sr
            
            logger.debug(f"Processing {len(text_chunks)} chunks at {sample_rate} Hz")
            
            for i, chunk_text in enumerate(text_chunks):
                logger.debug(f"Processing chunk {i+1}/{len(text_chunks)}")
                
                chunk_tensor = self.generate_audio_chunk(
                    chunk_text,
                    model,
                    audio_prompt_path,
                    temperature,
                    cfg_weight,
                    exaggeration
                )
                
                if chunk_tensor is None:
                    logger.warning(f"Skipping chunk {i+1} due to generation error")
                    continue
                
                all_audio_tensors.append(chunk_tensor)
                
                # Add silence between chunks (except after the last chunk)
                if i < len(text_chunks) - 1 and inter_chunk_silence_ms > 0:
                    silence_samples = int(sample_rate * inter_chunk_silence_ms / 1000.0)
                    silence_tensor = torch.zeros(
                        (1, silence_samples),
                        dtype=chunk_tensor.dtype,
                        device=chunk_tensor.device
                    )
                    all_audio_tensors.append(silence_tensor)
            
            if not all_audio_tensors:
                logger.error("No audio tensors generated")
                return None
            
            # Concatenate all audio tensors
            logger.debug("Concatenating audio tensors...")
            final_audio_tensor = torch.cat(all_audio_tensors, dim=1)
            
            logger.debug(f"Final audio shape: {final_audio_tensor.shape}")
            return final_audio_tensor
            
        except Exception as e:
            logger.error(f"Error in text-to-speech pipeline: {e}")
            logger.error(traceback.format_exc())
            return None

    
    def chatterbox(
        self,
        text: str,
        output_path: str,
        sample_audio_path: str = None,
        exaggeration=0.75,
        cfg_weight=0.7,
        temperature=0.7,
        chunk_chars: int = 1024,
        chunk_silence_ms: int = 350,
    ):
        start = time.time()
        context_logger = logger.bind(
            text_length=len(text),
            sample_audio_path=sample_audio_path,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            temperature=temperature,
            model="ChatterboxTTS",
            language="en-US",
            device=device.type,
        )
        context_logger.debug("starting TTS generation with Chatterbox")
        model = ChatterboxTTS.from_pretrained(device=device.type)

        if sample_audio_path:
            wav = self.text_to_speech_pipeline(
                text,
                model,
                audio_prompt_path=sample_audio_path,
                temperature=temperature,
                cfg_weight=cfg_weight,
                exaggeration=exaggeration,
                max_chars_per_chunk=chunk_chars,
                inter_chunk_silence_ms=chunk_silence_ms
            )
        else:
            wav = self.text_to_speech_pipeline(
                text,
                model,
                temperature=temperature,
                cfg_weight=cfg_weight,
                exaggeration=exaggeration,
                max_chars_per_chunk=chunk_chars,
                inter_chunk_silence_ms=chunk_silence_ms
            )

        if wav.dim() == 2 and wav.shape[0] == 1:
            wav = wav.repeat(2, 1)
        elif wav.dim() == 1:
            wav = wav.unsqueeze(0).repeat(2, 1)

        audio_length = wav.shape[1] / model.sr
        ta.save(output_path, wav, model.sr)
        context_logger.bind(
            execution_time=time.time() - start,
            audio_length=audio_length,
            speedup=audio_length / (time.time() - start),
            youtube_channel="https://www.youtube.com/@MommentumMindset"
        ).debug(
            "TTS generation with Chatterbox completed",
        )
```
