class Citation:
    def __init__(self, citation_id, entry_type, citation_key, fields):
        self._id = citation_id
        self._entry_type = entry_type
        self._citation_key = citation_key
        self._fields = fields

    @property
    def id(self):
        return self._id

    @property
    def entry_type(self):
        return self._entry_type

    @property
    def citation_key(self):
        return self._citation_key

    @property
    def fields(self):
        return self._fields

    def _format_container(self, data):
        """
        Build container string from available fields
        (journaltitle/booktitle/publisher, volume/number, pages).
        """
        journaltitle = data.get("journaltitle")
        booktitle = data.get("booktitle")
        publisher = data.get("publisher")

        volume = data.get("volume")
        number = data.get("number")
        pages = data.get("pages")

        segments = []
        first = journaltitle or booktitle or publisher
        if first:
            segments.append(first)

        if volume:
            seg = str(volume) + (f"({number})" if number else "")
            segments.append(seg)

        if pages:
            segments.append(f"pp. {pages}")

        return ", ".join(s for s in segments if s)

    def to_human_readable(self):
        """Return a human-readable string representation of the citation."""
        data = self.fields or {}

        author = data.get("author")
        year = data.get("year")
        header_parts = [p for p in (
            author, f"({year})" if year else None) if p]
        parts = [" ".join(header_parts).strip() + "."] if header_parts else []

        title = data.get("title")
        if title:
            parts.append(f"{title}.")

        container = self._format_container(data)
        if container:
            parts.append(container)

        result = " ".join(p.strip() for p in parts if p).strip()
        if result and not result.endswith("."):
            result += "."

        if not result:
            return f"{self.citation_key} ({self.entry_type})"

        return result

    def to_compact(self):
        """Return a compact one-line representation: entry type — key — brief fields."""
        items = sorted(self.fields.items())
        brief = ", ".join(v for k, v in items[:3])
        if len(items) > 3:
            brief += ", ..."

        return f"{self.entry_type} — {self.citation_key} — {brief}"

    def to_bibtex(self):
        """Return a BibTeX string representation of the citation."""
        tab_size = 2  # Maybe able to configure?
        spaces = tab_size * " "

        items = sorted(self.fields.items())

        fields_str = f",\n{spaces}".join(
            f"{k} = {{{v}}}" for k, v in items
        )

        bibtex_str = f"@{self.entry_type}{{{self.citation_key},\n{spaces}{fields_str}\n}}"
        return bibtex_str

    def to_dict(self):
        """Return a plain dict representation of the citation."""
        return {
            "id": self.id,
            "entry_type": self.entry_type,
            "citation_key": self.citation_key,
            "fields": self.fields,
        }

    def __str__(self):
        return f"@{self.entry_type}{{{self.citation_key}, {self.fields}}}"

    def __repr__(self):
        d = self.to_dict()
        return f"{self.__class__!s}({d!r})"
