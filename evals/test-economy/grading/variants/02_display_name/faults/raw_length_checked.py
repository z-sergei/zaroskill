def clean_display_name(raw):
    name = raw.strip()
    if not 1 <= len(raw) <= 20:
        raise ValueError("display name must contain 1 to 20 characters")
    return name
