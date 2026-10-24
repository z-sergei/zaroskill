def total(amount):
    if amount < 0:
        raise ValueError('negative amount')
    return amount + 3
