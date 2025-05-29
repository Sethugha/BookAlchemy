from data_models import db, Author, Book
import requests
import os
from tkinter import *
from PIL import ImageTk, Image


def load_csv(file, has_header):
    """
    Load csv with books for bulk import into database.
    Delivered from flask are the file and a boolean 'has_header'
    which determines if the first line is skipped.
    :parameter file: filepath to csv-file
    :parameter has_header:True if csv has a header
    :returns: Success: A list of lists is returned
              Fail: The error message is returned as string
    """
    booklist = []
    try:
        with open(file, "r") as csfile:
            if has_header:
                csfile.readline()
            lines = csfile.readlines()
            for line in lines:
                booklist.append(line)
        return booklist
    except Exception as e:
        return f"File access error, details: {e}."


def add_book_to_database(book, isbn):
    """
    A list of Book attributes (a single book) and an ISBN to precheck
    if the book is already in the database.
    If not, an attempt to add the book to the database follows.
    :parameter book: Book attributes to insert into database
    :parameter isbn: because of its uniqueness the isbn is the best way to
                     check for doubles.
    """
    item = db.session.query(Book.id).filter(Book.isbn == isbn).all()
    if item:
        return f"Book with isbn {isbn} already in database: row id = {item[0]}"
    try:
        db.session.add(book)
        db.session.commit()
        return f"Successfully added {isbn}."
    except Exception as e:
        db.session.rollback()
        return f"Book insertion failed, see {e}"


def retrieve_book_cover_from_url(url):
    im = Image.open(requests.get(url, stream=True).raw)
    return im


def main():
    im = retrieve_book_cover_from_url("https://covers.openlibrary.org/b/isbn/9798893540673-M.jpg")
    im

if __name__ == '__main__':
    main()
