"""
API Routes for Drug Interaction Checker
"""
from flask import Blueprint, request, jsonify
from interaction_checker import InteractionChecker
from knowledge_graph import KnowledgeGraph
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Initialize core components
interaction_checker = InteractionChecker()
knowledge_graph = KnowledgeGraph()

@api_bp.route('/check-interactions', methods=['POST'])
def check_interactions():
    """
    Check drug interactions for a list of drugs
    
    Request body:
    {
        "drugs": ["drug1", "drug2", "drug3"],
        "patient_factors": {  # Optional
            "age": 65,
            "conditions": ["hypertension"],
            "allergies": []
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'drugs' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing drugs parameter'
            }), 400
        
        drugs = data['drugs']
        patient_factors = data.get('patient_factors', {})
        
        if not isinstance(drugs, list) or len(drugs) < 2:
            return jsonify({
                'status': 'error',
                'message': 'Please provide at least 2 drugs'
            }), 400
        
        # Check interactions
        result = interaction_checker.check_interactions(drugs, patient_factors)
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f'Error checking interactions: {e}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/drug/<string:drug_name>', methods=['GET'])
def get_drug_info(drug_name):
    """Get detailed information about a specific drug"""
    try:
        drug_info = interaction_checker.get_drug_info(drug_name)
        
        if not drug_info:
            return jsonify({
                'status': 'error',
                'message': f'Drug "{drug_name}" not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': drug_info
        }), 200
        
    except Exception as e:
        logger.error(f'Error retrieving drug info: {e}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/alternatives/<string:drug_name>', methods=['GET'])
def get_alternatives(drug_name):
    """Get safer alternatives for a drug"""
    try:
        # Get context drugs from query parameters
        context_drugs = request.args.getlist('context')
        
        alternatives = interaction_checker.get_alternatives(
            drug_name, 
            context_drugs
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'original_drug': drug_name,
                'alternatives': alternatives
            }
        }), 200
        
    except Exception as e:
        logger.error(f'Error getting alternatives: {e}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/search', methods=['GET'])
def search_drugs():
    """Search for drugs by name"""
    try:
        query = request.args.get('q', '')
        limit = min(int(request.args.get('limit', 10)), 50)
        
        if len(query) < 2:
            return jsonify({
                'status': 'error',
                'message': 'Query must be at least 2 characters'
            }), 400
        
        results = interaction_checker.search_drugs(query, limit)
        
        return jsonify({
            'status': 'success',
            'data': {
                'query': query,
                'results': results
            }
        }), 200
        
    except Exception as e:
        logger.error(f'Error searching drugs: {e}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/visualize', methods=['POST'])
def visualize_interactions():
    """Generate visualization data for interaction graph"""
    try:
        data = request.get_json()
        drugs = data.get('drugs', [])
        
        if not drugs:
            return jsonify({
                'status': 'error',
                'message': 'No drugs provided'
            }), 400
        
        graph_data = knowledge_graph.generate_visualization(drugs)
        
        return jsonify({
            'status': 'success',
            'data': graph_data
        }), 200
        
    except Exception as e:
        logger.error(f'Error generating visualization: {e}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/severity/<string:drug1>/<string:drug2>', methods=['GET'])
def get_interaction_severity(drug1, drug2):
    """Get interaction severity between two specific drugs"""
    try:
        severity_data = interaction_checker.get_interaction_severity(
            drug1, 
            drug2
        )
        
        if not severity_data:
            return jsonify({
                'status': 'success',
                'data': {
                    'interaction': False,
                    'message': 'No known interaction found'
                }
            }), 200
        
        return jsonify({
            'status': 'success',
            'data': severity_data
        }), 200
        
    except Exception as e:
        logger.error(f'Error getting severity: {e}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/batch-check', methods=['POST'])
def batch_check():
    """
    Check multiple drug combinations in batch
    
    Request body:
    {
        "drug_combinations": [
            ["drug1", "drug2"],
            ["drug3", "drug4", "drug5"]
        ]
    }
    """
    try:
        data = request.get_json()
        combinations = data.get('drug_combinations', [])
        
        if not combinations:
            return jsonify({
                'status': 'error',
                'message': 'No drug combinations provided'
            }), 400
        
        results = []
        for drugs in combinations:
            result = interaction_checker.check_interactions(drugs)
            results.append({
                'drugs': drugs,
                'analysis': result
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_combinations': len(combinations),
                'results': results
            }
        }), 200
        
    except Exception as e:
        logger.error(f'Error in batch check: {e}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
