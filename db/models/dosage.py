"""Dosage parsing and equivalence utilities."""

import re


def parse_mg(dosage: str) -> float | None:
    """
    Parse a dosage string and extract the milligram value.

    Supports formats like:
    - "500mg", "500 mg"
    - "0.5g", "0.5 g" (converts to mg)
    - "25mg/5ml" (extracts the mg portion)

    Returns None if parsing fails.
    """
    if not dosage:
        return None

    dosage = dosage.lower().strip()

    # Try mg pattern first (most common)
    mg_match = re.match(r"^([\d.]+)\s*mg", dosage)
    if mg_match:
        return float(mg_match.group(1))

    # Try g pattern (convert to mg)
    g_match = re.match(r"^([\d.]+)\s*g(?:ram)?", dosage)
    if g_match:
        return float(g_match.group(1)) * 1000

    # Try mcg/ug pattern (convert to mg)
    mcg_match = re.match(r"^([\d.]+)\s*(?:mcg|ug)", dosage)
    if mcg_match:
        return float(mcg_match.group(1)) / 1000

    return None


def is_dosage_equivalent(
    prescribed_dosage: str,
    prescribed_quantity: int,
    requested_dosage: str,
    requested_quantity: int,
    tolerance: float = 0.25,
) -> bool:
    """
    Check if a requested dosage/quantity is equivalent to a prescription.

    Allows up to `tolerance` (default 25%) extra milligrams to account
    for rounding when using different dosage forms.

    Example:
    - Prescription: 10x50mg (500mg total)
    - Request: 5x100mg (500mg total) -> True (exact match)
    - Request: 6x100mg (600mg total) -> True (within 25% tolerance)
    - Request: 7x100mg (700mg total) -> False (exceeds tolerance)

    Returns False if dosages cannot be parsed.
    """
    prescribed_mg = parse_mg(prescribed_dosage)
    requested_mg = parse_mg(requested_dosage)

    if prescribed_mg is None or requested_mg is None:
        return False

    total_prescribed = prescribed_mg * prescribed_quantity
    total_requested = requested_mg * requested_quantity

    # Requested must not exceed prescribed + tolerance
    max_allowed = total_prescribed * (1 + tolerance)

    # Requested must be at least the prescribed amount (no under-dispensing)
    return total_prescribed <= total_requested <= max_allowed


def calculate_equivalent_quantity(
    prescribed_dosage: str,
    prescribed_quantity: int,
    stock_dosage: str,
) -> int | None:
    """
    Calculate how many units of stock_dosage are needed to fulfill a prescription.

    Returns None if dosages cannot be parsed.
    Returns the ceiling (rounded up) quantity needed.
    """
    import math

    prescribed_mg = parse_mg(prescribed_dosage)
    stock_mg = parse_mg(stock_dosage)

    if prescribed_mg is None or stock_mg is None:
        return None

    total_prescribed = prescribed_mg * prescribed_quantity

    # Calculate how many stock units needed (round up)
    return math.ceil(total_prescribed / stock_mg)


def calculate_equivalent_months(
    requested_dosage: str,
    requested_quantity: int,
    prescribed_dosage: str,
    tolerance: float = 0.25,
) -> int | None:
    """
    Calculate how many months of a prescription are consumed by a request.

    Returns the ceiling (rounded up) of equivalent months, but only if
    the rounding doesn't exceed the tolerance (default 25%).

    Example (with 25% tolerance):
    - 16 packs of 10mg with prescription of 20mg/month = 8.0 -> 8 months
    - 8 packs of 20mg with prescription of 20mg/month = 8.0 -> 8 months
    - 4 packs of 40mg with prescription of 20mg/month = 8.0 -> 8 months
    - 15 packs of 10mg with prescription of 20mg/month = 7.5 -> 8 months (within 125%)
    - 13 packs of 10mg with prescription of 20mg/month = 6.5 -> None (8 months would be >125%)

    Returns None if:
    - Dosages cannot be parsed
    - Rounding up would exceed the tolerance threshold
    """
    import math

    requested_mg = parse_mg(requested_dosage)
    prescribed_mg = parse_mg(prescribed_dosage)

    if requested_mg is None or prescribed_mg is None:
        return None

    total_requested_mg = requested_mg * requested_quantity
    exact_months = total_requested_mg / prescribed_mg
    rounded_months = math.ceil(exact_months)

    # Check if rounding up exceeds tolerance
    # e.g., if exact is 6.5 and rounded is 8, that's 8/6.5 = 1.23 (23% over)
    if exact_months > 0 and rounded_months / exact_months > (1 + tolerance):
        return None

    return rounded_months
