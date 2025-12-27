"""Stock/inventory repository."""

from db import medications
from db.connection import execute, query_all, query_one
from db.models import Stock, StockAvailability


def _row_to_stock(row: dict, include_medication: bool = False) -> Stock:
    """Convert a database row to a Stock model."""
    stock = Stock(
        id=row["id"],
        medication_id=row["medication_id"],
        dosage=row["dosage"],
        quantity=row["quantity"],
        updated_at=row["updated_at"],
    )
    if include_medication:
        stock.medication = medications.get_by_id(row["medication_id"])
    return stock


def get_by_id(stock_id: int, include_medication: bool = False) -> Stock | None:
    """Get a stock entry by ID."""
    row = query_one("SELECT * FROM stock WHERE id = ?", (stock_id,))
    if not row:
        return None
    return _row_to_stock(row, include_medication)


def get_by_medication_id(
    medication_id: int,
    dosage: str | None = None,
    include_medication: bool = False,
) -> list[Stock]:
    """Get stock entries for a medication, optionally filtered by dosage."""
    if dosage:
        rows = query_all(
            "SELECT * FROM stock WHERE medication_id = ? AND dosage = ?",
            (medication_id, dosage),
        )
    else:
        rows = query_all(
            "SELECT * FROM stock WHERE medication_id = ? ORDER BY dosage",
            (medication_id,),
        )
    return [_row_to_stock(row, include_medication) for row in rows]


def get_by_medication_name(
    name: str,
    dosage: str | None = None,
    include_medication: bool = False,
) -> list[Stock]:
    """Get stock entries by medication name."""
    med = medications.get_by_name(name)
    if not med:
        return []
    return get_by_medication_id(med.id, dosage, include_medication)


def check_availability(
    medication_id: int,
    dosage: str | None = None,
) -> StockAvailability:
    """
    Check stock availability for a medication/dosage.

    Returns a StockAvailability with:
    - exact_match: The stock entry if exact dosage found
    - available_quantity: Quantity for the exact match
    - alternatives: Other dosages available if no exact match or no dosage specified
    """
    result = StockAvailability(
        medication_id=medication_id,
        requested_dosage=dosage,
    )

    # Get all stock for this medication
    all_stock = get_by_medication_id(medication_id)

    if not all_stock:
        return result

    if dosage:
        # Look for exact match
        for stock_item in all_stock:
            if stock_item.dosage == dosage:
                result.exact_match = stock_item
                result.available_quantity = stock_item.quantity
            else:
                result.alternatives.append(stock_item)
    else:
        # No dosage specified - return all as alternatives
        result.alternatives = all_stock
        result.available_quantity = sum(s.quantity for s in all_stock)

    return result


def update_quantity(stock_id: int, quantity: int) -> bool:
    """Update the quantity for a stock entry."""
    execute(
        "UPDATE stock SET quantity = ?, updated_at = datetime('now') WHERE id = ?",
        (quantity, stock_id),
    )
    return True


def decrement(stock_id: int, amount: int = 1) -> bool:
    """Decrement stock quantity by amount. Returns False if insufficient stock."""
    row = query_one("SELECT quantity FROM stock WHERE id = ?", (stock_id,))
    if not row or row["quantity"] < amount:
        return False

    execute(
        "UPDATE stock SET quantity = quantity - ?, updated_at = datetime('now') WHERE id = ?",
        (amount, stock_id),
    )
    return True


def get_low_stock(threshold: int = 10, include_medication: bool = False) -> list[Stock]:
    """Get all stock entries with quantity below threshold."""
    rows = query_all(
        "SELECT * FROM stock WHERE quantity <= ? ORDER BY quantity",
        (threshold,),
    )
    return [_row_to_stock(row, include_medication) for row in rows]


def get_all(include_medication: bool = False) -> list[Stock]:
    """Get all stock entries."""
    rows = query_all("SELECT * FROM stock ORDER BY medication_id, dosage")
    return [_row_to_stock(row, include_medication) for row in rows]
