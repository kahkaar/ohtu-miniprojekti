class UserInputError(Exception):
    pass


def make_bibtex(book):
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
