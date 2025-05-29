from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    birth_date = db.Column(db.String)
    date_of_death = db.Column(db.String)

    books = db.relationship('Book', back_populates='author')

    def __repr__(self):
        return f"Author(id = {self.id}, name = {self.name}, birth_date = {self.birth_date}, \
            date_of_death = {self.date_of_death})"


    def ___str__(self):
        return f"{self.name}, born {self.birth_date}"


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.Integer, unique=True)
    title = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    author = db.relationship('Author', back_populates='books')


    def __repr__(self):
        return f"Book(id = {self.id}, title = {self.title}, publication_year = {self.publication_year}, \
            isbn = {self.isbn})"


    def ___str__(self):
        return f"{self.title}, isbn {self.isbn}"
