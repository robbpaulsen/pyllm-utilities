#!/usr/bin/env python3
"""
Enhanced Synergy Analyzer - Identifica oportunidades de alto valor
"""
import json
import argparse
from pathlib import Path
from collections import defaultdict

class SmartSynergyAnalyzer:
    def __init__(self):
        self.content_creation_workflows = {
            "youtube_automation": {
                "name": "YouTube Content Automation Pipeline",
                "required_patterns": ["MEDIA_PROCESSING", "API_CLIENT"],
                "utilities": ["media-detail-extractor", "fast-pycaptioner", "content_scheduler"],
                "workflow": [
                    "1. Extraer metadatos de videos (media-detail-extractor)",
                    "2. Generar subtítulos automáticos (fast-pycaptioner)", 
                    "3. Programar publicación optimizada (content_scheduler)",
                    "4. Crear archivos SRT para biblioteca completa"
                ],
                "business_value": "HIGH",
                "implementation_complexity": "MEDIUM"
            },
            
            "podcast_automation": {
                "name": "Podcast Production Pipeline",
                "required_patterns": ["MEDIA_PROCESSING"],
                "utilities": ["tts-py", "media-stitcher", "content_scheduler"],
                "workflow": [
                    "1. Generar audio con TTS (tts-py)",
                    "2. Unir segmentos de audio (media-stitcher)",
                    "3. Programar publicación (content_scheduler)"
                ],
                "business_value": "HIGH", 
                "implementation_complexity": "LOW"
            },
            
            "visual_content_pipeline": {
                "name": "Visual Content Creation Pipeline",
                "required_patterns": ["MEDIA_PROCESSING"],
                "utilities": ["image-generation", "media-stitcher", "content_scheduler"],
                "workflow": [
                    "1. Generar imágenes (image-generation)",
                    "2. Crear videos con imágenes (media-stitcher)",
                    "3. Programar publicación (content_scheduler)"
                ],
                "business_value": "MEDIUM",
                "implementation_complexity": "MEDIUM"
            },
            
            "multimedia_content_factory": {
                "name": "Multimedia Content Factory",
                "required_patterns": ["MEDIA_PROCESSING", "FILE_PROCESSING"],
                "utilities": ["tts-py", "image-generation", "media-stitcher", "fast-pycaptioner"],
                "workflow": [
                    "1. Generar script y audio (tts-py)",
                    "2. Crear imágenes complementarias (image-generation)",
                    "3. Unir audio e imágenes en video (media-stitcher)",
                    "4. Generar subtítulos (fast-pycaptioner)"
                ],
                "business_value": "VERY_HIGH",
                "implementation_complexity": "HIGH"
            }
        }
    
    def analyze_utilities(self, analyses_dir):
        """Analiza utilidades y encuentra workflows de alto valor."""
        analyses_dir = Path(analyses_dir)
        analysis_files = list(analyses_dir.glob("*.json"))
        
        utilities = {}
        for file_path in analysis_files:
            with open(file_path) as f:
                data = json.load(f)
                utilities[data["project_name"]] = data
        
        print(f"Analizando {len(utilities)} utilidades para workflows de alto valor...")
        
        # Detectar workflows posibles
        possible_workflows = []
        available_utils = set(utilities.keys())
        
        for workflow_id, workflow in self.content_creation_workflows.items():
            required_utils = set(workflow["utilities"])
            available_required = required_utils & available_utils
            
            if len(available_required) >= 2:  # Al menos 2 utilidades del workflow
                missing_utils = required_utils - available_utils
                
                workflow_analysis = {
                    **workflow,
                    "id": workflow_id,
                    "available_utilities": list(available_required),
                    "missing_utilities": list(missing_utils),
                    "completion_percentage": len(available_required) / len(required_utils) * 100,
                    "immediate_value": len(available_required) >= 3
                }
                possible_workflows.append(workflow_analysis)
        
        # Identificar módulos base compartidos
        shared_modules = self._identify_shared_modules(utilities)
        
        # Generar recomendaciones priorizadas
        recommendations = self._generate_recommendations(possible_workflows, shared_modules, utilities)
        
        return {
            "workflows": possible_workflows,
            "shared_modules": shared_modules,
            "recommendations": recommendations,
            "utilities_analyzed": list(utilities.keys())
        }
    
    def _identify_shared_modules(self, utilities):
        """Identifica módulos que deberían ser compartidos."""
        shared_patterns = defaultdict(list)
        
        # Agrupar por patrones de imports comunes
        common_modules = ["argparse", "logging", "pathlib", "concurrent.futures", "os", "json"]
        
        for util_name, util_data in utilities.items():
            util_commons = [imp for imp in util_data.get("imports", []) if imp in common_modules]
            if len(util_commons) >= 3:
                shared_patterns["cli_utilities"].append(util_name)
        
        # Identificar utilidades de media
        media_keywords = ["media", "video", "audio", "image", "tts", "caption"]
        for util_name, util_data in utilities.items():
            if any(keyword in util_name.lower() for keyword in media_keywords):
                shared_patterns["media_processing"].append(util_name)
        
        return dict(shared_patterns)
    
    def _generate_recommendations(self, workflows, shared_modules, utilities):
        """Genera recomendaciones priorizadas."""
        recommendations = []
        
        # Priorizar workflows con alta completitud
        complete_workflows = [w for w in workflows if w["completion_percentage"] >= 75]
        incomplete_workflows = [w for w in workflows if 50 <= w["completion_percentage"] < 75]
        
        # Recomendaciones de alta prioridad
        for workflow in sorted(complete_workflows, key=lambda x: x["completion_percentage"], reverse=True):
            if workflow["immediate_value"]:
                recommendations.append({
                    "type": "IMMEDIATE_IMPLEMENTATION",
                    "priority": "HIGH",
                    "title": f"Implementar {workflow['name']}",
                    "description": f"Tienes {len(workflow['available_utilities'])} de {len(workflow['utilities'])} utilidades necesarias",
                    "utilities": workflow["available_utilities"],
                    "missing": workflow["missing_utilities"],
                    "workflow_steps": workflow["workflow"],
                    "business_value": workflow["business_value"],
                    "next_steps": self._generate_implementation_steps(workflow)
                })
        
        # Recomendaciones de módulo base
        if len(shared_modules.get("cli_utilities", [])) >= 3:
            recommendations.append({
                "type": "INFRASTRUCTURE",
                "priority": "MEDIUM",
                "title": "Crear módulo base CLI",
                "description": "Múltiples utilidades comparten patrones CLI similares",
                "utilities": shared_modules["cli_utilities"],
                "benefits": [
                    "Consistencia en interfaces de línea de comandos",
                    "Reducir código duplicado",
                    "Facilitar mantenimiento",
                    "Acelerar desarrollo de nuevas utilidades"
                ],
                "next_steps": [
                    "1. Extraer funciones comunes de CLI",
                    "2. Crear base_cli.py con argumentos estándar",
                    "3. Implementar logging y configuración unificados",
                    "4. Migrar utilidades existentes al módulo base"
                ]
            })
        
        # Recomendaciones para workflows incompletos
        for workflow in incomplete_workflows:
            recommendations.append({
                "type": "FUTURE_OPPORTUNITY", 
                "priority": "LOW",
                "title": f"Completar {workflow['name']}",
                "description": f"Faltan {len(workflow['missing_utilities'])} utilidades para workflow completo",
                "missing_utilities": workflow["missing_utilities"],
                "current_utilities": workflow["available_utilities"],
                "potential_value": workflow["business_value"]
            })
        
        return recommendations
    
    def _generate_implementation_steps(self, workflow):
        """Genera pasos específicos de implementación."""
        steps = [
            "1. Crear directorio del proyecto integrado",
            "2. Definir interface común entre utilidades",
            "3. Crear script orquestador principal",
            "4. Implementar manejo de errores entre pasos",
            "5. Agregar logging y monitoreo",
            "6. Crear configuración unificada",
            "7. Testear workflow completo"
        ]
        
        if workflow["id"] == "youtube_automation":
            steps.extend([
                "8. Integrar con YouTube Data API",
                "9. Implementar detección automática de videos sin subtítulos", 
                "10. Crear dashboard de progreso"
            ])
        elif workflow["id"] == "podcast_automation":
            steps.extend([
                "8. Integrar con plataformas de podcasts",
                "9. Implementar templates de episodios",
                "10. Agregar distribución multi-plataforma"
            ])
        
        return steps

