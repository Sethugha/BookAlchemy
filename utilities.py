import json
import requests
import shutil
import wikipedia
from data_models import db, Author, Book
from flask import jsonify
from sqlalchemy import or_


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


def retrieve_entity_via_wikipedia(search_term, imgpath):
    """
    Uses wikipedia to retrieve the wiki page of the <search_term>.
    extracts the summary and image urls. This imge-url is requested afterwards
    returning the first image ending with 'jpg'
    :param search_term: any search string, one or more words
    :param imgpath: relative path of the image file, adapted to the purpose of the search.
                    author portraits are saved as /static/images/portraits/{author.id}.jpg
                    books as /static/images/{book.isbn}.jpg
    :return: page summary, str
    """
    page = wikipedia.page(search_term)
    summary = page.summary
    image_url_list = page.images
    for img_url in image_url_list:
        if img_url.endswith('jpg'):
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                with open(imgpath, 'wb') as imgfile:
                    imgfile.write(img_response.content)
    return summary

def file_convert_csv_to_json(text):
    pass

def cache_data(books):
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



def retrieve_entity_via_openlib(search_term):
    base_url = ("https://openlibrary.org/search/authors?q="
                + search_term.replace(' ', '+')
                + '&mode=everything')
    openLib = requests.get(base_url)
    if openLib.status_code == 200:
        return openLib.content


def backup_database(filepath):
    """function to create a copy of the database file
    using shutil
    return:
    """
    destination = filepath[:-2]+'sik'
    shutil.copyfile(filepath, destination)
    return "Database saved"

def query_database(query):
    if query['title']:
        print(f"searching for: {query['title']}")
        collection = db.session.query(Book).join(Author).filter(Book.title.contains(query['title'])) \
                                                        .all()
        print(f"found: {collection}")
    elif query['isbn']:
        print(f"searching for: {query['isbn']}")
        collection = db.session.query(Book).join(Author).filter(Book.isbn.contains(query['isbn'])) \
                                                        .all()
        print(f"found: {collection}")
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
             print(f"found: {collection}")
        if floor_year and top_year:
            collection = db.session.query(Book).join(Author).filter(Book.publication_year \
                                                            .between(floor_year, top_year)) \
                                                            .all()
            print(f"found: {collection}")
    elif query['authorname']:
        print(f"searching for: {query['authorname']}")
        authors = Author.query.filter(Author.name.contains(query['authorname'])).all()
        print(f"found: {authors}")
        author_ids = []
        for author in authors:
            author_ids.append(author.id)
        collection = db.session.query(Book).join(Author).filter(
                                            Book.author_id.in_(author_ids)).all()
        print(f"found: {collection}")

    if collection:
        print(f"from working query: {collection}")
        books = jsonify_query_results(collection)
        print(f" jsonified: {books.json}")
        return books.json
    return "No records found"


def query_for_keyword(text):
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
    books = jsonify_query_results(collection)
    print(f" jsonified: {books.json}")
    return books.json

def refresh_cache(book):
    books = load_cache()

    print(books)
    #for oldbook in books:
    #   if oldbook['isbn'] == book.isbn


def main():
    pass



if __name__ == '__main__':
    main()


# html codes:
# 301: Moved permanently
# 302: found
# 303: Resource wurde andernorts gefunden unm dort mit 'GET' abgerufen zu wrden. Folgt meist einem POST
# 305: Use Proxy
# Redirction unter Beibehaltung der Methode. (wird sonst zu 'get' gewandelt)
