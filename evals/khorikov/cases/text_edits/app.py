"""Apply non-overlapping edits expressed in original Python string offsets."""


def apply_edits(text, edits):
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized = []
    for edit in edits:
        if not isinstance(edit, (tuple, list)) or len(edit) != 3:
            raise TypeError("each edit must be a three-item tuple or list")
        start, stop, replacement = edit
        if (not isinstance(start, int) or isinstance(start, bool)
                or not isinstance(stop, int) or isinstance(stop, bool)):
            raise TypeError("offsets must be integers, not booleans")
        if not isinstance(replacement, str):
            raise TypeError("replacement must be a string")
        if not (0 <= start <= stop <= len(text)):
            raise ValueError("edit is outside the text")
        normalized.append((start, stop, replacement))

    ordered = sorted(normalized, key=lambda edit: (edit[0], edit[1]))
    pieces = []
    cursor = 0
    for start, stop, replacement in ordered:
        if start < cursor:
            raise ValueError("edits overlap")
        pieces.append(text[cursor:start])
        pieces.append(replacement)
        cursor = stop
    pieces.append(text[cursor:])
    return "".join(pieces)
