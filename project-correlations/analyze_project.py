#!/usr/bin/env python3
"""
Quick Project Analyzer - Versión simplificada para uso inmediato
"""
import os
import ast
import json
from pathlib import Path
import argparse

def analyze_project(project_path):
    """Analiza un proyecto Python y encuentra patrones."""
    project_path = Path(project_path)
    
    analysis = {
        "project_name": project_path.name,
        "functions": [],
        "classes": [],
        "imports": set(),
        "patterns": [],
        "suggestions": []
    }
    
    # Encontrar archivos Python
    python_files = list(project_path.rglob("*.py"))
    print(f"Analizando {len(python_files)} archivos Python...")
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extraer funciones
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "file": py_file.name,
                        "args": len(node.args.args)
                    })
                
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "file": py_file.name
                    })
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].add(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["imports"].add(node.module)
        
        except Exception as e:
            print(f"Error analizando {py_file}: {e}")
    
    # Convertir set a lista para JSON
    analysis["imports"] = list(analysis["imports"])
    
    # Detectar patrones
    api_imports = [imp for imp in analysis["imports"] if 
                   any(keyword in imp.lower() for keyword in ["requests", "http", "api"])]
    if api_imports:
        analysis["patterns"].append("API_CLIENT")
        analysis["suggestions"].append("Crear utilidad de cliente API genérico")
    
    media_imports = [imp for imp in analysis["imports"] if 
                     any(keyword in imp.lower() for keyword in ["pillow", "opencv", "ffmpeg"])]
    if media_imports:
        analysis["patterns"].append("MEDIA_PROCESSING")
        analysis["suggestions"].append("Crear utilidad de procesamiento multimedia")
    
    file_imports = [imp for imp in analysis["imports"] if 
                    any(keyword in imp.lower() for keyword in ["json", "csv", "yaml"])]
    if file_imports:
        analysis["patterns"].append("FILE_PROCESSING")
        analysis["suggestions"].append("Crear utilidad de procesamiento de archivos")
    
    return analysis

def main():
    parser = argparse.ArgumentParser(description="Analizar proyecto Python")
    parser.add_argument("project_path", help="Ruta al proyecto")
    parser.add_argument("-o", "--output", help="Archivo de salida JSON")
    
    args = parser.parse_args()
    
    analysis = analyze_project(args.project_path)
    
    print(f"\n{'='*50}")
    print(f"ANÁLISIS DE: {analysis['project_name']}")
    print(f"{'='*50}")
    print(f"Funciones encontradas: {len(analysis['functions'])}")
    print(f"Clases encontradas: {len(analysis['classes'])}")
    print(f"Imports únicos: {len(analysis['imports'])}")
    print(f"Patrones detectados: {', '.join(analysis['patterns'])}")
    
    print(f"\nSUGERENCIAS:")
    for suggestion in analysis['suggestions']:
        print(f"  • {suggestion}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\nAnálisis guardado en: {args.output}")

if __name__ == "__main__":
    main()
