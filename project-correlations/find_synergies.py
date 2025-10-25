#!/usr/bin/env python3
"""
Synergy Finder - Encuentra correlaciones entre utilidades
"""
import json
import argparse
from pathlib import Path

def find_synergies(analyses_dir):
    """Encuentra sinergias entre análisis de proyectos."""
    analyses_dir = Path(analyses_dir)
    analysis_files = list(analyses_dir.glob("*.json"))
    
    if len(analysis_files) < 2:
        print("Necesitas al menos 2 análisis para encontrar sinergias")
        return
    
    utilities = []
    for file_path in analysis_files:
        with open(file_path) as f:
            utilities.append(json.load(f))
    
    print(f"Analizando sinergias entre {len(utilities)} utilidades...")
    
    synergies = []
    
    # Buscar utilidades con imports similares
    for i, util1 in enumerate(utilities):
        for j, util2 in enumerate(utilities[i+1:], i+1):
            shared_imports = set(util1["imports"]) & set(util2["imports"])
            
            if len(shared_imports) >= 2:
                synergy = {
                    "type": "Dependencias Compartidas",
                    "utilities": [util1["project_name"], util2["project_name"]],
                    "shared_imports": list(shared_imports),
                    "potential": "Crear módulo base compartido"
                }
                synergies.append(synergy)
    
    # Buscar patrones complementarios
    media_utils = [u for u in utilities if "MEDIA_PROCESSING" in u.get("patterns", [])]
    api_utils = [u for u in utilities if "API_CLIENT" in u.get("patterns", [])]
    file_utils = [u for u in utilities if "FILE_PROCESSING" in u.get("patterns", [])]
    
    # Sinergia específica para contenido (tu caso de YouTube)
    if len(media_utils) >= 1 and len(file_utils) >= 1:
        synergies.append({
            "type": "Pipeline de Contenido",
            "utilities": [u["project_name"] for u in media_utils + file_utils],
            "description": "Combinar procesamiento multimedia con gestión de archivos",
            "potential": "Crear pipeline automático de contenido (ej: YouTube enhancement)",
            "priority": "HIGH"
        })
    
    if len(api_utils) >= 1 and (len(media_utils) >= 1 or len(file_utils) >= 1):
        synergies.append({
            "type": "Automatización de Publicación",
            "utilities": [u["project_name"] for u in api_utils + media_utils + file_utils],
            "description": "Integrar APIs con procesamiento de contenido",
            "potential": "Sistema de publicación automatizada",
            "priority": "MEDIUM"
        })
    
    return synergies

def main():
    parser = argparse.ArgumentParser(description="Encontrar sinergias entre utilidades")
    parser.add_argument("analyses_dir", help="Directorio con archivos de análisis JSON")
    
    args = parser.parse_args()
    
    synergies = find_synergies(args.analyses_dir)
    
    print(f"\n{'='*60}")
    print("OPORTUNIDADES DE SINERGIA DETECTADAS")
    print(f"{'='*60}")
    
    if not synergies:
        print("No se encontraron sinergias significativas")
        return
    
    for i, synergy in enumerate(synergies, 1):
        print(f"\n{i}. {synergy['type']}")
        print(f"   Utilidades: {', '.join(synergy['utilities'])}")
        print(f"   Potencial: {synergy['potential']}")
        if 'priority' in synergy:
            print(f"   Prioridad: {synergy['priority']}")
        if 'shared_imports' in synergy:
            print(f"   Imports compartidos: {', '.join(synergy['shared_imports'][:3])}...")

if __name__ == "__main__":
    main()
