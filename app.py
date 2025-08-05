from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import json
from datetime import datetime
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
import os
from dotenv import load_dotenv
from datetime import datetime
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

# Cargar variables de entorno
load_dotenv()

# Debug temporal - agrega estas líneas
print("=== DEBUG NOTION CONFIG ===")
print(f"NOTION_TOKEN: {os.getenv('NOTION_TOKEN')[:20]}..." if os.getenv('NOTION_TOKEN') else "NOTION_TOKEN: None")
print(f"NOTION_DATABASE_ID: {os.getenv('NOTION_DATABASE_ID')}")
print("========================")

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave segura

# Configuración de Notion
NOTION_TOKEN = os.getenv('NOTION_TOKEN', 'tu_token_de_notion_aqui')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID', 'tu_database_id_aqui')

@dataclass
class PoCEvaluationCriteria:
    """Criterios específicos basados en tu esquema de Notion"""
    tiempo_cierre_comercial: int      # 1️⃣=1, 2️⃣=2, 3️⃣=3
    recursos_preventa: int            # 1️⃣=1, 2️⃣=2, 3️⃣=3
    historial_cliente: int            # 1️⃣=1, 2️⃣=2, 3️⃣=3
    competencia_directa: int          # 1️⃣=1, 2️⃣=2, 3️⃣=3
    madurez_cliente: int              # 1️⃣=1, 2️⃣=2, 3️⃣=3
    naturaleza_poc: int               # 1️⃣=1, 2️⃣=2, 3️⃣=3
    sponsor_ejecutivo: int            # 1️⃣=1, 2️⃣=2, 3️⃣=3
    compromiso_cliente: int           # 1️⃣=1, 2️⃣=2, 3️⃣=3
    complejidad_tecnica: int          # 1️⃣=1, 2️⃣=2, 3️⃣=3
    monto_proyecto: int               # 1️⃣=1, 2️⃣=2, 3️⃣=3
    potencial_comercial: int          # 1️⃣=1, 2️⃣=2, 3️⃣=3
    poc_definida: int                 # 1️⃣=1, 2️⃣=2, 3️⃣=3
    plazo_ejecucion: int              # 1️⃣=1, 2️⃣=2, 3️⃣=3
    entorno_pruebas: int              # 1️⃣=1, 2️⃣=2, 3️⃣=3
    presupuesto_definido: int         # 1️⃣=1, 2️⃣=2, 3️⃣=3

