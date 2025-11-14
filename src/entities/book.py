class Book:
    def __init__(self, id, title, author, year, publisher, address):
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        self.publisher = publisher
        self.address = address

    def __str__(self):
        return f"{self.title} by {self.author}, {self.year}, {self.publisher}, {self.address}"