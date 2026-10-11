
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
