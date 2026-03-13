from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def parse_decimal(value: str | None) -> Decimal | None:
    if value is None or value.strip() == "":
        return None
    normalized = value.replace(",", ".").strip()
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
