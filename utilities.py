import shutil
from flask import jsonify
import storage


def validate_isbn(isbn):
    """
    Validates ISBN-13 and ISBN-10 following ISO 2108.
    No further action if isbn is valid
    """
    used_nums = 0
    if len(isbn) == 10:
        sum = 0
        for num in range(1,10):
            sum += int(isbn[num-1])*num
        if sum % 11 == 0 and isbn[-1].lower == 'x' or sum % 11 == int(isbn[-1]):
            return None
        return f"ISBN-10 with wrong checksum. Maybe transposed digits?"
    elif len(isbn) == 13:
        print(isbn)
        sum = 0
        for even in range(1, 12, 2):
            sum += int(isbn[even]) * 3
        for odd in range(0, 12, 2):
            sum += int(isbn[odd])


        if 10-(sum%10) == int(isbn[-1]):
            return None

        return "ISBN-13 with invalid checksum. Maybe transposed digits?"
    return f"Invalid ISBN with {len(isbn)} ciphers. Use 10 or 13 digits."


def jsonify_query_results(book_collection):
    """
    Converts result sets of database queries to json
    and refreshes the cache data, both actions to enable carousel reactions"""
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
            } for book in book_collection
    ])
    #Update cache for carousel reaction
    message = storage.cache_data(books) #debug
    return books


def jsonify_authors(collection):
    """converts result sets of database queries to json
    to enable carousel reactions. Additionally are portraits
     created if not already present"""
    authors = jsonify([
            {
                "id": author.id,
                "name": author.name,
                "birth_date": author.birth_date,
                "date_of_death": author.date_of_death

            } for author in collection
        ])
    return authors


def backup_database(filepath):
    """function to create a copy of the database file
    using shutil. As no data operations are made,
    this function is categorized as utility.
    return:
    """
    try:
        destination = filepath[:-2]+'sik'
        shutil.copyfile(filepath, destination)
        return "Database saved"
    except Exception as e:
        return f"Backup failed due to exception {e}."



def main():
    pass


if __name__ == "__main__":
    main()
