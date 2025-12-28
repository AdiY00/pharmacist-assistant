Multi-Step Flows

This document defines three distinct multi-step flows the agent can execute.
Each flow lists the expected sequence, tool usage, and how the agent responds.

Flow 1: Stock Check with Alternatives
User goal: Find a medication and see in-stock alternatives if the exact item is unavailable.
Sequence:
1) User asks for availability of a medication name.
2) Agent calls get_medication_stock with medication_name.
3) If in_stock is false or exact dosage is out of stock, agent:
   - Uses active_ingredients from the stock result.
   - Calls get_medications_by_ingredient with the primary ingredient name.
4) Agent summarizes availability and prices for alternatives in stock.
5) If user asks to reserve, agent moves to Flow 2.
Tool usage:
- get_medication_stock
- get_medications_by_ingredient (only if alternatives are needed)
Example (EN):
- User: "Do you have Acamol 500mg?"
- Agent: Calls get_medication_stock("Acamol") -> out of stock.
- Agent: Calls get_medications_by_ingredient("Acetaminophen") -> alternatives in stock.
- Agent: "Acamol is out of stock. In-stock alternatives with the same ingredient: Dexamol 500mg, Paracetamol Teva 500mg. Would you like to reserve one?"

Flow 2: Prescription Check and Reservation
User goal: Reserve prescription medication for pickup.
Sequence:
1) User requests to reserve a prescription medication.
2) Agent asks for 4-digit PIN.
3) Agent calls load_prescriptions with pin.
4) Agent lists active prescriptions and asks which medication, dosage, and quantity.
5) Agent calls reserve_medications with user_pin and requested items.
6) Agent confirms reservation details and total price.
Tool usage:
- load_prescriptions
- reserve_medications
Example (EN):
- User: "Reserve Lipitor 10mg for me."
- Agent: "Please provide your 4-digit PIN."
- Agent: Calls load_prescriptions("1234") -> active prescriptions found.
- Agent: "You have Lipitor 10mg available. How many monthly packs?"
- User: "2 packs."
- Agent: Calls reserve_medications({ user_pin: "1234", medications: [...] })
- Agent: "Reserved 2 packs of Lipitor 10mg. Total price: ILS ..."

Flow 3: Dosage Information with Safety Guardrails
User goal: Get dosage and usage instructions without receiving medical advice.
Sequence:
1) User asks for dosage/usage info for a medication.
2) Agent calls get_dosage_instructions with medication_name (and dosage if provided).
3) Agent returns factual dosage info from the database.
4) If the user requests advice or treatment recommendation, the agent refuses and
   redirects to a healthcare professional.
Tool usage:
- get_dosage_instructions
Example (EN):
- User: "How should I take Advil 200mg?"
- Agent: Calls get_dosage_instructions("Advil", "200mg") -> returns instructions.
- Agent: Provides dosage, frequency, warnings.
- User: "Should I take it for my headache?"
- Agent: Refuses to advise and suggests consulting a healthcare professional.
