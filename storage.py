import json
import utilities
import os.path
from data_models import db, Author, Book
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, PendingRollbackError
import shutil


def cache_data(books):
    """
    This function caches the actual cursor in a json-file. This cache
    is used to adapt the book-wheel to the cursor, will later be used to
    minimize frequent database access within the same cursor.
    """
    try:
        with open('cache.json', 'w') as cache:
            json.dump(books, cache, indent=4)
        return None
    except Exception as e:
        message = f"Something went wrong during cache-access: {e}."
        return message


def load_cache():
    """
    Loads storage file contents into memory
    as list of dictionaries.
    return: List of dict
    """
    try:
        with open('cache.json', 'r') as cache:
            books = json.load(cache)
        return books
    except Exception as e:
        return f"Error loading cache file. Exception {e}!"


def remove_from_cache(book_id):
    """
    Deleted books must be removed from cache to mirror the changes
    in carousel display.
    :param book_id: deleted book´s id
    :return:
    """
    books = load_cache()
    for book in books:
        if book['id'] == book_id:
            books.remove(book)
    cache_data(books)
    return 0


def query_database(query):
    """
    Database query of url-based keywords
    The current version only allows single keywords.
    parameter query: dictionary with columns as keys, keywords as values
    return: jsonified set of rows
            or message if no records found
    """
    if query['title']:
        collection = (db.session.query(Book) \
                                .join(Author) \
                                .filter(Book \
                                        .title \
                                        .contains(query['title'])) \
                                .all())

    elif query['isbn']:
        collection = (db.session.query(Book)
                      .join(Author) \
                      .filter(Book \
                              .isbn \
                              .contains(query['isbn'])) \
                      .all())

    elif query['year']:
        print(f"searching for: {query['year']}")
        year = query['year']
        valid_year = True
        top_year = 0
        floor_year = 0
        if year.find('-'):
            limits = year.split('-').strip()
            for year in limits:
                if not year.isdigits():
                    valid_year = False
                floor_year = int(limits[0])
                top_year = int(limits[1])
        if not year.isdigits():
            valid_year = False
        if valid_year:
            year = int(year)
        if isinstance(year, int):
            collection = db.session.query(Book) \
                                   .join(Author) \
                                   .filter(Book \
                                           .publication_year == year) \
                                           .all()
        if floor_year and top_year:
            collection = db.session.query(Book) \
                                   .join(Author) \
                                  .filter(Book \
                                          .publication_year \
                                          .between(floor_year, top_year)) \
                                          .all()
    elif query['authorname']:
        authors = Author.query.filter(Author \
                                      .name.contains(query['authorname'])) \
                                      .all()
        author_ids = []
        for author in authors:
            author_ids.append(author.id)
        collection = db.session.query(Book) \
                                     .join(Author) \
                                     .filter(Book \
                                             .author_id \
                                             .in_(author_ids)) \
                                     .all()
    if collection:
        books = utilities.jsonify_query_results(collection)
        return books.json
    return "No records found"


def query_for_keyword(text):
    """
    Queries over database columns looking for a match with a single keyword.
    Core of the keyword-query .
    :param text: search term or fragment
    :return:
    """
    if text:
        author_ids = []
        authors = Author.query.filter(Author.name.contains(text)).all()
        for author in authors:
            author_ids.append(author.id)
        collection = db.session.query(Book) \
                                     .join(Author) \
                                     .filter(or_(Book \
                                                 .title \
                                                 .contains(text), \
                                                           Book.isbn.contains(text), \
                                                           Book.publication_year == text, \
                                                           Book.author_id.in_(author_ids))) \
                                     .all()
    else:
        collection = db.session.query(Book) \
                                     .join(Author) \
                                     .all()
    books = utilities.jsonify_query_results(collection)
    return books.json


