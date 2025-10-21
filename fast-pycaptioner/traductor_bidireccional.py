#!/usr/bin/env python3
"""
Módulo de traducción bidireccional para Fast PyTranscriptor
Usa MarianMT de Helsinki-NLP para traducir entre múltiples idiomas
"""

from transformers import MarianMTModel, MarianTokenizer
import torch
import logging

logger = logging.getLogger(__name__)

class TraductorBidireccional:
    def __init__(self, device="cpu"):
        self.device = device
        self.modelos_cache = {}
        
        # Mapeo de códigos de idioma
        self.codigo_marian = {
            'es': 'es',  # español
            'en': 'en',  # inglés
            'fr': 'fr',  # francés
            'de': 'de',  # alemán
            'it': 'it',  # italiano
            'pt': 'pt',  # portugués
            'ru': 'ru',  # ruso
            'zh': 'zh',  # chino
            'ja': 'jap', # japonés (Marian usa 'jap')
        }
        
    def _get_modelo_traduccion(self, idioma_origen, idioma_destino):
        """Obtiene o carga el modelo de traducción apropiado"""
        # Convertir códigos
        origen = self.codigo_marian.get(idioma_origen, idioma_origen)
        destino = self.codigo_marian.get(idioma_destino, idioma_destino)
        
        # Crear clave para caché
        clave = f"{origen}-{destino}"
        
        if clave not in self.modelos_cache:
            try:
                # Intentar cargar modelo directo
                modelo_nombre = f"Helsinki-NLP/opus-mt-{origen}-{destino}"
                logger.info(f"Cargando modelo de traducción: {modelo_nombre}")
                
                tokenizer = MarianTokenizer.from_pretrained(modelo_nombre)
                model = MarianMTModel.from_pretrained(modelo_nombre)
                
                if self.device != "cpu" and torch.cuda.is_available():
                    model = model.to(self.device)
                
                self.modelos_cache[clave] = (tokenizer, model)
                
            except Exception as e:
                # Si no existe modelo directo, intentar multi-idioma
                logger.warning(f"No se encontró modelo {origen}-{destino}, intentando alternativas...")
                
                # Intentar modelos multiidioma
                alternativas = [
                    f"Helsinki-NLP/opus-mt-{origen}-en",  # Origen a inglés
                    f"Helsinki-NLP/opus-mt-en-{destino}", # Inglés a destino
                    "Helsinki-NLP/opus-mt-en-romance",    # Inglés a lenguas romances
                    "Helsinki-NLP/opus-mt-romance-en",    # Lenguas romances a inglés
                ]
                
                for alt in alternativas:
                    try:
                        tokenizer = MarianTokenizer.from_pretrained(alt)
                        model = MarianMTModel.from_pretrained(alt)
                        
                        if self.device != "cpu" and torch.cuda.is_available():
                            model = model.to(self.device)
                            
                        self.modelos_cache[clave] = (tokenizer, model)
                        logger.info(f"Usando modelo alternativo: {alt}")
                        break
                    except:
                        continue
                
                if clave not in self.modelos_cache:
                    raise Exception(f"No se pudo cargar modelo de traducción {origen}-{destino}")
        
        return self.modelos_cache[clave]
    
    def traducir(self, texto, idioma_origen, idioma_destino, max_length=512):
        """Traduce texto de un idioma a otro"""
        if idioma_origen == idioma_destino:
            return texto
            
        try:
            tokenizer, model = self._get_modelo_traduccion(idioma_origen, idioma_destino)
            
            # Dividir texto largo en chunks si es necesario
            if len(texto) > max_length * 3:  # Aproximación
                # Dividir por párrafos o frases
                partes = texto.split('\n\n')
                if len(partes) == 1:
                    partes = texto.split('. ')
                
                traducciones = []
                for parte in partes:
                    if parte.strip():
                        inputs = tokenizer(parte, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
                        
                        if self.device != "cpu":
                            inputs = {k: v.to(self.device) for k, v in inputs.items()}
                        
                        translated = model.generate(**inputs)
                        trad = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
                        traducciones.append(trad)
                
                return '\n\n'.join(traducciones) if '\n\n' in texto else '. '.join(traducciones)
            
            else:
                # Texto corto, traducir directamente
                inputs = tokenizer(texto, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
                
                if self.device != "cpu":
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                translated = model.generate(**inputs)
                return tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
                
        except Exception as e:
            logger.error(f"Error en traducción {idioma_origen}->{idioma_destino}: {e}")
            return texto  # Devolver texto original si falla

# Función helper para integrar con el transcriptor principal
def agregar_traduccion_bidireccional(transcriptor_class):
    """Decorator para agregar traducción bidireccional a la clase TranscriptorGPU"""
    
    # Guardar el __init__ original
    original_init = transcriptor_class.__init__
    
    def nuevo_init(self, *args, **kwargs):
        # Llamar al init original
        original_init(self, *args, **kwargs)
        # Agregar traductor
        self.traductor = TraductorBidireccional(self.device)
    
    # Guardar transcribir_archivo original
    original_transcribir = transcriptor_class.transcribir_archivo
    
    def nuevo_transcribir(self, archivo_path, idioma_origen=None, traducir=False, idioma_destino='en'):
        """Version mejorada con traducción a cualquier idioma"""
        # Primero obtener transcripción
        resultado = original_transcribir(self, archivo_path, idioma_origen, traducir=False)
        
        if "error" in resultado:
            return resultado
        
        # Si se pidió traducción
        if traducir:
            texto_original = resultado["texto"]
            
            # Detectar idioma si no se especificó
            if not idioma_origen and "idioma" in resultado:
                idioma_origen = resultado["idioma"]
            
            # Si Whisper puede traducir directamente a inglés, usarlo
            if idioma_destino == 'en' and idioma_origen != 'en':
                resultado_whisper = original_transcribir(self, archivo_path, idioma_origen, traducir=True)
                if "error" not in resultado_whisper:
                    resultado["texto_traducido"] = resultado_whisper["texto"]
                    resultado["idioma_destino"] = 'en'
                    return resultado
            
            # Para otros casos, usar traductor bidireccional
            logger.info(f"Traduciendo de {idioma_origen} a {idioma_destino}...")
            texto_traducido = self.traductor.traducir(
                texto_original, 
                idioma_origen or 'auto', 
                idioma_destino
            )
            
            resultado["texto_traducido"] = texto_traducido
            resultado["idioma_destino"] = idioma_destino
            resultado["texto_original"] = texto_original
            resultado["texto"] = texto_traducido  # Reemplazar con traducción
        
        return resultado
    
    # Reemplazar métodos
    transcriptor_class.__init__ = nuevo_init
    transcriptor_class.transcribir_archivo = nuevo_transcribir
    
    return transcriptor_class

# Ejemplo de uso:
# from traductor_bidireccional import agregar_traduccion_bidireccional
# 
# @agregar_traduccion_bidireccional
# class TranscriptorGPU:
#     ... (tu clase original)
