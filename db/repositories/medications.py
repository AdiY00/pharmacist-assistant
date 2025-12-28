"""Medications repository."""

from db.connection import query_all, query_one
from db.models import Ingredient, Medication


def _row_to_medication(row: dict) -> Medication:
    """Convert a database row to a Medication model."""
    return Medication(
        id=row["id"],
        name_en=row["name_en"],
        name_he=row["name_he"],
        description_en=row["description_en"],
        description_he=row["description_he"],
        price=row["price"],
        requires_prescription=bool(row["requires_prescription"]),
        created_at=row["created_at"],
    )


def _get_ingredients_for_medication(medication_id: int) -> list[Ingredient]:
    """Get all ingredients for a medication."""
    rows = query_all(
        """
        SELECT i.id, i.name_en, i.name_he
        FROM ingredients i
        JOIN medication_ingredients mi ON i.id = mi.ingredient_id
        WHERE mi.medication_id = ?
        """,
        (medication_id,),
    )
    return [Ingredient(**row) for row in rows]


def get_by_id(
    medication_id: int, include_ingredients: bool = False
) -> Medication | None:
    """Get a medication by ID."""
    row = query_one("SELECT * FROM medications WHERE id = ?", (medication_id,))
    if not row:
        return None

    med = _row_to_medication(row)
    if include_ingredients:
        med.ingredients = _get_ingredients_for_medication(medication_id)
    return med


def get_by_name(
    name: str,
    include_ingredients: bool = False,
    language: str = "en",
) -> Medication | None:
    """Get a medication by name (searches both EN and HE names)."""
    row = query_one(
        """
        SELECT * FROM medications
        WHERE LOWER(name_en) = LOWER(?) OR LOWER(name_he) = LOWER(?)
        """,
        (name, name),
    )
    if not row:
        return None

    med = _row_to_medication(row)
    if include_ingredients:
        med.ingredients = _get_ingredients_for_medication(med.id)
    return med


def search(
    query: str,
    include_ingredients: bool = False,
) -> list[Medication]:
    """Search medications by name (partial match)."""
    rows = query_all(
        """
        SELECT * FROM medications
        WHERE LOWER(name_en) LIKE LOWER(?) OR LOWER(name_he) LIKE LOWER(?)
        ORDER BY name_en
        """,
        (f"%{query}%", f"%{query}%"),
    )

    medications = [_row_to_medication(row) for row in rows]
    if include_ingredients:
        for med in medications:
            med.ingredients = _get_ingredients_for_medication(med.id)
    return medications


def get_by_ingredient(
    ingredient_name: str,
    include_ingredients: bool = False,
) -> list[Medication]:
    """Get all medications containing a specific ingredient."""
    rows = query_all(
        """
        SELECT m.* FROM medications m
        JOIN medication_ingredients mi ON m.id = mi.medication_id
        JOIN ingredients i ON i.id = mi.ingredient_id
        WHERE LOWER(i.name_en) LIKE LOWER(?) OR LOWER(i.name_he) LIKE LOWER(?)
        ORDER BY m.name_en
        """,
        (f"%{ingredient_name}%", f"%{ingredient_name}%"),
    )

    medications = [_row_to_medication(row) for row in rows]
    if include_ingredients:
        for med in medications:
            med.ingredients = _get_ingredients_for_medication(med.id)
    return medications


def get_all(include_ingredients: bool = False) -> list[Medication]:
    """Get all medications."""
    rows = query_all("SELECT * FROM medications ORDER BY name_en")

    medications = [_row_to_medication(row) for row in rows]
    if include_ingredients:
        for med in medications:
            med.ingredients = _get_ingredients_for_medication(med.id)
    return medications


def get_dosage_instructions(
    medication_id: int,
    dosage: str | None = None,
) -> list[dict]:
    """
    Get dosage instructions for a medication.

    If dosage is provided, returns instructions for that specific dosage.
    Otherwise, returns instructions for all available dosages.
    """
    if dosage:
        rows = query_all(
            """
            SELECT dosage, adult_dose, child_dose, frequency, max_daily,
                   instructions, warnings
            FROM dosage_instructions
            WHERE medication_id = ? AND LOWER(dosage) = LOWER(?)
            """,
            (medication_id, dosage),
        )
    else:
        rows = query_all(
            """
            SELECT dosage, adult_dose, child_dose, frequency, max_daily,
                   instructions, warnings
            FROM dosage_instructions
            WHERE medication_id = ?
            ORDER BY dosage
            """,
            (medication_id,),
        )
    return [dict(row) for row in rows]
