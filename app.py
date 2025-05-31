from http.cookiejar import is_HDN

from flask import Flask,render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, or_
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from data_models import db, Author, Book
import os



#store absolute path to database file
storage_path = f"""{os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                  'data', 'library.db'))}"""

# Hint for the function of the 'delete Book'  image switch
DEL_MSG="To delete this book (ISBN visible below), use 'Delete Book' button"

#create Flask instance
app = Flask(__name__)
#configure database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{storage_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/')
def home():
    """ Route to home page. """
    books = db.session.query(Book).join(Author).all()
    return render_template('home.html', books=books, message=DEL_MSG)



@app.route('/api/books')
def get_books():
    """Retrieves all books from the database.
    Used in js. to fetch all books.
    """

    books = db.session.query(Book).join(Author).all()
    return jsonify([
        {
            "id": book.id,
            "title": book.title,
            "author": book.author.name,
            "publication_year": book.publication_year,
            "isbn": book.isbn,
            "img": f"static/images/{book.isbn}.png",
            "face": f"static/images/Portraits/{book.author_id}.png"
        } for book in books
    ])




@app.route('/add_author', methods=['GET','POST'])
def add_author():
    """
        Route for adding authors.
        :parameter name: String containing complete full name w/o quotes
        :parameter birth_date: birth date as date.

        :parameter date_of_death: If author has already passed away,
                                  the date of the author´s death as date or NULL

        :return: after adding to db a success message returns.
        """
    if request.method == 'GET':
        return render_template('add_author.html')

    elif request.method == 'POST':
        # Handle the POST request
        name = request.form.get('name')
        birth_date = convert_date_string(request.form.get('birth_date'))
        date_of_death = convert_date_string(request.form.get('date_of_death'))
        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        try:
            db.session.add(author)
            db.session.commit()
            return render_template('add_author.html', message=f"{author.name}, born {birth_date}, successfully added to authors.")
        except Exception as e:
            db.session.rollback()
            return render_template('add_author.html', message=f"Error: Exception {e} occured. Rollback initiated.")


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Route for adding books. Currently the manual addition of single items
    is working, bulk import of pasted csv worked once, will be reimplemented next
    :parameter title: String containing complete title w/o quotes
    :parameter ISBN: String of numbers, 13 digits, no quotes. No numerics because
                     ISBN10 sometimes end with an 'x'.
    :parameter author: Full name of author w/o quotes
    :parameter publication_year: 4 digit number
    :return: after retrieving the author_id the record is added to db and a success message returns.
    """
    if request.method == 'GET':
        return render_template('add_book.html')
    elif request.method == 'POST':
        # Handle the POST request

        title = request.form.get('title')
        authorname = request.form.get('author')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')

        author = db.session.query(Author).filter(Author.name == authorname).one()
        book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author.id)

        try:
            db.session.add(book)
            db.session.commit()
            return redirect(url_for('add_book'))

        except Exception as e:
            db.session.rollback()
            return render_template('add_book.html', message=f"Error: Exception {e} occured. Rollback initiated.")
    return render_template('add_book.html',
                           message=f"{book.title}, ISBN {book.isbn} from {authorname} successfully added to books.")


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
    if request.method == 'POST':
        if request.form.get('title'):
            order_item = getattr(Book, 'title', None)
        elif request.form.get('author'):
            order_item = getattr(Author, 'name', None)
        elif request.form.get('publication_year'):
            order_item = getattr(Book, 'publication_year', None)
            if request.form.get('desc'):
                sorted_books = db.session.query(Book.id, Book.author_id, Book.title,Book.isbn,
                                 Book.publication_year,Author.name).join(Author, \
                                 Book.author_id == Author.id) \
                                 .order_by(desc(order_item)).all()
            else:
                sorted_books = db.session.query(Book.id, Book.author_id, Book.title,Book.isbn,
                                 Book.publication_year,Author.name).join(Author, \
                                 Book.author_id == Author.id) \
                                 .order_by(order_item).all()

    return jsonify([
           {
                "id": book.id,
                "title": book.title,
                "author": book.author_id,
                "publication_year": book.publication_year,
                "isbn": book.isbn,
                "img": f"static/images/{book.isbn}.png",
                "face": f"static/images/Portraits/{book.author_id}.png"
           } for book in sorted_books
    ])


@app.route('/edit', methods=('GET','PUT'))
def edit_book(id):
    """This function should enable record editing
    by simply changing the details on the right side
    and clicking "Edit" button. Work still in progress
    due to write protected fields there
    """
    book = Book.query.get_or_404(id)

    if request.method == 'PUT':
        title = request.form['title']
        writer = request.form['author']
        isbn = request.form['isbn']
        year = int(request.form['publication_year'])

        author = Author.query.get_or_404(writer)
        book.title = title
        book.author_id = author.id
        book.isbn = isbn
        book.publication_year = year

        try:
            db.session.add(book)
            db.session.commit()
            return render_template('add_book.html',
                                   message=f"{book.title} from {author.name} succesfully changed.")
        except Exception as e:
            db.session.rollback()
            return render_template('add_book.html', message=f"Error accessing database. Details: {e}")
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
            db.session.delete(book)
            db.session.commit()
            return render_template('home.html', message=f"Deleted Book: {title}")
        except Exception as e:
            return render_template('home.html', message=f"Error deleting book {title}. Details. {e}")
    return render_template('home.html')


@app.route('/wildcard_search', methods=['GET','POST'])
def wildcard_search():
        """
        Route to search books with POST and any search term containing title, author or year
        :return: Query results as List of dictionaries
        """
        if request.method == 'POST':
            term = request.form.get('wildcard_search')
            if term:
                term = '%' + term + '%'
                books = db.session.query(Book).join(Author) \
                         .filter(or_(Book.title.contains(term), \
                                    Book.isbn.contains(term), \
                                    Book.publication_year.contains(term), \
                                    Author.name.contains(term))) \
                                    .all()

            return jsonify([
                {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author_id,
                    "publication_year": book.publication_year,
                    "isbn": book.isbn,
                    "img": f"static/images/{book.isbn}.png",
                    "face": f"static/images/Portraits/{book.author_id}.png"
                } for book in books
            ])
        return redirect(url_for('home'))



def convert_date_string(datestring):
    """
    Converts the date, which are submitted by add_author,
    into german style date-strings. Only for my convenience.
    :returns: German style datestring, type String
              e.g: 01.01.2010 instead of 2010-01-01
     """
    return datestring[-2:] + '.' + datestring[-5:-3] + '.' + datestring[:4]


if __name__ == "__main__":
    """Initialization of backend service"""
    db.init_app(app)
    #with app.app_context():
    # db.create_all()
    app.run(host="127.0.0.1", port=5000, debug=True)
