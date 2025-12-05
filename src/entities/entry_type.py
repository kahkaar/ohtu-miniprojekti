class EntryType:
    """Represents an entry type entity."""

    def __init__(self, entry_type_id, name):
        self._id = entry_type_id
        self._name = name

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def to_dict(self):
        """Return a plain dict representation of the entry type."""

        return {
            "id": self.id,
            "name": self.name,
        }

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        d = self.to_dict()
        return f"{self.__class__!s}({d!r})"
