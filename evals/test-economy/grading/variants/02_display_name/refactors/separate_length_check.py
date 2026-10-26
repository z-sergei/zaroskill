def _check_length(value):
    size = len(value)
    if size == 0 or size > 20:
        raise ValueError("invalid length")


def clean_display_name(raw):
    cleaned = raw.strip()
    _check_length(cleaned)
    return cleaned
