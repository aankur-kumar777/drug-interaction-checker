"""
Unit tests for Drug Interaction Checker API
"""
import pytest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import create_app
from app.interaction_checker import InteractionChecker

@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def checker():
    """Create interaction checker instance"""
    return InteractionChecker()

# API Tests

def test_index_route(client):
    """Test the index route"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Drug Interaction Checker API'
    assert data['status'] == 'active'

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_check_interactions_valid(client):
    """Test checking interactions with valid drugs"""
    response = client.post(
        '/api/check-interactions',
        data=json.dumps({'drugs': ['warfarin', 'aspirin']}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'interactions' in data['data']

def test_check_interactions_missing_drugs(client):
    """Test checking interactions without drugs parameter"""
    response = client.post(
        '/api/check-interactions',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'

def test_check_interactions_insufficient_drugs(client):
    """Test checking interactions with only one drug"""
    response = client.post(
        '/api/check-interactions',
        data=json.dumps({'drugs': ['warfarin']}),
        content_type='application/json'
    )
    assert response.status_code == 400

def test_search_drugs(client):
    """Test drug search"""
    response = client.get('/api/search?q=war')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'results' in data['data']

def test_search_drugs_short_query(client):
    """Test drug search with query too short"""
    response = client.get('/api/search?q=w')
    assert response.status_code == 400

def test_get_drug_info(client):
    """Test getting drug information"""
    response = client.get('/api/drug/warfarin')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'

def test_get_drug_info_not_found(client):
    """Test getting info for non-existent drug"""
    response = client.get('/api/drug/nonexistentdrug')
    assert response.status_code == 404

# Interaction Checker Tests

def test_checker_get_drug_info(checker):
    """Test getting drug information"""
    info = checker.get_drug_info('warfarin')
    assert info is not None
    assert info['class'] == 'anticoagulant'

def test_checker_search_drugs(checker):
    """Test searching for drugs"""
    results = checker.search_drugs('war', limit=5)
    assert len(results) > 0
    assert any('warfarin' in r['name'] for r in results)

def test_checker_interaction_detection(checker):
    """Test interaction detection"""
    result = checker.check_interactions(['warfarin', 'aspirin'])
    assert 'interactions' in result
    assert len(result['interactions']) > 0
    assert result['overall_risk'] in ['low', 'moderate', 'high', 'critical']

def test_checker_no_interaction(checker):
    """Test drugs with no interaction"""
    result = checker.check_interactions(['metformin', 'amoxicillin'])
    # Should return but may or may not have interactions
    assert 'interactions' in result

def test_checker_calculate_risk(checker):
    """Test risk calculation"""
    interactions = [
        {'severity': 'major'},
        {'severity': 'moderate'}
    ]
    risk = checker._calculate_overall_risk(interactions)
    assert risk in ['low', 'moderate', 'high', 'critical']

def test_checker_alternatives(checker):
    """Test getting alternatives"""
    alternatives = checker.get_alternatives('ibuprofen', context_drugs=['warfarin'])
    assert isinstance(alternatives, list)

# Integration Tests

def test_full_workflow(client):
    """Test complete workflow"""
    # Search for drug
    search_response = client.get('/api/search?q=asp')
    assert search_response.status_code == 200
    
    # Check interactions
    check_response = client.post(
        '/api/check-interactions',
        data=json.dumps({'drugs': ['warfarin', 'aspirin', 'ibuprofen']}),
        content_type='application/json'
    )
    assert check_response.status_code == 200
    data = json.loads(check_response.data)
    assert data['status'] == 'success'
    
    # Get alternatives
    alt_response = client.get('/api/alternatives/ibuprofen?context=warfarin')
    assert alt_response.status_code == 200

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