class FortinetPoCEvaluator:
    """Evaluador específico para PoCs Fortinet basado en tu matriz de evaluación"""
    
    def __init__(self):
        self.proyectos_fortinet = [
            'SD-WAN', 'SASE', 'Firewall', 'VPN', 'FortiGate', 'FortiSASE', 
            'FortiClient', 'FortiManager', 'FortiAnalyzer', 'FortiSIEM',
            'FortiEDR', 'FortiNAC', 'Zero Trust', 'Security Fabric'
        ]
        
        # Lista de responsables de preventa
        self.responsables_preventa = [
            'Josué Temich',
            'Alexis Millan',
            'Luis Mata', 
            'Lucy Terrazas',
            'Gabriel Lopez',
            'Antonio Mendoza',
            'Edgar Cantu',
            'Esau Ruiz',
            'Joel Rodriguez',
	    'Joel Garza',
	    'Otro SE...'
        ]
	# Criterios de evaluación según tu esquema
        self.evaluation_options = {
            'tiempo_cierre_comercial': {
                1: '1️⃣ <30 días estimados',
                2: '2️⃣ 1-3 meses estimados', 
                3: '3️⃣ >3 meses o indefinido'
            },
            'recursos_preventa': {
                1: '1️⃣ <1 día de esfuerzo',
                2: '2️⃣ 1–3 días de esfuerzo',
                3: '3️⃣ >3 días o múltiples áreas'
            },
            'historial_cliente': {
                1: '1️⃣ Cliente establecido con compras previas',
                2: '2️⃣ Cliente conocido sin compras recientes',
                3: '3️⃣ Cliente nuevo o sin potencial claro'
            },
            'competencia_directa': {
                1: '1️⃣ Somos incumbentes/favoritos',
                2: '2️⃣ Competimos en igualdad',
                3: '3️⃣ Solo buscan benchmark'
            },
            'madurez_cliente': {
                1: '1️⃣ Conocen y usan algo similar',
                2: '2️⃣ Parcial o básico',
                3: '3️⃣ Sin experiencia'
            },
            'naturaleza_poc': {
                1: '1️⃣ Validación específica',
                2: '2️⃣ Comparación técnica',
                3: '3️⃣ Curiosidad técnica'
            },
            'sponsor_ejecutivo': {
                1: '1️⃣ Activo y comprometido',
                2: '2️⃣ Pasivo o externo',
                3: '3️⃣ Inexistente'
            },
            'compromiso_cliente': {
                1: '1️⃣ Equipo dedicado',
                2: '2️⃣ Solo uno disponible',
                3: '3️⃣ Nadie asignado o ausente'
            },
            'complejidad_tecnica': {
                1: '1️⃣ Baja: configuración estándar',
                2: '2️⃣ Media: requiere customización',
                3: '3️⃣ Alta: tecnología nueva y compleja'
            },
            'monto_proyecto': {
                1: '1️⃣ >$100K con compromiso firme',
                2: '2️⃣ $10K-$100K con interés real',
                3: '3️⃣ <$10K o sin promesa de compra'
            },
            'potencial_comercial': {
                1: '1️⃣ Proyecto definido con presupuesto',
                2: '2️⃣ Interés real pero sin presupuesto',
                3: '3️⃣ Sin proyecto real / exploratorio'
            },
            'poc_definida': {
                1: '1️⃣ Criterios claros y documentados',
                2: '2️⃣ Parcial / sin criterios claros',
                3: '3️⃣ Todo verbal o indefinido'
            },
            'plazo_ejecucion': {
                1: '1️⃣ Adecuado con recursos disponibles',
                2: '2️⃣ Justo pero factible',
                3: '3️⃣ Imposible o fuera de alcance'
            },
            'entorno_pruebas': {
                1: '1️⃣ Lab dedicado disponible',
                2: '2️⃣ Ambiente de desarrollo',
                3: '3️⃣ 100% en producción'
            },
            'presupuesto_definido': {
                1: '1️⃣ Presupuesto aprobado y disponible',
                2: '2️⃣ En proceso de aprobación',
                3: '3️⃣ No existe presupuesto definido'
            }
        }
        
    def calculate_scores(self, criteria: PoCEvaluationCriteria) -> Dict:
        """Calcula puntuaciones de eficiencia y riesgo según tu metodología"""
        
        # Criterios de EFICIENCIA (menor puntaje = mayor eficiencia)
        eficiencia_criteria = [
            criteria.tiempo_cierre_comercial,
            criteria.recursos_preventa, 
            criteria.monto_proyecto,
            criteria.potencial_comercial,
            criteria.poc_definida,
            criteria.plazo_ejecucion,
            criteria.entorno_pruebas,
            criteria.presupuesto_definido
        ]
        
        # Criterios de RIESGO (menor puntaje = menor riesgo)
        riesgo_criteria = [
            criteria.historial_cliente,
            criteria.competencia_directa,
            criteria.madurez_cliente,
            criteria.naturaleza_poc,
            criteria.sponsor_ejecutivo,
            criteria.compromiso_cliente,
            criteria.complejidad_tecnica
        ]
        
        eficiencia_total = sum(eficiencia_criteria)
        riesgo_total = sum(riesgo_criteria)
        
        # Clasificación de niveles según tu esquema
        def get_eficiencia_level(score):
            if score <= 10:
                return "🏆 Alta"
            elif score <= 16:
                return "⚖️ Media"
            else:
                return "🕳️ Baja"
                
        def get_riesgo_level(score):
            if score <= 10:
                return "✅ Bajo"
            elif score <= 14:
                return "⚠️ Medio"
            else:
                return "❌ Alto"
                
        nivel_eficiencia = get_eficiencia_level(eficiencia_total)
        nivel_riesgo = get_riesgo_level(riesgo_total)
        
        # Semáforo según tu lógica
        def get_semaforo(eficiencia_score, riesgo_score):
            if riesgo_score <= 10 and eficiencia_score <= 10:
                return "🟢 Ideal: Bajo riesgo y alta eficiencia"
            elif riesgo_score <= 10 and eficiencia_score <= 16:
                return "🟡 Bueno: Bajo riesgo con eficiencia media"
            elif riesgo_score <= 14 and eficiencia_score <= 10:
                return "🟡 Aceptable: Riesgo medio pero alta eficiencia"
            elif riesgo_score <= 14 and eficiencia_score <= 16:
                return "🟠 Cuidado: Riesgo y eficiencia medios"
            elif riesgo_score > 14 and eficiencia_score <= 16:
                return "🟠 Alto riesgo con eficiencia media: evaluar con cuidado"
            else:
                return "🔴 Crítico: Alto riesgo y baja eficiencia"
        
        semaforo = get_semaforo(eficiencia_total, riesgo_total)
        
        return {
            'eficiencia_total': eficiencia_total,
            'nivel_eficiencia': nivel_eficiencia,
            'riesgo_total': riesgo_total,
            'nivel_riesgo': nivel_riesgo,
            'semaforo': semaforo
        }
    
    def get_recommendations(self, criteria: PoCEvaluationCriteria, scores: Dict) -> List[str]:
        """Genera recomendaciones específicas basadas en las puntuaciones"""
        recommendations = []
        
        # Recomendaciones basadas en criterios específicos
        if criteria.poc_definida >= 3:
            recommendations.append("📋 CRÍTICO: Definir criterios claros de éxito para la PoC antes de proceder")
            
        if criteria.sponsor_ejecutivo >= 3:
            recommendations.append("👔 Identificar y comprometer un sponsor ejecutivo del cliente")
            
        if criteria.compromiso_cliente >= 3:
            recommendations.append("🤝 Asegurar dedicación de recursos técnicos del cliente")
            
        if criteria.presupuesto_definido >= 3:
            recommendations.append("💰 Validar existencia y disponibilidad de presupuesto")
            
        if criteria.complejidad_tecnica >= 3:
            recommendations.append("⚙️ Evaluar complejidad técnica y recursos internos necesarios")
            
        if criteria.entorno_pruebas >= 3:
            recommendations.append("🧪 Negociar ambiente de pruebas adecuado (no producción)")
            
        # Recomendaciones según semáforo
        if "Crítico" in scores['semaforo']:
            recommendations.append("🚨 NO RECOMENDADO: Considerar declinar esta PoC")
        elif "Alto riesgo" in scores['semaforo']:
            recommendations.append("⚠️ Proceder con extrema cautela y aprobación gerencial")
        elif "Ideal" in scores['semaforo']:
            recommendations.append("✨ PoC RECOMENDADA: Condiciones óptimas para el éxito")
            
        return recommendations

# Instancia del evaluador
evaluator = FortinetPoCEvaluator()

