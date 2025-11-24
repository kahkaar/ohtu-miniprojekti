# pylint: disable=R0913,R0917,R0903

class Book:
    def __init__(self, book_id, title, author, year, publisher, address):
        self.id = book_id
        self.title = title
        self.author = author
        self.year = year
        self.publisher = publisher
        self.address = address

    def __str__(self):
        return f"{self.title} by {self.author}, {self.year}, {self.publisher}, {self.address}"
