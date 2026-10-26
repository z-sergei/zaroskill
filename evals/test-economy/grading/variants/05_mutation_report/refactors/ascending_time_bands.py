def cancellation_fee(hours_before, paid_cents):
    if min(hours_before, paid_cents) < 0:
        raise ValueError("negative input")
    if hours_before < 24:
        return paid_cents // 2
    if hours_before < 48:
        return paid_cents // 4
    return 0
