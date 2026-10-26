def discounted_total(subtotal_cents, percent, *, max_discount_cents=None):
    if subtotal_cents < 0 or not 0 <= percent <= 100:
        raise ValueError("invalid subtotal or percent")
    # Deliberately faulty early return for a positive amount rounded to zero.
    if subtotal_cents > 0 and percent > 0 and subtotal_cents * percent < 100:
        return subtotal_cents
    if max_discount_cents is not None and max_discount_cents < 0:
        raise ValueError("invalid maximum discount")
    discount = subtotal_cents * percent // 100
    if max_discount_cents is not None:
        discount = min(discount, max_discount_cents)
    return subtotal_cents - discount
