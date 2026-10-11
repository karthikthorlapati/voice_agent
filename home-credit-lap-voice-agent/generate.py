import os
import json

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

os.makedirs('src', exist_ok=True)
os.makedirs('tests', exist_ok=True)
os.makedirs('prompts', exist_ok=True)
os.makedirs('reports', exist_ok=True)
os.makedirs('submission', exist_ok=True)
os.makedirs('scenarios', exist_ok=True)

models_code = """
from pydantic import BaseModel
from typing import Optional, List, Dict

class CustomerFacts(BaseModel):
    property_type: Optional[str] = None
    ownership_status: Optional[str] = None
    original_documents_available: Optional[bool] = None
    requested_loan_amount: Optional[float] = None
    loan_amount_limit_response: Optional[bool] = None
    occupation: Optional[str] = None
    income_mode: Optional[str] = None
    estimated_market_value: Optional[float] = None
    requested_tenure_years: Optional[float] = None
    existing_property_loan: Optional[bool] = None
    emi_reduction_request: Optional[bool] = None
    transfer_required: Optional[bool] = None
    customer_verified: Optional[bool] = None
    customer_available: Optional[bool] = None
    callback_time: Optional[str] = None

class QualificationState(BaseModel):
    facts: CustomerFacts = CustomerFacts()
    disqualified: bool = False
    disqualification_reason: Optional[str] = None
    all_checklist_items_complete: bool = False
    handoff_allowed: bool = False
    conversation_status: str = "IN_PROGRESS"
"""
write_file('src/models.py', models_code)

engine_code = """
from src.models import QualificationState, CustomerFacts

class QualificationEngine:
    def __init__(self):
        self.state = QualificationState()

    def update_facts(self, facts_dict: dict):
        if self.state.conversation_status != "IN_PROGRESS":
            return
            
        for k, v in facts_dict.items():
            if v is not None:
                setattr(self.state.facts, k, v)
                
        self.evaluate_rules()

    def evaluate_rules(self):
        facts = self.state.facts
        
        if facts.customer_available is False:
            self.state.conversation_status = "ENDED_CALLBACK"
            return
            
        if facts.transfer_required or facts.existing_property_loan or facts.emi_reduction_request:
            self.state.conversation_status = "ENDED_TRANSFER"
            return
            
        if facts.property_type and facts.property_type.lower() == "agricultural":
            self.disqualify("Agricultural property not allowed.")
            return
            
        if facts.original_documents_available is False:
            self.disqualify("Original documents must be available.")
            return
            
        if facts.requested_loan_amount is not None:
            if facts.requested_loan_amount > 7500000:
                if facts.loan_amount_limit_response is False:
                    self.state.conversation_status = "ENDED_DECLINED_LIMIT"
                    return
                elif facts.loan_amount_limit_response is True:
                    facts.requested_loan_amount = 7500000
                    
        if facts.income_mode and facts.income_mode.lower() == "cash":
            self.disqualify("Cash income not allowed.")
            return
            
        if facts.requested_tenure_years is not None:
            if facts.requested_tenure_years < 3 or facts.requested_tenure_years > 15:
                self.disqualify("Tenure must be between 3 and 15 years.")
                return

        checklist = [
            facts.property_type, facts.ownership_status, facts.original_documents_available,
            facts.requested_loan_amount, facts.occupation, facts.income_mode,
            facts.estimated_market_value, facts.requested_tenure_years
        ]
        
        self.state.all_checklist_items_complete = all(v is not None for v in checklist)
        
        if self.state.all_checklist_items_complete and facts.customer_verified and facts.customer_available:
            if not self.state.disqualified and self.state.conversation_status == "IN_PROGRESS":
                if facts.requested_loan_amount <= 7500000:
                    self.state.handoff_allowed = True
                    self.state.conversation_status = "ENDED_QUALIFIED"

    def disqualify(self, reason):
        self.state.disqualified = True
        self.state.disqualification_reason = reason
        self.state.conversation_status = "ENDED_DISQUALIFIED"
        self.state.handoff_allowed = False
        
    def get_next_question(self):
        if self.state.conversation_status != "IN_PROGRESS":
            return None
            
        facts = self.state.facts
        if not facts.customer_verified: return "Are you the intended customer?"
        if facts.customer_available is None: return "Are you available to speak?"
        if not facts.property_type: return "What type of property is it?"
        if not facts.ownership_status: return "Is the property solely or jointly owned?"
        if facts.original_documents_available is None: return "Do you have the original documents?"
        if not facts.requested_loan_amount: return "What is the desired loan amount?"
        if facts.requested_loan_amount > 7500000 and facts.loan_amount_limit_response is None:
            return "The maximum is 75,00,000. Would you like to proceed with that?"
        if not facts.occupation: return "Are you salaried or self-employed?"
        if not facts.income_mode: return "Is your income received through a bank?"
        if not facts.estimated_market_value: return "What is the estimated market value?"
        if not facts.requested_tenure_years: return "What is the desired repayment tenure (3-15 years)?"
        return None
"""
write_file('src/qualification_engine.py', engine_code)

tests_code = """
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
"""
write_file('tests/test_eligibility_rules.py', tests_code)

write_file('requirements.txt', 'pytest\\npydantic\\n')
write_file('README.md', '# Home Credit LAP Voice Agent\\n\\nRun tests: `pytest tests/`\\n')
write_file('.env.example', 'RETELL_API_KEY=\\n')

prompts_code = """
# System Prompt
You are an AI voice agent for Home Credit Loan Against Property.
Your name is {{agent_name}} ({{agent_gender}}).
Company: {{company_name}}
Customer: {{customer_name}}
"""
write_file('prompts/system_prompt.md', prompts_code)
write_file('prompts/system_prompt_variables.md', '# Variables\\n...')
write_file('prompts/conversation_examples.md', '# Examples\\n...')

write_file('submission/FINAL_SYSTEM_PROMPT.md', prompts_code)
write_file('submission/TEST_SCENARIOS.md', '# Test Scenarios\\n...')
write_file('submission/CALL_RECORDINGS_AND_TRANSCRIPTS.md', '# Links\\nNo recordings yet.')
write_file('submission/SUBMISSION_CHECKLIST.md', '# Checklist\\n- [x] Code done')

write_file('reports/requirements_traceability.md', '# Traceability\\n...')
write_file('reports/test_results.md', '# Test Results\\n...')
write_file('reports/architecture.md', '# Architecture\\n...')
write_file('reports/known_limitations.md', '# Limitations\\n...')

print("Generated project files.")
