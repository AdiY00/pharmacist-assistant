"""Database models and utilities."""

from db.models.dosage import (
    calculate_equivalent_months,
    calculate_equivalent_quantity,
    is_dosage_equivalent,
    parse_mg,
)
from db.models.entities import (
    Ingredient,
    Medication,
    Prescription,
    Stock,
    StockAvailability,
    User,
)

__all__ = [
    # Entities
    "Ingredient",
    "Medication",
    "Prescription",
    "Stock",
    "StockAvailability",
    "User",
    # Dosage utilities
    "calculate_equivalent_months",
    "calculate_equivalent_quantity",
    "is_dosage_equivalent",
    "parse_mg",
]
