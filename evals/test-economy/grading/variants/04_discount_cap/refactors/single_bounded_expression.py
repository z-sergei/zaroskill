def discounted_total(subtotal_cents, percent, *, max_discount_cents=None):
    invalid_base = subtotal_cents < 0 or percent < 0 or percent > 100
    invalid_cap = max_discount_cents is not None and max_discount_cents < 0
    if invalid_base or invalid_cap:
        raise ValueError("invalid discount input")
    computed = (percent * subtotal_cents) // 100
    limit = computed if max_discount_cents is None else max_discount_cents
    return subtotal_cents - (computed if computed <= limit else limit)
