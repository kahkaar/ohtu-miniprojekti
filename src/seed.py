import os

from config import app


def seed_demo(data=None, json_path=None):
    """Insert demo data.

    Parameters:
    - data: optional dict in the same shape as `src/demo_data.json`. If
      provided, entries are taken from this dict. Otherwise the function
      will try to load the JSON file from `json_path` or
      `src/demo_data.json` next to this module.

    The JSON shape is expected to be:
      { "categories": [...], "tags": [...], "citations": [...] }

    The function is idempotent for tags/categories and will skip or log
    errors for duplicate citation keys.
    """
    # Import inside function to avoid import cycles when module is imported
    from repositories.category_repository import (
        get_or_create_category,
        get_or_create_tags,
    )
    from repositories.citation_repository import create_citation_with_metadata
    from repositories.entry_type_repository import get_entry_type_by_name

    print("Seeding demo data...")

    # Load data from provided dict or JSON file next to this module.
    import json

    if data is None:
        json_path = json_path or os.path.join(
            os.path.dirname(__file__), "demo_data.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Demo data not provided and file not found: {json_path}"
            )

    categories = data.get("categories", [])
    tags = data.get("tags", [])
    citations = data.get("citations", [])

    created_categories = {name: get_or_create_category(
        name) for name in categories}
    created_tags_list = get_or_create_tags(tags)
    created_tags = {t.name: t for t in created_tags_list}

    def et(name):
        return get_entry_type_by_name(name)

    for c in citations:
        cat = c.get("category")
        if isinstance(cat, str):
            c_category = created_categories.get(cat)
        else:
            c_category = cat

        raw_tags = c.get("tags") or []
        tag_objs = []
        for t in raw_tags:
            if hasattr(t, "id"):
                tag_objs.append(t)
            else:
                tag_obj = created_tags.get(t)
                if tag_obj:
                    tag_objs.append(tag_obj)

        try:
            create_citation_with_metadata(
                entry_type=et(c["entry_type"]),
                citation_key=c["citation_key"],
                fields=c.get("fields") or {},
                categories=[c_category],
                tags=tag_objs,
            )
        except Exception as exc:
            print(
                f"Failed to create demo citation {c.get('citation_key')}: {exc}")

    print("Demo data seeded")


if __name__ == "__main__":
    with app.app_context():
        seed_demo()
