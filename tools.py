import json
from typing import Any

from pydantic import BaseModel, Field

from db import medications, prescriptions, stock, users
from db.connection import get_connection
from db.dosage import calculate_equivalent_months


class BaseTool(BaseModel):
    """Base class for all tools. Subclass and implement execute()."""

    @classmethod
    def name(cls) -> str:
        """Tool name derived from class name."""
        # Convert PascalCase to snake_case
        class_name = cls.__name__
        result = []
        for i, char in enumerate(class_name):
            if char.isupper() and i > 0:
                result.append("_")
            result.append(char.lower())
        return "".join(result)

    @classmethod
    def description(cls) -> str:
        """Tool description from docstring."""
        return cls.__doc__ or ""

    @classmethod
    def to_openai_schema(cls) -> dict[str, Any]:
        """Convert to OpenAI function tool schema."""
        return {
            "type": "function",
            "name": cls.name(),
            "description": cls.description(),
            "parameters": cls.model_json_schema(),
        }

    def execute(self) -> dict[str, Any]:
        """Execute the tool. Override in subclass."""
        raise NotImplementedError

    @classmethod
    def run(cls, arguments: str) -> str:
        """Parse JSON arguments, execute, and return JSON result."""
        args = json.loads(arguments)
        instance = cls(**args)
        result = instance.execute()
        return json.dumps(result)


class GetMedicationStock(BaseTool):
    """Get stock info for a medication by name. Returns all available dosages and quantities (in monthly packs)."""

    medication_name: str = Field(description="The name of the medication to check")

    def execute(self) -> dict[str, Any]:
        # Look up medication by name (with ingredients for alternative suggestions)
        med = medications.get_by_name(self.medication_name, include_ingredients=True)
        if not med:
            return {
                "medication_name": self.medication_name,
                "found": False,
                "error": f"Medication '{self.medication_name}' not found in catalogue",
            }

        # Check stock availability
        availability = stock.check_availability(med.id)

        # Get in-stock items
        in_stock_items = [s for s in availability.alternatives if s.quantity > 0]

        return {
            "medication_name": med.name_en,
            "found": True,
            "description": med.description_en,
            "requires_prescription": med.requires_prescription,
            "price": med.price,
            "in_stock": len(in_stock_items) > 0,
            "active_ingredients": [ing.name_en for ing in med.ingredients],
            "available_stock": [
                {"dosage": s.dosage, "quantity": s.quantity} for s in in_stock_items
            ],
        }


class GetDosageInstructions(BaseTool):
    """Get dosage and usage instructions for a medication. Returns adult/child doses, frequency, max daily dose, and warnings."""

    medication_name: str = Field(description="The name of the medication")
    dosage: str | None = Field(
        default=None,
        description="Optional specific dosage (e.g., '500mg'). If not provided, returns instructions for all available dosages.",
    )

    def execute(self) -> dict[str, Any]:
        med = medications.get_by_name(self.medication_name)
        if not med:
            return {
                "medication_name": self.medication_name,
                "found": False,
                "error": f"Medication '{self.medication_name}' not found in catalogue",
            }

        instructions = medications.get_dosage_instructions(med.id, self.dosage)

        if not instructions:
            if self.dosage:
                return {
                    "medication_name": med.name_en,
                    "found": True,
                    "dosage": self.dosage,
                    "instructions_found": False,
                    "error": f"No dosage instructions found for {self.dosage}",
                }
            return {
                "medication_name": med.name_en,
                "found": True,
                "instructions_found": False,
                "error": "No dosage instructions available for this medication",
            }

        return {
            "medication_name": med.name_en,
            "found": True,
            "instructions_found": True,
            "dosage_instructions": instructions,
        }


