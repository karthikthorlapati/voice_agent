import json
from src.qualification_engine import QualificationEngine

def main():
    print("==============================================")
    print(" Home Credit LAP AI Voice Agent - Simulator ")
    print("==============================================")
    print("Type 'quit' or 'exit' to stop.")
    print("Provide facts as JSON. For example:")
    print('{"customer_verified": true}')
    print("----------------------------------------------")
    
    engine = QualificationEngine()
    
    while True:
        question = engine.get_next_question()
        if not question:
            print("\nConversation Finished!")
            print(f"Final Status: {engine.state.conversation_status}")
            if engine.state.disqualified:
                print(f"Reason: {engine.state.disqualification_reason}")
            break
            
        print(f"\nAgent: {question}")
        user_input = input("Customer (JSON facts) > ")
        
        if user_input.lower() in ['quit', 'exit']:
            break
            
        try:
            facts = json.loads(user_input)
            engine.update_facts(facts)
        except json.JSONDecodeError:
            print("Invalid JSON. Please enter facts like {\"property_type\": \"residential\"}")

if __name__ == "__main__":
    main()