def main():
    parser = argparse.ArgumentParser(description="Análisis inteligente de sinergias")
    parser.add_argument("analyses_dir", help="Directorio con archivos de análisis JSON")
    parser.add_argument("-o", "--output", help="Guardar análisis en archivo JSON")
    
    args = parser.parse_args()
    
    analyzer = SmartSynergyAnalyzer()
    analysis = analyzer.analyze_utilities(args.analyses_dir)
    
    print(f"\n{'='*80}")
    print("ANÁLISIS INTELIGENTE DE SINERGIAS - OPORTUNIDADES DE ALTO VALOR")
    print(f"{'='*80}")
    
    print(f"\nUtilidades analizadas: {', '.join(analysis['utilities_analyzed'])}")
    
    print(f"\n🚀 WORKFLOWS DISPONIBLES:")
    print("-" * 50)
    for workflow in analysis["workflows"]:
        status = "✅ LISTO PARA IMPLEMENTAR" if workflow["immediate_value"] else "🔄 EN DESARROLLO"
        print(f"\n{workflow['name']} - {status}")
        print(f"   Completitud: {workflow['completion_percentage']:.0f}%")
        print(f"   Disponibles: {', '.join(workflow['available_utilities'])}")
        if workflow["missing_utilities"]:
            print(f"   Faltantes: {', '.join(workflow['missing_utilities'])}")
        print(f"   Valor de negocio: {workflow['business_value']}")
    
    print(f"\n💡 RECOMENDACIONES PRIORIZADAS:")
    print("-" * 50)
    for i, rec in enumerate(analysis["recommendations"], 1):
        priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        print(f"\n{i}. {priority_emoji[rec['priority']]} {rec['title']}")
        print(f"   {rec['description']}")
        if rec["type"] == "IMMEDIATE_IMPLEMENTATION":
            print(f"   Utilidades: {', '.join(rec['utilities'])}")
            print(f"   Próximos pasos:")
            for step in rec["next_steps"][:3]:
                print(f"     • {step}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\nAnálisis completo guardado en: {args.output}")

if __name__ == "__main__":
    main()
