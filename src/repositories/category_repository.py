from sqlalchemy import text

from config import db
from util import to_category, to_tag


def get_categories():
    """Fetches all categories from the database"""

    sql = text(
        """
        SELECT id, name
        FROM categories
        ORDER BY name, id
        """
    )

    result = db.session.execute(sql).fetchall()

    if not result:
        return []

    return [to_category(row) for row in result]


def get_tags():
    """Fetches all tags from the database"""

    sql = text(
        """
        SELECT id, name
        FROM tags
        ORDER BY name, id
        """
    )

    result = db.session.execute(sql).fetchall()

    if not result:
        return []

    return [to_tag(row) for row in result]


def get_category(category_id):
    """Fetches a category by its ID from the database"""

    sql = text(
        """
        SELECT id, name
        FROM categories
        WHERE id = :category_id
        """
    )

    params = {
        "category_id": category_id,
    }

    result = db.session.execute(sql, params).fetchone()

    if not result:
        return None

    return to_category(result)


def get_tag(tag_id):
    """Fetches a tag by its ID from the database"""

    sql = text(
        """
        SELECT id, name
        FROM tags
        WHERE id = :tag_id
        """
    )

    params = {
        "tag_id": tag_id,
    }

    result = db.session.execute(sql, params).fetchone()

    if not result:
        return None

    return to_tag(result)


def create_category(name):
    """Creates a new category in the database"""

    sql = text(
        """
        INSERT INTO categories (name)
        VALUES (:name)
        RETURNING id, name
        """
    )

    params = {
        "name": name,
    }

    result = db.session.execute(sql, params).fetchone()
    db.session.commit()

    return to_category(result)


def create_tag(name):
    """Creates a new tag in the database"""

    sql = text(
        """
        INSERT INTO tags (name)
        VALUES (:name)
        RETURNING id, name
        """
    )

    params = {
        "name": name,
    }

    result = db.session.execute(sql, params).fetchone()
    db.session.commit()

    return to_tag(result)


def create_tags(tag_names):
    """Creates multiple tags in the database"""

    sql = text(
        """
        INSERT INTO tags (name)
        VALUES (:name)
        RETURNING id, name
        """
    )

    created_tags = []
    for name in tag_names:
        params = {
            "name": name,
        }

        result = db.session.execute(sql, params).fetchone()
        created_tags.append(to_tag(result))

    db.session.commit()

    return created_tags


def get_or_create_category(name):
    """Fetches a category by name or creates it if it does not exist"""

    sql = text(
        """
        SELECT id, name
        FROM categories
        WHERE name = :name
        """
    )

    params = {
        "name": name,
    }

    result = db.session.execute(sql, params).fetchone()

    if result:
        return to_category(result)

    return create_category(name)


def get_or_create_tag(name):
    """Fetches a tag by name or creates it if it does not exist"""

    sql = text(
        """
        SELECT id, name
        FROM tags
        WHERE name = :name
        """
    )

    params = {
        "name": name,
    }

    result = db.session.execute(sql, params).fetchone()

    if result:
        return to_tag(result)

    return create_tag(name)


def get_or_create_tags(tag_names):
    """Fetches multiple tags by name or creates them if they do not exist"""

    existing_tags = {}
    sql = text(
        """
        SELECT id, name
        FROM tags
        WHERE name = :name
        """
    )

    for name in tag_names:
        params = {
            "name": name,
        }

        result = db.session.execute(sql, params).fetchone()

        if result:
            existing_tags[name] = to_tag(result)

    tags_to_create = [name for name in tag_names if name not in existing_tags]

    created_tags = create_tags(tags_to_create)

    for tag in created_tags:
        existing_tags[tag.name] = tag

    return list(existing_tags.values())


def assign_tag_to_citation(citation_id, tag):
    """Assigns a single tag to a citation."""

    sql = text(
        """
        INSERT INTO tags (citation_id, tag_id)
        VALUES (:citation_id, :tag_id)
        """
    )

    params = {
        "citation_id": citation_id,
        "tag_id": tag.id,
    }

    db.session.execute(sql, params)
    db.session.commit()


def assign_tags_to_citation(citation_id, tags):
    """Assigns multiple tags to a citation"""

    sql = text(
        """
        INSERT INTO tags (citation_id, tag_id)
        VALUES (:citation_id, :tag_id)
        """
    )

    for tag in tags:
        params = {
            "citation_id": citation_id,
            "tag_id": tag.id,
        }

        db.session.execute(sql, params)

    db.session.commit()


def assign_category_to_citation(citation_id, category_id):
    """Assigns a category to a citation"""

    sql = text(
        """
        INSERT INTO categories (citation_id, category_id)
        VALUES (:citation_id, :category_id)
        """
    )

    params = {
        "citation_id": citation_id,
        "category_id": category_id,
    }

    db.session.execute(sql, params)
    db.session.commit()


def remove_tag_from_citation(tag_id, citation_id):
    """Removes a tag from a citation"""

    sql = text(
        """
        DELETE FROM tags
        WHERE citation_id = :citation_id AND tag_id = :tag_id
        """
    )

    params = {
        "citation_id": citation_id,
        "tag_id": tag_id,
    }

    db.session.execute(sql, params)
    db.session.commit()


def remove_category_from_citation(category_id, citation_id):
    """Removes a category from a citation"""

    sql = text(
        """
        DELETE FROM categories
        WHERE citation_id = :citation_id AND category_id = :category_id
        """
    )

    params = {
        "citation_id": citation_id,
        "category_id": category_id,
    }

    db.session.execute(sql, params)
    db.session.commit()
