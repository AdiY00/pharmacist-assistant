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


class CheckStock(BaseTool):
    """Check if a medication is in stock."""

    medication_name: str = Field(description="The name of the medication to check")
    dosage: str | None = Field(
        default=None,
        description="Optional dosage to check if provided by user (e.g., '10mg', '500mg')",
    )

    def execute(self) -> dict[str, Any]:
        # Look up medication by name
        med = medications.get_by_name(self.medication_name)
        if not med:
            return {
                "medication_name": self.medication_name,
                "found": False,
                "error": f"Medication '{self.medication_name}' not found in catalogue",
            }

        # Check stock availability
        availability = stock.check_availability(med.id, self.dosage)

        result: dict[str, Any] = {
            "medication_name": med.name_en,
            "medication_name_he": med.name_he,
            "found": True,
            "in_stock": availability.available_quantity > 0,
            "total_quantity": availability.available_quantity,
        }

        if self.dosage:
            result["requested_dosage"] = self.dosage
            result["exact_match"] = availability.has_exact_match

        # Include available dosages/quantities
        if availability.exact_match:
            result["stock"] = {
                "dosage": availability.exact_match.dosage,
                "quantity": availability.exact_match.quantity,
            }

        if availability.alternatives:
            result["alternatives"] = [
                {"dosage": s.dosage, "quantity": s.quantity}
                for s in availability.alternatives
            ]

        return result
