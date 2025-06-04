import json
from data_models import db, Author, Book
from sqlalchemy import or_
import utilities


def cache_data(books):
    """
    This function caches the actual cursor in a json-file. This cache
    is used to adapt the book-wheel to the cursor, will later be used to
    minimize frequent database access within the same cursor.
    """
    with open('cache.json', 'w') as cache:
        json.dump(books, cache, indent=4)
    return 0


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
        collection = db.session.query(Book).join(Author).filter(Book.title.contains(query['title'])) \
                                                        .all()
    elif query['isbn']:
        collection = db.session.query(Book).join(Author).filter(Book.isbn.contains(query['isbn'])) \
                                                        .all()
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
             collection = db.session.query(Book).join(Author).filter(Book.publication_year == year) \
                                                             .all()
        if floor_year and top_year:
            collection = db.session.query(Book).join(Author).filter(Book.publication_year \
                                                            .between(floor_year, top_year)) \
                                                            .all()
    elif query['authorname']:
        authors = Author.query.filter(Author.name.contains(query['authorname'])).all()
        author_ids = []
        for author in authors:
            author_ids.append(author.id)
        collection = db.session.query(Book).join(Author).filter(
                                            Book.author_id.in_(author_ids)).all()
    if collection:
        books = utilities.jsonify_query_results(collection)
        return books.json
    return "No records found"


def query_for_keyword(text):
    """
    Queries over database columns looking for a match with a single keyword
    :param text: search term or fragment
    :return:
    """
    if text:
        author_ids = []
        authors = Author.query.filter(Author.name.contains(text)).all()
        for author in authors:
            author_ids.append(author.id)
        collection = db.session.query(Book).join(Author).filter(or_(Book.title.contains(text), \
                                                         Book.isbn.contains(text), \
                                                         Book.publication_year == text, \
                                                         Book.author_id.in_(author_ids))) \
                                                        .all()
    else:
        collection = db.session.query(Book).join(Author).all()
    books = utilities.jsonify_query_results(collection)
    return books.json
