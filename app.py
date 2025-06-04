from flask import Flask,render_template, request, jsonify, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, or_
from data_models import db, Author, Book
from os import path
import config
import utilities
import storage
import json, csv

#store absolute path to database file
DB_PATH=path.abspath(path.join(path.dirname(__file__),path.join('data','library.db')))


#create Flask instance
app = Flask(__name__)
#configure flask_SQLAlchemy
app.config.from_object('config.DevConfig')


@app.route('/', methods=['GET'])
def home():
    """ Route to home page. """
    #check for an existing cache
    books = storage.load_cache()
    if isinstance(books, str):
        books = db.session.query(Book).join(Author).all()
    return render_template("home.html", books=books)


@app.route('/api/books',methods=['GET', 'POST'])
def get_books():
    """
    Retrieves cached books from file. Is the access route
    for the js fetch api. This step is necessary to
    change the wheel contents matching the cursor.
    """
    books = storage.load_cache()
    if isinstance(books, str):
        collection = db.session.query(Book).join(Author).all()
        books = utilities.jsonify_query_results(collection)
    return books


@app.route('/add_author', methods=['GET','POST'])
def add_author():
    """
    Route for adding authors.
    :parameter name: String containing complete full name w/o quotes
    :parameter birth_date: birthdate as date.
    :parameter date_of_death: If author has already passed away,
               the date of the author´s death as date or NULL
    :return: after adding to db a success message returns.
    """
    if request.method == 'GET':
        return render_template('add_author.html')

    # Handle the POST request
    name = request.form.get('name')
    birth_date = request.form.get('birth_date')
    date_of_death = request.form.get('date_of_death')
    author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
    txlog = storage.add_author_to_db(author)
    return render_template('add_author.html', message=txlog)


@app.route('/add_book', methods=['GET','POST'])
def add_book():
    """
    Route for manual adding single books.
    :parameter title: String containing complete title w/o quotes
    :parameter ISBN: String of numbers, 10 or 13 digits, no quotes. No numerics because
                     ISBN10 sometimes end with an 'x'.
    :parameter author: Full name of author w/o quotes
    :parameter publication_year: 4-digit-number
    :return: after retrieving the author_id the record is added to db and a success message returns.
    """
    if request.method == 'GET':
        return render_template('add_book.html')

    # Handle the POST request
    title = request.form.get('title')
    author_name = request.form.get('author_name')
    isbn = request.form.get('isbn')
    publication_year = request.form.get('publication_year')
    print(title, author_name, isbn)
    author = db.session.query(Author.id).filter(Author.name == author_name).one()
    author_id = author[0]
    if not author_id:
        return render_template('add_book.html', message=f"unknown author {author_name}.")
    book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id)
    txlog = storage.add_book_to_db(book)
    return render_template('add_book.html', message=txlog)


