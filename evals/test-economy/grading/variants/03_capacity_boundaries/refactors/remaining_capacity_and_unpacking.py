class CapacityError(ValueError):
    pass


def reserve(used, requested, limit):
    if requested <= limit - used:
        return requested + used
    raise CapacityError("not enough room")


def handle_request(payload):
    used, requested, limit = (payload[k] for k in ("used", "requested", "limit"))
    try:
        total = reserve(used, requested, limit)
    except CapacityError:
        status, total = "full", used
    else:
        status = "ok"
    return dict(status=status, used=total)
