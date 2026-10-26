def cancellation_fee(hours_before, paid_cents):
    if hours_before < 0 or paid_cents < 0:
        raise ValueError("arguments cannot be negative")
    if hours_before >= 48:
        return 0
    if hours_before >= 24:
        return paid_cents // 4
    return (paid_cents + 1) // 2