@app.route('/add_bulk', methods=['POST'])
def add_bulk():
    """
    Route for bulk insertion of books.
    :parameter pasted csv: csv, pasted into the textarea. No headers, no quotes!
    :parameter file upload: upload a csv file to server.
    """
    # Handle the POST request
    book_data = []
    booklist = request.form.get('booklist')
    file = request.form.get('file')
    if booklist:
        with open('input.csv', 'w') as textfile:
            for book in booklist.split('\n'):
                textfile.writelines(book)
        with open('input.csv', 'r') as csvfile:
            data=list(csv.DictReader(csvfile))
    elif file:
        with open(file, 'r') as csvfile:
            data=list(csv.DictReader(csvfile))

    with open('output.json', 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    with open('output.json','r') as jsonfile:
        data = json.load(jsonfile)
    txlog = storage.bulk_insert_bookshelf(data)
    return render_template('add_book.html', message=txlog)


@app.route('/sort', methods=['GET','POST'])
def get_sorted_books():
    """
    Sorting books following the switches in the upper center.
    Currently only one sort-column and the sort-direction are usable.
    Combined sorting still in progress
    :parameter: 3 radio buttons indicating the sort-column and
                1 switch for descending order or not.
    :return: Sorted books, visible by repositioning of the books
             on the wheel
    """
    order_item = 'id'
    if request.form.get('title'):
        order_item = getattr(Book, 'title', None)
    elif request.form.get('author'):
        order_item = getattr(Author, 'name', None)
    elif request.form.get('publication_year'):
        order_item = getattr(Book, 'publication_year', None)
        if request.form.get('desc'):
            sorted_books = db.session.query(Book).join(Author) \
                             .order_by(desc(order_item)) \
                             .all()
        else:
            sorted_books = db.session.query(Book).join(Author) \
                                                 .order_by(order_item) \
                                                 .all()
        if sorted_books:
            books = utilities.jsonify_query_results(sorted_books)
            return books


@app.route('/edit', methods=['POST'])
def edit_book():
    """
    Record editing function. As long as the mouse is hovering over the left
    upper sidebar the attributes visible are editable except the ISBN. As it is
    wordwide unique, editing would be counterproductive.
    Since there is no cache refresh, a search is necessary to view the change
    """
    isbn = request.form.get('isbn')
    title = request.form.get('title')
    writer = request.form.get('author')
    year = request.form.get('year')
    item = db.session.query(Author.id).filter(Author.name == writer).one()
    book = db.session.query(Book).filter(Book.isbn == isbn).one()
    book.title = title
    book.author_id = item[0]
    book.publication_year = year
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete', methods=['POST'])
def delete_book_in_view():
    """
    Route to delete the book which is currently in focus, meaning:
    that book visible in carousel center with displayed details on the right side.
    No warning, so confirmation. Just kill.
    Result is immediately visible: The book disappears from wheel.
    :return: Message indicating the deleted book´s title.
    """
    isbn = request.form.get('bookId')
    item = db.session.query(Book.id, Book.title).filter(Book.isbn == isbn).one()
    book_id = item[0]
    title = item[1]
    book = Book.query.get(book_id)
    if book:
        try:
            storage.remove_from_cache(book.id)
            db.session.delete(book)
            db.session.commit()
            return render_template('home.html', message=f"Deleted Book: {title}")
        except Exception as e:
            return render_template('home.html', message=f"Error deleting book {title}. Details. {e}")
    return redirect(url_for('home.html'))


@app.route('/search')
def search():
    """Query over all database tables
    under consideration of the url search specs listed below.
    The search is sensitive but finds fragments.
    :parameter: title (usage: url/?title=<search term>)
                      query books table for title-fragments
    :parameter: author (usage: url/?author=<search term>)
                      query authors table for author-name drags
                      afterward query books for books from this author
    :parameter: year  a single 4-letter expression delivers the books of this year
                      two years,separated by a hyphen retrieves the tme span between
    :return: redirection to homepage
    """
    query = {'title': None, 'isbn': None, 'authorname': None, 'year': None}
    query['title'] = request.args.get('title')
    query['isbn'] = request.args.get('isbn')
    query['authorname'] = request.args.get('author')
    query['year'] = request.args.get('publication_year')

    collection = storage.query_database(query)
    print(collection)
    if not isinstance(collection, str):
        storage.cache_data(collection)
    return redirect(url_for('home'))


@app.route('/wildcard', methods=['POST'])
def create_query_from_wildcard():
    """
    This function receives a submitted search term (POSTed),
    and queries every column for this term.
    Submitting an empty input field gains all records.
    :return: redirection to homepage
    """
    term = request.form.get('wildcard_term')
    print(f"from wildcard: {term}")
    collection = storage.query_for_keyword(term)
    if not isinstance(collection, str):
        storage.cache_data(collection)
    return redirect(url_for('home'))


@app.route('/backup')
def backup():
    """This function is triggered to copy the database file into a backup.
    Uses shutil.copyfile().
    """
    message = utilities.backup_database(DB_PATH)
    return redirect(url_for('home'))


if __name__ == "__main__":
    """Check for database file and initialization of backend service"""
    if DB_PATH:
        db.init_app(app)
        #with app.app_context():
        # db.create_all()
        app.run(host="127.0.0.1", port=5002, debug=True)
    else:
        print("No database accessible. Aborting.")