def send_to_notion(data: Dict) -> bool:
    """Envía los datos a tu base de datos de Notion con la estructura exacta"""
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    
    # Mapear valores a formato de tu BD
    def map_select_value(field_name, value):
        return evaluator.evaluation_options[field_name][int(value)]
    
    # Estructura de datos para Notion (SOLO campos editables)
    notion_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Cliente": {
                "title": [{"text": {"content": data.get('cliente', '')}}]
            },
            "Proyecto": {
                "select": {"name": data.get('proyecto', '')}
            },
            "Responsable Preventa": {
                "select": {"name": data.get('responsable_preventa', 'Josué Temich')}
            },
            "Fecha de evaluación": {
                "date": {"start": datetime.now().isoformat().split('T')[0]}
            },
            "Estado": {
                "status": {"name": "Planeación"}
            },
            "Tiempo para cierre comercial": {
                "select": {"name": map_select_value('tiempo_cierre_comercial', data.get('tiempo_cierre_comercial', 3))}
            },
            "Recursos preventa requeridos": {
                "select": {"name": map_select_value('recursos_preventa', data.get('recursos_preventa', 3))}
            },
            "Historial con el cliente": {
                "select": {"name": map_select_value('historial_cliente', data.get('historial_cliente', 3))}
            },
            "Competencia directa": {
                "select": {"name": map_select_value('competencia_directa', data.get('competencia_directa', 3))}
            },
            "Madurez del cliente": {
                "select": {"name": map_select_value('madurez_cliente', data.get('madurez_cliente', 3))}
            },
            "Naturaleza del PoC": {
                "select": {"name": map_select_value('naturaleza_poc', data.get('naturaleza_poc', 3))}
            },
            "Sponsor ejecutivo": {
                "select": {"name": map_select_value('sponsor_ejecutivo', data.get('sponsor_ejecutivo', 3))}
            },
            "Compromiso del cliente": {
                "select": {"name": map_select_value('compromiso_cliente', data.get('compromiso_cliente', 3))}
            },
            "Complejidad técnica": {
                "select": {"name": map_select_value('complejidad_tecnica', data.get('complejidad_tecnica', 3))}
            },
            "Monto del proyecto": {
                "select": {"name": map_select_value('monto_proyecto', data.get('monto_proyecto', 3))}
            },
            "Potencial comercial": {
                "select": {"name": map_select_value('potencial_comercial', data.get('potencial_comercial', 3))}
            },
            "PoC bien definida": {
                "select": {"name": map_select_value('poc_definida', data.get('poc_definida', 3))}
            },
            "Plazo de ejecución": {
                "select": {"name": map_select_value('plazo_ejecucion', data.get('plazo_ejecucion', 3))}
            },
            "Entorno de pruebas": {
                "select": {"name": map_select_value('entorno_pruebas', data.get('entorno_pruebas', 3))}
            },
            "Presupuesto definido": {
                "select": {"name": map_select_value('presupuesto_definido', data.get('presupuesto_definido', 3))}
            },
            "Eficiencia_total": {
                "number": data.get('eficiencia_total', 0)
            },
            "Riesgo_total": {
                "number": data.get('riesgo_total', 0)
            }
            # REMOVER: Los campos Nivel Eficiencia, Nivel Riesgo y Semáforo 
            # son fórmulas y se calculan automáticamente en Notion
        }
    }
    
    try:
        response = requests.post(
            'https://api.notion.com/v1/pages',
            headers=headers,
            json=notion_data
        )
        
        if response.status_code == 200:
            logger.info("PoC evaluada y guardada exitosamente en Notion")
            return True
        else:
            logger.error(f"Error al enviar a Notion: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Excepción al enviar a Notion: {str(e)}")
        return False
    
    # Mapear valores a formato de tu BD
    def map_select_value(field_name, value):
        return evaluator.evaluation_options[field_name][value]
    
    # Estructura de datos para Notion (según tu esquema exacto)
    notion_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Cliente": {
                "title": [{"text": {"content": data.get('cliente', '')}}]
            },
            "Proyecto": {
                "select": {"name": data.get('proyecto', '')}
            },
            "Responsable Preventa": {
                "select": {"name": data.get('responsable_preventa', '')}
            },
            "Fecha de evaluación": {
                "date": {"start": datetime.now().isoformat().split('T')[0]}
            },
            "Estado": {
                "status": {"name": "Planeación"}
            },
            "Tiempo para cierre comercial": {
                "select": {"name": map_select_value('tiempo_cierre_comercial', data.get('tiempo_cierre_comercial', 3))}
            },
            "Recursos preventa requeridos": {
                "select": {"name": map_select_value('recursos_preventa', data.get('recursos_preventa', 3))}
            },
            "Historial con el cliente": {
                "select": {"name": map_select_value('historial_cliente', data.get('historial_cliente', 3))}
            },
            "Competencia directa": {
                "select": {"name": map_select_value('competencia_directa', data.get('competencia_directa', 3))}
            },
            "Madurez del cliente": {
                "select": {"name": map_select_value('madurez_cliente', data.get('madurez_cliente', 3))}
            },
            "Naturaleza del PoC": {
                "select": {"name": map_select_value('naturaleza_poc', data.get('naturaleza_poc', 3))}
            },
            "Sponsor ejecutivo": {
                "select": {"name": map_select_value('sponsor_ejecutivo', data.get('sponsor_ejecutivo', 3))}
            },
            "Compromiso del cliente": {
                "select": {"name": map_select_value('compromiso_cliente', data.get('compromiso_cliente', 3))}
            },
            "Complejidad técnica": {
                "select": {"name": map_select_value('complejidad_tecnica', data.get('complejidad_tecnica', 3))}
            },
            "Monto del proyecto": {
                "select": {"name": map_select_value('monto_proyecto', data.get('monto_proyecto', 3))}
            },
            "Potencial comercial": {
                "select": {"name": map_select_value('potencial_comercial', data.get('potencial_comercial', 3))}
            },
            "PoC bien definida": {
                "select": {"name": map_select_value('poc_definida', data.get('poc_definida', 3))}
            },
            "Plazo de ejecución": {
                "select": {"name": map_select_value('plazo_ejecucion', data.get('plazo_ejecucion', 3))}
            },
            "Entorno de pruebas": {
                "select": {"name": map_select_value('entorno_pruebas', data.get('entorno_pruebas', 3))}
            },
            "Presupuesto definido": {
                "select": {"name": map_select_value('presupuesto_definido', data.get('presupuesto_definido', 3))}
            },
            "Eficiencia_total": {
                "number": data.get('eficiencia_total', 0)
            },
            "Nivel Eficiencia": {
                "formula": {}  # Se calcula automáticamente en Notion
            },
            "Riesgo_total": {
                "number": data.get('riesgo_total', 0)
            },
            "Nivel Riesgo": {
                "formula": {}  # Se calcula automáticamente en Notion
            },
            "Semáforo": {
                "formula": {}  # Se calcula automáticamente en Notion
            }
        }
    }
    
    try:
        response = requests.post(
            'https://api.notion.com/v1/pages',
            headers=headers,
            json=notion_data
        )
        
        if response.status_code == 200:
            logger.info("PoC evaluada y guardada exitosamente en Notion")
            return True
        else:
            logger.error(f"Error al enviar a Notion: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Excepción al enviar a Notion: {str(e)}")
        return False

