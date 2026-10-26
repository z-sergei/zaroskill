def delivery_fee(subtotal_cents):
    if subtotal_cents < 0:
        return 500
    if subtotal_cents >= 10000:
        return 0
    if subtotal_cents >= 5000:
        return 250
    return 500
