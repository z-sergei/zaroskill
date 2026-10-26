def discounted_total(subtotal_cents, percent, *, max_discount_cents=None):
    if subtotal_cents < 0 or not 0 <= percent <= 100:
        raise ValueError("invalid subtotal or percent")
    if subtotal_cents == 0:
        return 0
    if max_discount_cents is not None and max_discount_cents < 0:
        raise ValueError("invalid maximum discount")
    discount = subtotal_cents * percent // 100
    if max_discount_cents is not None:
        discount = min(discount, max_discount_cents)
    return subtotal_cents - discount
