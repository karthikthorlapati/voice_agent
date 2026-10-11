
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
