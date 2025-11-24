class UserInputError(Exception):
    pass


def make_bibtex(book):
    """
    Generate a BibTeX entry for a given book object.

    Args:
        book: An object representing a book, expected to have attributes
            id, author, title, year, publisher, and address.

    Returns:
        str: A string containing the BibTeX entry for the book.
    """
    tex = f"@book{{{book.id},\n"
    if book.author:
        tex += f"  author = {{{book.author}}},\n"
    if book.title:
        tex += f"  title = {{{book.title}}},\n"
    if book.year:
        tex += f"  year = {{{book.year}}},\n"
    if book.publisher:
        tex += f"  publisher = {{{book.publisher}}},\n"
    if book.address:
        tex += f"  address = {{{book.address}}},\n"
    tex += "}"
    return tex
