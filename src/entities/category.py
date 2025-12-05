class Category():
    """A Category represents a classification for entries."""

    def __init__(self, category_id, name):
        self._id = category_id
        self._name = name

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def to_dict(self):
        """Return a plain dict representation of the category."""
        return {
            "id": self._id,
            "name": self._name,
        }

    def __str__(self):
        return f"{self._name}"

    def __repr__(self):
        d = self.to_dict()
        return f"{self.__class__!s}({d!r})"


class Tag(Category):
    """A Tag is a specialized Category used for tagging entries."""
    # pylint: disable=W0246

    def __init__(self, tag_id, name):
        super().__init__(tag_id, name)
