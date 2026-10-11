
import pytest
from src.qualification_engine import QualificationEngine

def test_fully_eligible():
    engine = QualificationEngine()
    engine.update_facts({
        'customer_verified': True,
        'customer_available': True,
        'property_type': 'residential',
        'ownership_status': 'sole',
        'original_documents_available': True,
        'requested_loan_amount': 5000000,
        'occupation': 'salaried',
        'income_mode': 'bank',
        'estimated_market_value': 10000000,
        'requested_tenure_years': 10
    })
    assert engine.state.all_checklist_items_complete is True
    assert engine.state.handoff_allowed is True
    assert engine.state.conversation_status == "ENDED_QUALIFIED"

def test_agricultural_disqualifies():
    engine = QualificationEngine()
    engine.update_facts({'property_type': 'agricultural'})
    assert engine.state.disqualified is True
    assert engine.state.conversation_status == "ENDED_DISQUALIFIED"
    
def test_loan_limit_rejection():
    engine = QualificationEngine()
    engine.update_facts({'requested_loan_amount': 8000000, 'loan_amount_limit_response': False})
    assert engine.state.conversation_status == "ENDED_DECLINED_LIMIT"
