def delivery_fee(subtotal_cents):
    if subtotal_cents < 0:
        raise ValueError("subtotal cannot be negative")
    if subtotal_cents >= 10000:
        return 0
    if subtotal_cents > 5000:
        return 250
    return 500