@app.route('/')
def index():
    """Página principal con el formulario de evaluación"""
    return render_template('evaluation_form.html', 
                         evaluator=evaluator)

@app.route('/evaluate', methods=['POST'])
def evaluate_poc():
    """Procesa la evaluación de la PoC"""
    try:
        # Obtener datos del formulario
        form_data = request.form.to_dict()
        
        # Crear objeto de criterios de evaluación
        criteria = PoCEvaluationCriteria(
            tiempo_cierre_comercial=int(form_data.get('tiempo_cierre_comercial', 3)),
            recursos_preventa=int(form_data.get('recursos_preventa', 3)),
            historial_cliente=int(form_data.get('historial_cliente', 3)),
            competencia_directa=int(form_data.get('competencia_directa', 3)),
            madurez_cliente=int(form_data.get('madurez_cliente', 3)),
            naturaleza_poc=int(form_data.get('naturaleza_poc', 3)),
            sponsor_ejecutivo=int(form_data.get('sponsor_ejecutivo', 3)),
            compromiso_cliente=int(form_data.get('compromiso_cliente', 3)),
            complejidad_tecnica=int(form_data.get('complejidad_tecnica', 3)),
            monto_proyecto=int(form_data.get('monto_proyecto', 3)),
            potencial_comercial=int(form_data.get('potencial_comercial', 3)),
            poc_definida=int(form_data.get('poc_definida', 3)),
            plazo_ejecucion=int(form_data.get('plazo_ejecucion', 3)),
            entorno_pruebas=int(form_data.get('entorno_pruebas', 3)),
            presupuesto_definido=int(form_data.get('presupuesto_definido', 3))
        )
        
        # Calcular puntuaciones
        scores = evaluator.calculate_scores(criteria)
        recommendations = evaluator.get_recommendations(criteria, scores)
        
        # Preparar datos para Notion
        notion_data = {
            **form_data,
            **scores,
            **{k: v for k, v in criteria.__dict__.items()}
        }
        
        # Enviar a Notion
        success = send_to_notion(notion_data)
        
        if success:
            flash('¡PoC evaluada y guardada exitosamente en Notion!', 'success')
        else:
            flash('PoC evaluada pero error al guardar en Notion. Revisa la configuración.', 'warning')
        
        # Agregar fecha actual
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        return render_template('evaluation_results.html', 
                             scores=scores,
                             recommendations=recommendations,
                             form_data=form_data,
                             criteria=criteria,
                             evaluator=evaluator,
                             current_date=current_date)
                             
    except Exception as e:
        logger.error(f"Error en evaluación: {str(e)}")
        flash(f'Error al procesar la evaluación: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    """API endpoint para evaluación programática"""
    try:
        data = request.get_json()
        
        criteria = PoCEvaluationCriteria(**{k: data.get(k, 3) for k in PoCEvaluationCriteria.__annotations__.keys()})
        scores = evaluator.calculate_scores(criteria)
        recommendations = evaluator.get_recommendations(criteria, scores)
        
        return jsonify({
            'scores': scores,
            'recommendations': recommendations,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 400
@app.route('/cliente/<string:nombre_cliente>')
def historial_cliente(nombre_cliente):
    """Ver historial de evaluaciones de un cliente específico"""
    try:
        headers = {
            'Authorization': f'Bearer {NOTION_TOKEN}',
            'Notion-Version': '2022-06-28'
        }
        
        # Buscar todas las PoCs de este cliente
        response = requests.post(
            f'https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query',
            headers=headers,
            json={
                "filter": {
                    "property": "Cliente",
                    "title": {
                        "contains": nombre_cliente
                    }
                },
                "sorts": [
                    {
                        "property": "Fecha de evaluación",
                        "direction": "descending"
                    }
                ]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            evaluaciones = []
            
            for page in data.get('results', []):
                props = page.get('properties', {})
                
                # Calcular semáforo basado en los scores
                eficiencia = props.get('Eficiencia_total', {}).get('number', 0)
                riesgo = props.get('Riesgo_total', {}).get('number', 0)
                
                # Aplicar tu lógica de semáforo
                if riesgo <= 10 and eficiencia <= 10:
                    semaforo = "🟢 Ideal"
                    color_class = "success"
                elif riesgo <= 10 and eficiencia <= 16:
                    semaforo = "🟡 Bueno"
                    color_class = "warning"
                elif riesgo <= 14 and eficiencia <= 10:
                    semaforo = "🟡 Aceptable"
                    color_class = "warning"
                elif riesgo <= 14 and eficiencia <= 16:
                    semaforo = "🟠 Cuidado"
                    color_class = "orange"
                elif riesgo > 14 and eficiencia <= 16:
                    semaforo = "🟠 Alto riesgo"
                    color_class = "orange"
                else:
                    semaforo = "🔴 Crítico"
                    color_class = "danger"
                
                evaluacion = {
                    'id': page.get('id'),
                    'cliente': props.get('Cliente', {}).get('title', [{}])[0].get('text', {}).get('content', ''),
                    'proyecto': props.get('Proyecto', {}).get('select', {}).get('name', ''),
                    'responsable': props.get('Responsable Preventa', {}).get('select', {}).get('name', ''),
                    'fecha': props.get('Fecha de evaluación', {}).get('date', {}).get('start', ''),
                    'eficiencia_total': eficiencia,
                    'riesgo_total': riesgo,
                    'semaforo': semaforo,
                    'color_class': color_class,
                    'estado': props.get('Estado', {}).get('status', {}).get('name', ''),
                }
                evaluaciones.append(evaluacion)
            
            return render_template('historial_cliente.html', 
                                 cliente=nombre_cliente, 
                                 evaluaciones=evaluaciones,
                                 evaluator=evaluator)
        else:
            flash('Error al obtener historial del cliente', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error en historial cliente: {str(e)}")
        flash(f'Error al cargar historial: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/buscar_cliente', methods=['POST'])
def buscar_cliente():
    """Buscar evaluaciones de un cliente"""
    cliente = request.form.get('cliente_buscar', '').strip()
    if cliente:
        return redirect(url_for('historial_cliente', nombre_cliente=cliente))
    else:
        flash('Por favor ingrese un nombre de cliente', 'warning')
        return redirect(url_for('index'))

@app.route('/editar/<string:notion_page_id>')
def editar_evaluacion(notion_page_id):
    """Cargar evaluación existente para editar"""
    try:
        headers = {
            'Authorization': f'Bearer {NOTION_TOKEN}',
            'Notion-Version': '2022-06-28'
        }
        
        # Obtener la página específica de Notion
        response = requests.get(
            f'https://api.notion.com/v1/pages/{notion_page_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            page_data = response.json()
            props = page_data.get('properties', {})
            
            # Mapear datos de Notion de vuelta al formulario
            def reverse_map_value(field_name, notion_value):
                option_text = notion_value.get('select', {}).get('name', '')
                for key, text in evaluator.evaluation_options[field_name].items():
                    if text == option_text:
                        return key
                return 3  # Default
            
            # Extraer datos para prellenar el formulario
            evaluacion_data = {
                'cliente': props.get('Cliente', {}).get('title', [{}])[0].get('text', {}).get('content', ''),
                'proyecto': props.get('Proyecto', {}).get('select', {}).get('name', ''),
                'responsable_preventa': props.get('Responsable Preventa', {}).get('select', {}).get('name', ''),
                'descripcion': '',  # No se guarda en Notion actualmente
                'tiempo_cierre_comercial': reverse_map_value('tiempo_cierre_comercial', props.get('Tiempo para cierre comercial', {})),
                'recursos_preventa': reverse_map_value('recursos_preventa', props.get('Recursos preventa requeridos', {})),
                'historial_cliente': reverse_map_value('historial_cliente', props.get('Historial con el cliente', {})),
                'competencia_directa': reverse_map_value('competencia_directa', props.get('Competencia directa', {})),
                'madurez_cliente': reverse_map_value('madurez_cliente', props.get('Madurez del cliente', {})),
                'naturaleza_poc': reverse_map_value('naturaleza_poc', props.get('Naturaleza del PoC', {})),
                'sponsor_ejecutivo': reverse_map_value('sponsor_ejecutivo', props.get('Sponsor ejecutivo', {})),
                'compromiso_cliente': reverse_map_value('compromiso_cliente', props.get('Compromiso del cliente', {})),
                'complejidad_tecnica': reverse_map_value('complejidad_tecnica', props.get('Complejidad técnica', {})),
                'monto_proyecto': reverse_map_value('monto_proyecto', props.get('Monto del proyecto', {})),
                'potencial_comercial': reverse_map_value('potencial_comercial', props.get('Potencial comercial', {})),
                'poc_definida': reverse_map_value('poc_definida', props.get('PoC bien definida', {})),
                'plazo_ejecucion': reverse_map_value('plazo_ejecucion', props.get('Plazo de ejecución', {})),
                'entorno_pruebas': reverse_map_value('entorno_pruebas', props.get('Entorno de pruebas', {})),
                'presupuesto_definido': reverse_map_value('presupuesto_definido', props.get('Presupuesto definido', {})),
                'notion_page_id': notion_page_id,  # Para saber que es una edición
                'fecha_original': props.get('Fecha de evaluación', {}).get('date', {}).get('start', '')
            }
            
            return render_template('evaluation_form.html', 
                                 evaluator=evaluator,
                                 edit_data=evaluacion_data,
                                 is_edit=True)
        else:
            flash('Error al cargar evaluación para editar', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error al cargar evaluación: {str(e)}")
        flash(f'Error al cargar evaluación: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/actualizar', methods=['POST'])
def actualizar_evaluacion():
    """Actualizar evaluación existente y crear entrada de timeline"""
    try:
        form_data = request.form.to_dict()
        notion_page_id = form_data.get('notion_page_id')
        
        if not notion_page_id:
            flash('Error: ID de evaluación no encontrado', 'error')
            return redirect(url_for('index'))
        
        # Crear objeto de criterios
        criteria = PoCEvaluationCriteria(
            tiempo_cierre_comercial=int(form_data.get('tiempo_cierre_comercial', 3)),
            recursos_preventa=int(form_data.get('recursos_preventa', 3)),
            historial_cliente=int(form_data.get('historial_cliente', 3)),
            competencia_directa=int(form_data.get('competencia_directa', 3)),
            madurez_cliente=int(form_data.get('madurez_cliente', 3)),
            naturaleza_poc=int(form_data.get('naturaleza_poc', 3)),
            sponsor_ejecutivo=int(form_data.get('sponsor_ejecutivo', 3)),
            compromiso_cliente=int(form_data.get('compromiso_cliente', 3)),
            complejidad_tecnica=int(form_data.get('complejidad_tecnica', 3)),
            monto_proyecto=int(form_data.get('monto_proyecto', 3)),
            potencial_comercial=int(form_data.get('potencial_comercial', 3)),
            poc_definida=int(form_data.get('poc_definida', 3)),
            plazo_ejecucion=int(form_data.get('plazo_ejecucion', 3)),
            entorno_pruebas=int(form_data.get('entorno_pruebas', 3)),
            presupuesto_definido=int(form_data.get('presupuesto_definido', 3))
        )
        
        # Calcular nuevas puntuaciones
        scores = evaluator.calculate_scores(criteria)
        recommendations = evaluator.get_recommendations(criteria, scores)
        
        # Actualizar el registro existente en Notion
        success = update_notion_record(notion_page_id, {
            **form_data,
            **scores,
            **{k: v for k, v in criteria.__dict__.items()}
        })
        
        # Crear entrada de timeline (nuevo registro)
        timeline_success = create_timeline_entry({
            **form_data,
            **scores,
            **{k: v for k, v in criteria.__dict__.items()},
            'fecha_original': form_data.get('fecha_original', ''),
            'tipo_actualizacion': 'Reevaluación'
        })
        
        if success:
            flash('¡Evaluación actualizada exitosamente! Se creó entrada en el timeline.', 'success')
        else:
            flash('Evaluación procesada pero error al actualizar en Notion.', 'warning')
        
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        return render_template('evaluation_results.html', 
                             scores=scores,
                             recommendations=recommendations,
                             form_data=form_data,
                             criteria=criteria,
                             evaluator=evaluator,
                             current_date=current_date,
                             is_update=True)
                             
    except Exception as e:
        logger.error(f"Error en actualización: {str(e)}")
        flash(f'Error al actualizar evaluación: {str(e)}', 'error')
        return redirect(url_for('index'))

def update_notion_record(page_id, data):
    """Actualizar registro existente en Notion"""
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    
    def map_select_value(field_name, value):
        return evaluator.evaluation_options[field_name][value]
    
    # Estructura para actualizar (PATCH)
    notion_data = {
        "properties": {
            "Fecha de evaluación": {
                "date": {"start": datetime.now().isoformat().split('T')[0]}
            },
            "Estado": {
                "status": {"name": "Actualizado"}
            },
            "Tiempo para cierre comercial": {
                "select": {"name": map_select_value('tiempo_cierre_comercial', data.get('tiempo_cierre_comercial', 3))}
            },
            "Recursos preventa requeridos": {
                "select": {"name": map_select_value('recursos_preventa', data.get('recursos_preventa', 3))}
            },
            "Historial con el cliente": {
                "select": {"name": map_select_value('historial_cliente', data.get('historial_cliente', 3))}
            },
            "Competencia directa": {
                "select": {"name": map_select_value('competencia_directa', data.get('competencia_directa', 3))}
            },
            "Madurez del cliente": {
                "select": {"name": map_select_value('madurez_cliente', data.get('madurez_cliente', 3))}
            },
            "Naturaleza del PoC": {
                "select": {"name": map_select_value('naturaleza_poc', data.get('naturaleza_poc', 3))}
            },
            "Sponsor ejecutivo": {
                "select": {"name": map_select_value('sponsor_ejecutivo', data.get('sponsor_ejecutivo', 3))}
            },
            "Compromiso del cliente": {
                "select": {"name": map_select_value('compromiso_cliente', data.get('compromiso_cliente', 3))}
            },
            "Complejidad técnica": {
                "select": {"name": map_select_value('complejidad_tecnica', data.get('complejidad_tecnica', 3))}
            },
            "Monto del proyecto": {
                "select": {"name": map_select_value('monto_proyecto', data.get('monto_proyecto', 3))}
            },
            "Potencial comercial": {
                "select": {"name": map_select_value('potencial_comercial', data.get('potencial_comercial', 3))}
            },
            "PoC bien definida": {
                "select": {"name": map_select_value('poc_definida', data.get('poc_definida', 3))}
            },
            "Plazo de ejecución": {
                "select": {"name": map_select_value('plazo_ejecucion', data.get('plazo_ejecucion', 3))}
            },
            "Entorno de pruebas": {
                "select": {"name": map_select_value('entorno_pruebas', data.get('entorno_pruebas', 3))}
            },
            "Presupuesto definido": {
                "select": {"name": map_select_value('presupuesto_definido', data.get('presupuesto_definido', 3))}
            },
            "Eficiencia_total": {
                "number": data.get('eficiencia_total', 0)
            },
            "Riesgo_total": {
                "number": data.get('riesgo_total', 0)
            }
        }
    }
    
    try:
        response = requests.patch(
            f'https://api.notion.com/v1/pages/{page_id}',
            headers=headers,
            json=notion_data
        )
        
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error al actualizar Notion: {str(e)}")
        return False

def create_timeline_entry(data):
    """Crear nueva entrada en timeline (copia con fecha actual)"""
    # Usar la función send_to_notion existente pero con datos de timeline
    timeline_data = data.copy()
    timeline_data['cliente'] = f"{data.get('cliente', '')} - Timeline"
    
    return send_to_notion(timeline_data)

# Agregar estas rutas después de las existentes en app.py

@app.route('/editar/<string:notion_page_id>')
def editar_evaluacion(notion_page_id):
    """Cargar evaluación existente para editar"""
    try:
        headers = {
            'Authorization': f'Bearer {NOTION_TOKEN}',
            'Notion-Version': '2022-06-28'
        }
        
        # Obtener la página específica de Notion
        response = requests.get(
            f'https://api.notion.com/v1/pages/{notion_page_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            page_data = response.json()
            props = page_data.get('properties', {})
            
            # Mapear datos de Notion de vuelta al formulario
            def reverse_map_value(field_name, notion_value):
                option_text = notion_value.get('select', {}).get('name', '')
                for key, text in evaluator.evaluation_options[field_name].items():
                    if text == option_text:
                        return key
                return 3  # Default
            
            # Extraer datos para prellenar el formulario
            evaluacion_data = {
                'cliente': props.get('Cliente', {}).get('title', [{}])[0].get('text', {}).get('content', ''),
                'proyecto': props.get('Proyecto', {}).get('select', {}).get('name', ''),
                'responsable_preventa': props.get('Responsable Preventa', {}).get('select', {}).get('name', ''),
                'descripcion': '',  # No se guarda en Notion actualmente
                'tiempo_cierre_comercial': reverse_map_value('tiempo_cierre_comercial', props.get('Tiempo para cierre comercial', {})),
                'recursos_preventa': reverse_map_value('recursos_preventa', props.get('Recursos preventa requeridos', {})),
                'historial_cliente': reverse_map_value('historial_cliente', props.get('Historial con el cliente', {})),
                'competencia_directa': reverse_map_value('competencia_directa', props.get('Competencia directa', {})),
                'madurez_cliente': reverse_map_value('madurez_cliente', props.get('Madurez del cliente', {})),
                'naturaleza_poc': reverse_map_value('naturaleza_poc', props.get('Naturaleza del PoC', {})),
                'sponsor_ejecutivo': reverse_map_value('sponsor_ejecutivo', props.get('Sponsor ejecutivo', {})),
                'compromiso_cliente': reverse_map_value('compromiso_cliente', props.get('Compromiso del cliente', {})),
                'complejidad_tecnica': reverse_map_value('complejidad_tecnica', props.get('Complejidad técnica', {})),
                'monto_proyecto': reverse_map_value('monto_proyecto', props.get('Monto del proyecto', {})),
                'potencial_comercial': reverse_map_value('potencial_comercial', props.get('Potencial comercial', {})),
                'poc_definida': reverse_map_value('poc_definida', props.get('PoC bien definida', {})),
                'plazo_ejecucion': reverse_map_value('plazo_ejecucion', props.get('Plazo de ejecución', {})),
                'entorno_pruebas': reverse_map_value('entorno_pruebas', props.get('Entorno de pruebas', {})),
                'presupuesto_definido': reverse_map_value('presupuesto_definido', props.get('Presupuesto definido', {})),
                'notion_page_id': notion_page_id,  # Para saber que es una edición
                'fecha_original': props.get('Fecha de evaluación', {}).get('date', {}).get('start', '')
            }
            
            return render_template('evaluation_form.html', 
                                 evaluator=evaluator,
                                 edit_data=evaluacion_data,
                                 is_edit=True)
        else:
            flash('Error al cargar evaluación para editar', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error al cargar evaluación: {str(e)}")
        flash(f'Error al cargar evaluación: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/actualizar', methods=['POST'])
def actualizar_evaluacion():
    """Actualizar evaluación existente y crear entrada de timeline"""
    try:
        form_data = request.form.to_dict()
        notion_page_id = form_data.get('notion_page_id')
        
        if not notion_page_id:
            flash('Error: ID de evaluación no encontrado', 'error')
            return redirect(url_for('index'))
        
        # Crear objeto de criterios
        criteria = PoCEvaluationCriteria(
            tiempo_cierre_comercial=int(form_data.get('tiempo_cierre_comercial', 3)),
            recursos_preventa=int(form_data.get('recursos_preventa', 3)),
            historial_cliente=int(form_data.get('historial_cliente', 3)),
            competencia_directa=int(form_data.get('competencia_directa', 3)),
            madurez_cliente=int(form_data.get('madurez_cliente', 3)),
            naturaleza_poc=int(form_data.get('naturaleza_poc', 3)),
            sponsor_ejecutivo=int(form_data.get('sponsor_ejecutivo', 3)),
            compromiso_cliente=int(form_data.get('compromiso_cliente', 3)),
            complejidad_tecnica=int(form_data.get('complejidad_tecnica', 3)),
            monto_proyecto=int(form_data.get('monto_proyecto', 3)),
            potencial_comercial=int(form_data.get('potencial_comercial', 3)),
            poc_definida=int(form_data.get('poc_definida', 3)),
            plazo_ejecucion=int(form_data.get('plazo_ejecucion', 3)),
            entorno_pruebas=int(form_data.get('entorno_pruebas', 3)),
            presupuesto_definido=int(form_data.get('presupuesto_definido', 3))
        )
        
        # Calcular nuevas puntuaciones
        scores = evaluator.calculate_scores(criteria)
        recommendations = evaluator.get_recommendations(criteria, scores)
        
        # Actualizar el registro existente en Notion
        success = update_notion_record(notion_page_id, {
            **form_data,
            **scores,
            **{k: v for k, v in criteria.__dict__.items()}
        })
        
        # Crear entrada de timeline (nuevo registro)
        timeline_success = create_timeline_entry({
            **form_data,
            **scores,
            **{k: v for k, v in criteria.__dict__.items()},
            'fecha_original': form_data.get('fecha_original', ''),
            'tipo_actualizacion': 'Reevaluación'
        })
        
        if success:
            flash('¡Evaluación actualizada exitosamente! Se creó entrada en el timeline.', 'success')
        else:
            flash('Evaluación procesada pero error al actualizar en Notion.', 'warning')
        
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        return render_template('evaluation_results.html', 
                             scores=scores,
                             recommendations=recommendations,
                             form_data=form_data,
                             criteria=criteria,
                             evaluator=evaluator,
                             current_date=current_date,
                             is_update=True)
                             
    except Exception as e:
        logger.error(f"Error en actualización: {str(e)}")
        flash(f'Error al actualizar evaluación: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/timeline/<string:cliente>')
def timeline_cliente(cliente):
    """Mostrar timeline completo de evolución del cliente"""
    try:
        headers = {
            'Authorization': f'Bearer {NOTION_TOKEN}',
            'Notion-Version': '2022-06-28'
        }
        
        # Buscar TODAS las entradas (principales + timeline)
        response = requests.post(
            f'https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query',
            headers=headers,
            json={
                "filter": {
                    "or": [
                        {
                            "property": "Cliente",
                            "title": {"contains": cliente}
                        },
                        {
                            "property": "Cliente", 
                            "title": {"contains": f"{cliente} - Timeline"}
                        }
                    ]
                },
                "sorts": [
                    {
                        "property": "Fecha de evaluación",
                        "direction": "ascending"
                    }
                ]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            timeline_entries = []
            
            for page in data.get('results', []):
                props = page.get('properties', {})
                
                # Calcular semáforo
                eficiencia = props.get('Eficiencia_total', {}).get('number', 0)
                riesgo = props.get('Riesgo_total', {}).get('number', 0)
                
                # Lógica de semáforo
                if riesgo <= 10 and eficiencia <= 10:
                    semaforo = "🟢 Ideal"
                    color_class = "success"
                elif riesgo <= 10 and eficiencia <= 16:
                    semaforo = "🟡 Bueno" 
                    color_class = "warning"
                elif riesgo <= 16 and eficiencia <= 10:
                    semaforo = "🟡 Aceptable"
                    color_class = "warning"
                elif riesgo <= 16 and eficiencia <= 16:
                    semaforo = "🟠 Regular"
                    color_class = "warning"
                else:
                    semaforo = "🔴 Crítico"
                    color_class = "danger"
                
                entry = {
                    'fecha': props.get('Fecha de evaluación', {}).get('date', {}).get('start', ''),
                    'eficiencia_total': eficiencia,
                    'riesgo_total': riesgo,
                    'semaforo': semaforo,
                    'color_class': color_class,
                    'estado': props.get('Estado', {}).get('status', {}).get('name', ''),
                    'responsable': props.get('Responsable Preventa', {}).get('select', {}).get('name', ''),
                    'is_timeline': '- Timeline' in props.get('Cliente', {}).get('title', [{}])[0].get('text', {}).get('content', '')
                }
                timeline_entries.append(entry)
            
            return render_template('timeline_cliente.html',
                                 cliente=cliente,
                                 timeline=timeline_entries)
        else:
            flash('Error al obtener timeline del cliente', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error en timeline: {str(e)}")
        flash(f'Error al cargar timeline: {str(e)}', 'error')
        return redirect(url_for('index'))

def update_notion_record(page_id, data):
    """Actualizar registro existente en Notion"""
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    
    def map_select_value(field_name, value):
        return evaluator.evaluation_options[field_name][int(value)]
    
    # Estructura para actualizar (PATCH)
    notion_data = {
        "properties": {
            "Fecha de evaluación": {
                "date": {"start": datetime.now().isoformat().split('T')[0]}
            },
            "Estado": {
                "status": {"name": "Actualizado"}
            },
            "Tiempo para cierre comercial": {
                "select": {"name": map_select_value('tiempo_cierre_comercial', data.get('tiempo_cierre_comercial', 3))}
            },
            "Recursos preventa requeridos": {
                "select": {"name": map_select_value('recursos_preventa', data.get('recursos_preventa', 3))}
            },
            "Historial con el cliente": {
                "select": {"name": map_select_value('historial_cliente', data.get('historial_cliente', 3))}
            },
            "Competencia directa": {
                "select": {"name": map_select_value('competencia_directa', data.get('competencia_directa', 3))}
            },
            "Madurez del cliente": {
                "select": {"name": map_select_value('madurez_cliente', data.get('madurez_cliente', 3))}
            },
            "Naturaleza del PoC": {
                "select": {"name": map_select_value('naturaleza_poc', data.get('naturaleza_poc', 3))}
            },
            "Sponsor ejecutivo": {
                "select": {"name": map_select_value('sponsor_ejecutivo', data.get('sponsor_ejecutivo', 3))}
            },
            "Compromiso del cliente": {
                "select": {"name": map_select_value('compromiso_cliente', data.get('compromiso_cliente', 3))}
            },
            "Complejidad técnica": {
                "select": {"name": map_select_value('complejidad_tecnica', data.get('complejidad_tecnica', 3))}
            },
            "Monto del proyecto": {
                "select": {"name": map_select_value('monto_proyecto', data.get('monto_proyecto', 3))}
            },
            "Potencial comercial": {
                "select": {"name": map_select_value('potencial_comercial', data.get('potencial_comercial', 3))}
            },
            "PoC bien definida": {
                "select": {"name": map_select_value('poc_definida', data.get('poc_definida', 3))}
            },
            "Plazo de ejecución": {
                "select": {"name": map_select_value('plazo_ejecucion', data.get('plazo_ejecucion', 3))}
            },
            "Entorno de pruebas": {
                "select": {"name": map_select_value('entorno_pruebas', data.get('entorno_pruebas', 3))}
            },
            "Presupuesto definido": {
                "select": {"name": map_select_value('presupuesto_definido', data.get('presupuesto_definido', 3))}
            },
            "Eficiencia_total": {
                "number": data.get('eficiencia_total', 0)
            },
            "Riesgo_total": {
                "number": data.get('riesgo_total', 0)
            }
        }
    }
    
    try:
        response = requests.patch(
            f'https://api.notion.com/v1/pages/{page_id}',
            headers=headers,
            json=notion_data
        )
        
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error al actualizar Notion: {str(e)}")
        return False

def create_timeline_entry(data):
    """Crear nueva entrada en timeline (copia con fecha actual)"""
    # Usar la función send_to_notion existente pero con datos de timeline
    timeline_data = data.copy()
    timeline_data['cliente'] = f"{data.get('cliente', '')} - Timeline"
    
    return send_to_notion(timeline_data)

if __name__ == '__main__':
    import os
    # Detectar si estamos en Railway
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Fortinet PoC Evaluator on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
