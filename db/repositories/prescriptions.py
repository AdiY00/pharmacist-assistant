"""Prescriptions repository."""

from db.connection import execute, query_all, query_one
from db.models import Prescription
from db.repositories import medications, users


def _row_to_prescription(
    row: dict,
    include_user: bool = False,
    include_medication: bool = False,
) -> Prescription:
    """Convert a database row to a Prescription model."""
    prescription = Prescription(
        id=row["id"],
        user_id=row["user_id"],
        medication_id=row["medication_id"],
        dosage=row["dosage"],
        months_supply=row["months_supply"],
        months_fulfilled=row["months_fulfilled"],
        created_at=row["created_at"],
        expires_at=row["expires_at"],
    )
    if include_user:
        prescription.user = users.get_by_id(row["user_id"])
    if include_medication:
        prescription.medication = medications.get_by_id(row["medication_id"])
    return prescription


def get_by_id(
    prescription_id: int,
    include_user: bool = False,
    include_medication: bool = False,
) -> Prescription | None:
    """Get a prescription by ID."""
    row = query_one("SELECT * FROM prescriptions WHERE id = ?", (prescription_id,))
    if not row:
        return None
    return _row_to_prescription(row, include_user, include_medication)


def get_by_user_id(
    user_id: int,
    active_only: bool = True,
    include_medication: bool = False,
) -> list[Prescription]:
    """Get all prescriptions for a user."""
    if active_only:
        rows = query_all(
            """
            SELECT * FROM prescriptions
            WHERE user_id = ?
            AND months_fulfilled < months_supply
            AND (expires_at IS NULL OR expires_at > datetime('now'))
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
    else:
        rows = query_all(
            "SELECT * FROM prescriptions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
    return [
        _row_to_prescription(
            row, include_user=False, include_medication=include_medication
        )
        for row in rows
    ]


def get_by_user_pin(
    pin: str,
    active_only: bool = True,
    include_medication: bool = False,
) -> list[Prescription]:
    """Get all prescriptions for a user by their PIN."""
    user = users.get_by_pin(pin)
    if not user:
        return []
    return get_by_user_id(user.id, active_only, include_medication)


def fulfill(prescription_id: int, months: int = 1) -> bool:
    """
    Fulfill a prescription for the specified number of months.
    Returns False if prescription not found or already fully fulfilled.
    """
    prescription = get_by_id(prescription_id)
    if not prescription:
        return False

    if prescription.months_fulfilled + months > prescription.months_supply:
        return False

    execute(
        "UPDATE prescriptions SET months_fulfilled = months_fulfilled + ? WHERE id = ?",
        (months, prescription_id),
    )
    return True


def is_valid(prescription_id: int) -> bool:
    """Check if a prescription is valid (not expired and not fully fulfilled)."""
    row = query_one(
        """
        SELECT * FROM prescriptions
        WHERE id = ?
        AND months_fulfilled < months_supply
        AND (expires_at IS NULL OR expires_at > datetime('now'))
        """,
        (prescription_id,),
    )
    return row is not None


def get_all(
    active_only: bool = True,
    include_user: bool = False,
    include_medication: bool = False,
) -> list[Prescription]:
    """Get all prescriptions."""
    if active_only:
        rows = query_all(
            """
            SELECT * FROM prescriptions
            WHERE months_fulfilled < months_supply
            AND (expires_at IS NULL OR expires_at > datetime('now'))
            ORDER BY created_at DESC
            """
        )
    else:
        rows = query_all("SELECT * FROM prescriptions ORDER BY created_at DESC")
    return [_row_to_prescription(row, include_user, include_medication) for row in rows]
