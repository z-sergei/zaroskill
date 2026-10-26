import unicodedata

def clean_display_name(raw):
    name = unicodedata.normalize("NFC", raw.strip())
    if not 1 <= len(name) <= 20:
        raise ValueError("display name must contain 1 to 20 characters")
    return name
