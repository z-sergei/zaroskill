def discounted_total(subtotal_cents, percent):
    if subtotal_cents < 0 or not 0 <= percent <= 100:
        raise ValueError("invalid subtotal or percent")
    discount = subtotal_cents * percent // 100
    return subtotal_cents - discount
