import json
from typing import Any

from pydantic import BaseModel, Field


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

    def execute(self) -> dict[str, Any]:
        return {
            "medication_name": self.medication_name,
            "in_stock": True,
        }
