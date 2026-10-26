class CapacityError(ValueError):
    pass


def reserve(used, requested, limit):
    updated = used + requested
    if updated > limit:
        raise CapacityError("capacity exceeded")
    return updated


def handle_request(payload):
    try:
        updated = reserve(payload["used"], payload["requested"], payload["limit"])
    except CapacityError:
        return {"status": "full", "used": payload["used"]}
    return {"status": "ok", "used": payload["used"]}
