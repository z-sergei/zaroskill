"""An in-memory document revision store with explicit optimistic preconditions."""


class DocumentExistsError(LookupError):
    """A document with this ID already exists."""


class DocumentNotFoundError(LookupError):
    """The requested document does not exist."""


class RevisionNotFoundError(LookupError):
    """The requested positive revision does not exist."""


class VersionConflictError(RuntimeError):
    """The expected version is not the current version."""


def _validate_id(document_id):
    if type(document_id) is not str:
        raise TypeError("document_id must be a string")
    if not document_id:
        raise ValueError("document_id must not be empty")


def _validate_version(version):
    if type(version) is not int:
        raise TypeError("version must be an integer")
    if version < 1:
        raise ValueError("version must be positive")


def _validate_content(content):
    if type(content) is not dict:
        raise TypeError("content must be a dict")
    for key, value in content.items():
        if type(key) is not str:
            raise TypeError("content keys must be strings")
        if type(value) is str:
            continue
        if type(value) is list and all(type(item) is str for item in value):
            continue
        raise TypeError("content values must be strings or lists of strings")


def _copy_content(content):
    return {key: value[:] if type(value) is list else value for key, value in content.items()}


def _snapshot(document_id, version, content):
    return {"document_id": document_id, "version": version, "content": _copy_content(content)}


class RevisionStore:
    """See task.md for the public, authoritative contract."""

    def __init__(self):
        self._revisions = {}

    def _require(self, document_id):
        try:
            return self._revisions[document_id]
        except KeyError:
            raise DocumentNotFoundError(document_id) from None

    def create(self, document_id, content):
        _validate_id(document_id)
        _validate_content(content)
        if document_id in self._revisions:
            raise DocumentExistsError(document_id)
        self._revisions[document_id] = [_copy_content(content)]
        return _snapshot(document_id, 1, self._revisions[document_id][0])

    def read(self, document_id, *, version=None):
        _validate_id(document_id)
        if version is not None:
            _validate_version(version)
        revisions = self._require(document_id)
        selected_version = len(revisions) if version is None else version
        if selected_version > len(revisions):
            raise RevisionNotFoundError((document_id, selected_version))
        return _snapshot(document_id, selected_version, revisions[selected_version - 1])

    def history(self, document_id):
        _validate_id(document_id)
        revisions = self._require(document_id)
        return [_snapshot(document_id, number, content) for number, content in enumerate(revisions, 1)]

    def replace(self, document_id, content, *, expected_version):
        return self.replace_many([(document_id, expected_version, content)])[0]

    def replace_many(self, changes):
        if type(changes) is not list:
            raise TypeError("changes must be a list")
        seen = set()
        for entry in changes:
            if type(entry) is not tuple or len(entry) != 3:
                raise TypeError("each change must be a three-item tuple")
            document_id, expected_version, content = entry
            _validate_id(document_id)
            _validate_version(expected_version)
            _validate_content(content)
            if document_id in seen:
                raise ValueError("a batch cannot mention a document twice")
            seen.add(document_id)

        for document_id, expected_version, content in changes:
            revisions = self._require(document_id)
            if len(revisions) != expected_version:
                raise VersionConflictError(document_id)

        committed = []
        for document_id, expected_version, content in changes:
            revisions = self._require(document_id)
            revisions.append(_copy_content(content))
            committed.append(_snapshot(document_id, len(revisions), revisions[-1]))
        return committed
