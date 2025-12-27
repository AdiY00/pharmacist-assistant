import json
from typing import Any

from pydantic import BaseModel, Field

from db import medications, stock


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
    """Get stock info for a medication by name. Returns all available dosages and quantities."""

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
            "in_stock": len(in_stock_items) > 0,
            "active_ingredients": [ing.name_en for ing in med.ingredients],
            "available_stock": [
                {"dosage": s.dosage, "quantity": s.quantity} for s in in_stock_items
            ],
        }


class GetMedicationsByIngredient(BaseTool):
    """Get medications containing an ingredient. Returns stock availability for each."""

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
