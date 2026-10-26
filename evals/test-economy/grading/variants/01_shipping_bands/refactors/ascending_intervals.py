def delivery_fee(subtotal_cents):
    if subtotal_cents < 0:
        raise ValueError("negative amount")
    for end, fee in ((5000, 500), (10000, 250)):
        if subtotal_cents < end:
            return fee
    return 0
