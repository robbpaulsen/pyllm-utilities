# Audio Samples

Coloca aquí tus muestras de audio de referencia para clonación de voz.

## Formatos Soportados

- **WAV** (recomendado)
- **MP3**
- **FLAC**

## Calidad de las Muestras

Para mejores resultados, usa audio que cumpla:

- ✅ **Duración:** 10-30 segundos mínimo
- ✅ **Calidad:** Sin ruido de fondo, claro y nítido
- ✅ **Contenido:** Habla natural, no susurros ni gritos
- ✅ **Formato:** WAV sin comprimir (44.1kHz o 48kHz)
- ✅ **Voz:** Una sola persona hablando

## Recomendaciones

1. **Grabación limpia:** Usa un micrófono decente en ambiente silencioso
2. **Habla natural:** Lee un texto con entonación normal
3. **Sin música:** Solo voz, sin música de fondo
4. **Volumen consistente:** Ni muy bajo ni saturado

## Ejemplo de Grabación

Graba un texto como este:

> "Hola, mi nombre es [tu nombre]. Me gusta leer libros, escuchar música y aprender cosas nuevas.
> Hoy hace un día soleado y espero que tengas un excelente día. Gracias por escuchar."

## Uso

```bash
# Usar una voz de referencia
uv run main.py --text "Tu texto aquí" --voice audio-samples/mi_voz.wav --output salida.wav

# O con un guion
uv run main.py --script creative-scripts/guion.txt --voice audio-samples/mi_voz.wav --output salida.wav
```

## Ética y Legalidad

⚠️ **IMPORTANTE:**

- ✅ Usa solo tu propia voz o voces con permiso explícito
- ✅ Para proyectos personales y creativos legítimos
- ❌ NO uses para suplantar identidad
- ❌ NO uses voces de otras personas sin consentimiento
- ❌ NO uses para engañar o defraudar

Este proyecto es para uso **ético y legal** solamente.