class GetMedicationsByIngredient(BaseTool):
    """Get medications containing an ingredient. Returns stock availability (in monthly packs) for each."""

    ingredient_name: str = Field(
        description="The name of the active ingredient to search for"
    )

    def execute(self) -> dict[str, Any]:
        results = medications.get_by_ingredient(
            self.ingredient_name, include_ingredients=True
        )

        if not results:
            return {
                "ingredient_name": self.ingredient_name,
                "found": False,
                "count": 0,
                "medications": [],
            }

        medication_list = []
        for med in results:
            # Get stock availability
            availability = stock.check_availability(med.id)
            in_stock_items = [s for s in availability.alternatives if s.quantity > 0]

            # Find extra ingredients (besides the searched one)
            extra_ingredients = [
                ing.name_en
                for ing in med.ingredients
                if ing.name_en.lower() != self.ingredient_name.lower()
            ]

            med_info: dict[str, Any] = {
                "name": med.name_en,
                "description": med.description_en,
                "requires_prescription": med.requires_prescription,
                "price": med.price,
                "in_stock": len(in_stock_items) > 0,
                "available_stock": [
                    {"dosage": s.dosage, "quantity": s.quantity} for s in in_stock_items
                ],
            }

            if extra_ingredients:
                med_info["extra_ingredients"] = extra_ingredients

            medication_list.append(med_info)

        return {
            "ingredient_name": self.ingredient_name,
            "found": True,
            "count": len(results),
            "medications": medication_list,
        }


class LoadPrescriptions(BaseTool):
    """Load all active prescriptions for a user by their 4-digit PIN."""

    pin: str = Field(description="The user's 4-digit PIN")

    def execute(self) -> dict[str, Any]:
        user_prescriptions = prescriptions.get_by_user_pin(
            self.pin, active_only=True, include_medication=True
        )

        if not user_prescriptions:
            return {
                "found": False,
                "error": "No active prescriptions found for this PIN",
                "prescriptions": [],
            }

        # Get user name from the first prescription's user lookup
        user = user_prescriptions[0].user
        if not user:
            # Fetch user separately if not included
            user = users.get_by_pin(self.pin)

        prescription_list = []
        for rx in user_prescriptions:
            rx_info: dict[str, Any] = {
                "prescription_id": rx.id,
                "dosage": rx.dosage,
                "months_supply": rx.months_supply,
                "months_fulfilled": rx.months_fulfilled,
                "months_remaining": rx.months_remaining,
                "expires_at": rx.expires_at.isoformat() if rx.expires_at else None,
            }

            if rx.medication:
                rx_info["medication_name"] = rx.medication.name_en
                rx_info["price"] = rx.medication.price

            prescription_list.append(rx_info)

        return {
            "found": True,
            "user_name": user.name if user else None,
            "count": len(prescription_list),
            "prescriptions": prescription_list,
        }


class MedicationToReserve(BaseModel):
    """A single medication to reserve with dosage and quantity (in monthly packs)."""

    medication_name: str = Field(description="The name of the medication to reserve")
    dosage: str = Field(description="The dosage to reserve (e.g., '500mg', '100mg')")
    quantity: int = Field(description="Number of monthly packs to reserve", gt=0)