def add_author_to_db(author):
    """
    Function to add a new instance of Author to db
    As an automatic portrait import is still under construction
    feel free to add a portrait to static/images/portraits
    named <id>.png or use the joker named 0.png
    :parameter author: New instance of Author
    :return: message
    """
    try:
        db.session.add(author)
        db.session.commit()
        return f"{author.name}, born {author.birth_date} successfully added."
    except IntegrityError:
        db.session.rollback()
        return f"Another author with the same data already present. Insertion aborted."
    except PendingRollbackError:
        while db.session.registry().in_transaction():
            db.session.rollback()
        return  "operation terminated due to a failed insert or update before,  \
                 waiting for an orderly rollback. Cleared transaction log of pending \
                 transactions"
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        db.session.rollback()
        return f"Something went wrong: Exception {e}."


def add_book_to_db(book):
    """Stores a single book in the database. As the automatic picture import
    is still under construction feel free to add a cover img to static/images
    named <isbn>.png. Alternatively there is a joker named void.png.
    :parameter: new Book instance "book"
    :return: message
    """
    try:
        db.session.add(book)
        db.session.commit()
        return f"{book.title}, ISBN {book.isbn} successfully added to books."
    except IntegrityError:
        db.session.rollback()
        return "Uniqueness violated. Insertion aborted.  \
                Maybe you stated a wrong ISBN?"
    except PendingRollbackError:
        while db.session.registry().in_transaction():
            db.session.rollback()
        return "Operation terminated due to a failed insert or update before,  \
                 waiting for an orderly rollback. Cleared transaction log of pending \
                 transactions"
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        db.session.rollback()
        return f"Something went wrong: Exception {e}."


def bulk_insert_bookshelf(data):
    """
    Bulk import of a bookshelf into db. not fully developed but functional.
    A small input file can be found in the root folder.
    cover pictures must be added afterwards.
    Bulk imports expect the author ids thus authors must be added before.
    parameter data: booklist converted from csv to json
    return: message
    """
    try:
        db.session.bulk_insert_mappings(Book, data)
        db.session.commit()
        return f"Bulk {data} successfully added to books."
    except IntegrityError:
        db.session.rollback()
        return """Uniqueness violated. Insertion aborted.
                  Please check the imported list for doubles."""
    except PendingRollbackError:
        db.session.rollback()
        return """Operation terminated due to a failed insert or update before,
                                             waiting for an orderly rollback."""
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        db.session.rollback()
        return f"Something went wrong: Exception {e}."


def remove_author(author_id):
    """
    Removes author with given id from database.
    :param author_id: author_id, int
    :return: Log entry if successful,
             error message, if not.
    """
    author = db.session.query(Author).filter(Author.id == author_id).first()
    try:
        db.session.delete(author)
        db.session.commit()
        return f"{author.name}, successfully removed."
    except PendingRollbackError:
        while db.session.registry().in_transaction():
            db.session.rollback()
        return "Operation terminated due to a failed insert or update before,  \
                 waiting for an orderly rollback. Cleared transaction log of pending \
                 transactions"
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        db.session.rollback()
        return f"Something went wrong: Exception {e}."


def create_portrait_wildcard(author):
    """
    Compares, if a portrait named {author_id}.png exists
    and, if not, copies the prepared joker 0.png.
    :return:
    """
    try:
        filepath = f'static/images/Portraits/{author.id}.png'
        if not os.path.isfile(filepath):
            shutil.copyfile('static/images/Portraits/void.png', filepath)
    except Exception as e:
        print(f"Joker fabrication failed: Error {e}.")
    return 0


def create_cover_wildcard(book):
    """
    Compares if a cover named {ISBN}.png exists
    and, if not, copies the prepared joker void.png.
    :return:
    """
    try:
        filepath = f'static/images/{book.isbn}.png'
        if not os.path.isfile(filepath):
            shutil.copyfile('static/images/void.png', filepath)
    except Exception as e:
        print(f"Joker fabrication failed: Error {e}.")
    return 0
