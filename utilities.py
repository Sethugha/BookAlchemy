import json
import shutil
from data_models import db, Author, Book
from flask import jsonify
from sqlalchemy import or_
import storage

def convert_date_string(datestring):
    """
    Converts the date, which are submitted by add_author,
    into german style date-strings. Only for my convenience.
    :returns: German style datestring, type String
              e.g: 01.01.2010 instead of 2010-01-01
     """
    return datestring[-2:] + '.' + datestring[-5:-3] + '.' + datestring[:4]



def jsonify_query_results(collection):
    """converts result sets of database queries to json
    to enable """
    books = jsonify([
            {
                "id": book.id,
                "title": book.title,
                "author": book.author.name,
                "publication_year": book.publication_year,
                "authors_birth_date": book.author.birth_date,
                "authors_date_of_death": book.author.date_of_death,
                "isbn": book.isbn,
                "img": f"static/images/{book.isbn}.png",
                "face": f"static/images/Portraits/{book.author_id}.png"
            } for book in collection
        ])
    return books


def backup_database(filepath):
    """function to create a copy of the database file
    using shutil. As no data operations are made,
    this function is categorized as utility.
    return:
    """
    destination = filepath[:-2]+'sik'
    shutil.copyfile(filepath, destination)
    return "Database saved"
