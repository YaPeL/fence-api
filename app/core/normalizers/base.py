from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any


def normalize_status(value: Any) -> str:
    if isinstance(value, str):
        return value.strip().lower()
    return ""


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float | Decimal):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return False


def to_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None

    if not decimal_value.is_finite():
        return None

    return decimal_value


def parse_date(value: Any, formats: tuple[str, ...]) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if not isinstance(value, str):
        return None

    clean_value = value.strip()
    if not clean_value:
        return None

    for fmt in formats:
        try:
            return datetime.strptime(clean_value, fmt).date()
        except ValueError:
            continue
    return None
