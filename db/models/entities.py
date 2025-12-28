"""Pydantic models for database entities."""

from datetime import datetime

from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    """Active ingredient model."""

    id: int
    name_en: str
    name_he: str | None = None


class Medication(BaseModel):
    """Medication catalogue entry."""

    id: int
    name_en: str
    name_he: str | None = None
    description_en: str | None = None
    description_he: str | None = None
    price: float | None = None
    requires_prescription: bool = False
    created_at: datetime

    # Optional: populated when joining with ingredients
    ingredients: list[Ingredient] = Field(default_factory=list)


class Stock(BaseModel):
    """Inventory stock entry."""

    id: int
    medication_id: int
    dosage: str | None = None
    quantity: int = 0
    updated_at: datetime

    # Optional: populated when joining with medications
    medication: Medication | None = None


class StockAvailability(BaseModel):
    """Result of checking stock availability."""

    medication_id: int
    requested_dosage: str | None = None
    exact_match: Stock | None = None
    available_quantity: int = 0
    alternatives: list[Stock] = Field(default_factory=list)

    @property
    def has_exact_match(self) -> bool:
        """Check if exact dosage match was found with stock."""
        return self.exact_match is not None and self.available_quantity > 0

    @property
    def has_alternatives(self) -> bool:
        """Check if alternative dosages are available."""
        return len(self.alternatives) > 0


class User(BaseModel):
    """Customer/user model."""

    id: int
    pin: str = Field(min_length=4, max_length=4)
    name: str
    created_at: datetime


class Prescription(BaseModel):
    """Prescription model."""

    id: int
    user_id: int
    medication_id: int
    dosage: str | None = None
    months_supply: int
    months_fulfilled: int = 0
    created_at: datetime
    expires_at: datetime | None = None

    # Optional: populated when joining
    user: User | None = None
    medication: Medication | None = None

    @property
    def months_remaining(self) -> int:
        """Calculate remaining months to fulfill."""
        return self.months_supply - self.months_fulfilled

    @property
    def is_fully_fulfilled(self) -> bool:
        """Check if prescription is fully fulfilled."""
        return self.months_fulfilled >= self.months_supply
