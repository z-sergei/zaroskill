def fee(weight):
    if not 1 <= weight <= 20:
        raise ValueError('unsupported weight')
    return 4 if weight <= 5 else 7