class ReserveMedications(BaseTool):
    """Reserve medications for a user. Validates prescriptions, checks stock, and updates inventory.

    Stock units are monthly packs. Each reservation decrements stock and increments
    the prescription's months_fulfilled by the quantity reserved.

    All medications must have valid active prescriptions. Dosage flexibility is allowed -
    e.g., 5x100mg packs can fulfill a 10x50mg prescription (equivalent total milligrams,
    with up to 25% tolerance for rounding).

    This is an all-or-nothing operation: if any medication fails validation,
    no reservations are made.
    """

    user_pin: str = Field(description="The user's 4-digit PIN")
    medications: list[MedicationToReserve] = Field(
        description="List of medications to reserve with dosage and quantity"
    )

    def execute(self) -> dict[str, Any]:
        # 1. Validate user exists
        user = users.get_by_pin(self.user_pin)
        if not user:
            return {
                "success": False,
                "error": f"User with PIN '{self.user_pin}' not found",
            }

        # 2. Get all active prescriptions for the user
        user_prescriptions = prescriptions.get_by_user_pin(
            self.user_pin, active_only=True, include_medication=True
        )

        # Build a lookup: medication_id -> prescription
        prescription_by_med_id: dict[int, Any] = {}
        for rx in user_prescriptions:
            prescription_by_med_id[rx.medication_id] = rx

        # 3. Validate all medications before making any changes
        validated_items: list[dict[str, Any]] = []
        errors: list[str] = []

        for med_request in self.medications:
            # Find the medication
            med = medications.get_by_name(med_request.medication_name)
            if not med:
                errors.append(
                    f"Medication '{med_request.medication_name}' not found in catalogue"
                )
                continue

            # Check if user has an active prescription for this medication
            # Only required if medication requires a prescription
            rx = prescription_by_med_id.get(med.id)
            if not rx and med.requires_prescription:
                errors.append(
                    f"No active prescription for '{med_request.medication_name}'"
                )
                continue

            # Check dosage equivalence and calculate effective months consumed
            # E.g., 16 packs of 10mg fulfills 8 months of a 20mg prescription
            effective_months: int | None = None
            if rx and rx.dosage:
                effective_months = calculate_equivalent_months(
                    requested_dosage=med_request.dosage,
                    requested_quantity=med_request.quantity,
                    prescribed_dosage=rx.dosage,
                    tolerance=0.25,
                )

                if effective_months is None:
                    errors.append(
                        f"Requested dosage {med_request.dosage} of "
                        f"'{med_request.medication_name}' cannot be converted to "
                        f"prescription dosage {rx.dosage} (rounding exceeds 25% tolerance)"
                    )
                    continue

                # Check that effective months don't exceed remaining prescription
                if effective_months > rx.months_remaining:
                    errors.append(
                        f"Cannot reserve {med_request.quantity}x{med_request.dosage} of "
                        f"'{med_request.medication_name}': equivalent to {effective_months} "
                        f"month(s), but only {rx.months_remaining} month(s) remaining on prescription"
                    )
                    continue

            # Check stock availability
            stock_items = stock.get_by_medication_id(med.id, med_request.dosage)
            if not stock_items:
                errors.append(
                    f"'{med_request.medication_name}' {med_request.dosage} not in stock"
                )
                continue

            stock_item = stock_items[0]
            if stock_item.quantity < med_request.quantity:
                errors.append(
                    f"Insufficient stock for '{med_request.medication_name}' "
                    f"{med_request.dosage}: requested {med_request.quantity}, "
                    f"available {stock_item.quantity}"
                )
                continue

            # All checks passed for this medication
            validated_items.append(
                {
                    "medication": med,
                    "prescription": rx,
                    "stock_item": stock_item,
                    "quantity": med_request.quantity,
                    "dosage": med_request.dosage,
                    "effective_months": effective_months,
                }
            )

        # If any errors, fail the entire operation
        if errors:
            return {
                "success": False,
                "errors": errors,
            }

        if not validated_items:
            return {
                "success": False,
                "error": "No medications to reserve",
            }

        # 4. Execute all updates in a transaction
        conn = get_connection()
        try:
            cursor = conn.cursor()

            reserved_details: list[dict[str, Any]] = []
            total_reservation_price = 0.0

            for item in validated_items:
                stock_item = item["stock_item"]
                rx = item["prescription"]
                med = item["medication"]

                # Decrement stock
                cursor.execute(
                    "UPDATE stock SET quantity = quantity - ?, "
                    "updated_at = datetime('now') WHERE id = ?",
                    (item["quantity"], stock_item.id),
                )

                # Increment prescription months_fulfilled by effective months consumed
                # Only for prescription medications
                if rx:
                    cursor.execute(
                        "UPDATE prescriptions SET months_fulfilled = months_fulfilled + ? "
                        "WHERE id = ?",
                        (item["effective_months"], rx.id),
                    )

                # Get dosage instructions for the reserved dosage
                dosage_instructions = medications.get_dosage_instructions(
                    med.id, item["dosage"]
                )

                item_total_price = (med.price or 0.0) * item["quantity"]
                total_reservation_price += item_total_price

                reserved_item: dict[str, Any] = {
                    "medication_name": med.name_en,
                    "dosage": item["dosage"],
                    "quantity": item["quantity"],
                    "unit_price": med.price,
                    "total_price": item_total_price,
                }

                # Include prescription info only if applicable
                if rx:
                    reserved_item["prescription_id"] = rx.id
                    reserved_item["months_remaining"] = (
                        rx.months_remaining - item["effective_months"]
                    )

                if dosage_instructions:
                    reserved_item["usage"] = dosage_instructions[0]

                reserved_details.append(reserved_item)

            conn.commit()

        except Exception as e:
            conn.rollback()
            return {
                "success": False,
                "error": f"Transaction failed: {str(e)}",
            }
        finally:
            conn.close()

        return {
            "success": True,
            "user_name": user.name,
            "reserved": reserved_details,
            "total_reservation_price": total_reservation_price,
        }
