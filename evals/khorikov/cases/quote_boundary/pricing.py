"""A pure quote boundary; all amounts are integer minor currency units."""
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Line:
    unit_minor: int
    quantity: int


@dataclass(frozen=True)
class Quote:
    gross_minor: int
    discount_minor: int
    shipping_minor: int
    total_minor: int


def quote(lines: Iterable[Line], percent: int, shipping_minor: int, digital: bool = False) -> Quote:
    items = tuple(lines)
    if not items:
        raise ValueError("An order needs at least one line")
    if type(percent) is not int or not 0 <= percent <= 100:
        raise ValueError("Discount must be an integer percentage from 0 to 100")
    if type(shipping_minor) is not int or shipping_minor < 0:
        raise ValueError("Shipping must be non-negative integer minor units")
    for item in items:
        if type(item.unit_minor) is not int or item.unit_minor < 0 or type(item.quantity) is not int or item.quantity <= 0:
            raise ValueError("Each line needs a non-negative integer price and positive integer quantity")
    gross = sum(item.unit_minor * item.quantity for item in items)
    discount = (gross * percent + 50) // 100
    subtotal = gross - discount
    shipping = 0 if digital or subtotal >= 5000 else shipping_minor
    return Quote(gross, discount, shipping, subtotal + shipping)
