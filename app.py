from flask import Flask,render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from data_models import db, Author, Book
import os



#store absolute path to database file
storage_path = f"""{os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                  'data', 'library.db'))}"""

DEL_MSG="To delete this book (ISBN visible below), use 'Delete Book' button"

#create Flask instance
app = Flask(__name__)
#configure database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{storage_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Route to home page with POST to sort the books by title, author or year if switched.
    :return:
    """
    books = db.session.query(Book).join(Author).all()
    return render_template('home.html', books=books, message=DEL_MSG)

    if request.method == 'POST':
        sort_by = ''
        if request.form.get('sw_title'):
            sort_by = getattr(Book, 'title', None)
        elif request.form.get('sw_author'):
            sort_by = getattr(Author, 'name', None)
        elif request.form.get('sw_year'):
            sort_by = getattr(Book, 'publication_year', None)
        if request.form.get('desc'):
            books = db.session.query(Book.id, Book.author_id, Book.title,Book.isbn,
                                     Book.publication_year,Author.name).join(Author, \
                                     Book.author_id == Author.id) \
                                     .order_by(desc(sort_by)).all()
        else:
            books = db.session.query(Book.id, Book.author_id, Book.title,Book.isbn,
                                     Book.publication_year,Author.name).join(Author, \
                                     Book.author_id == Author.id) \
                                     .order_by(sort_by).all()

    books = jsonify([
        {
            "title": book.title,
            "author": book.author_id,
            "publication_year": book.publication_year,
            "isbn": book.isbn,
            "img": f"static/images/{book.isbn}.png",
            "face": f"static/images/Portraits/{book.author_id}.png"
        } for book in books
    ])
    return render_template('home.html', books=books, message=DEL_MSG)

@app.route('/api/books')
def get_books():
    """Retrieves all books from the database. Used in js
    to fetch all books."""
    books = db.session.query(Book).join(Author).all()
    return jsonify([
        {
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
            return render_template('add_book.html', message=f"{book.title}, ISBN {book.isbn} from {authorname} successfully added to books.")
        except Exception as e:
            db.session.rollback()
            return render_template('add_book.html', message=f"Error: Exception {e} occured. Rollback initiated.")


@app.route('/sort',methods=['GET','POST'])
def sort():
    if request.method == 'GET':
        books = db.session.query(Book).join(Author).all()
        return render_template('home.html', books=books, message=DEL_MSG)
    if request.form.get('sw_title'):
        sort_by = getattr(Book, 'title', None)
    elif request.form.get('sw_author'):
        sort_by = getattr(Author, 'name', None)
    elif request.form.get('sw_year'):
        sort_by = getattr(Book, 'publication_year', None)
    if request.form.get('desc'):
        books = db.session.query(Book.id, Book.author_id, Book.title,Book.isbn,
                                 Book.publication_year,Author.name).join(Author, \
                                 Book.author_id == Author.id) \
                                 .order_by(desc(sort_by)).all()
    else:
        books = db.session.query(Book.id, Book.author_id, Book.title,Book.isbn,
                                 Book.publication_year,Author.name).join(Author, \
                                 Book.author_id == Author.id) \
                                 .order_by(sort_by).all()

    books = jsonify([
        {
            "title": book.title,
            "author": book.author_id,
            "publication_year": book.publication_year,
            "isbn": book.isbn,
            "img": f"static/images/{book.isbn}.png",
            "face": f"static/images/Portraits/{book.author_id}.png"
        } for book in books
    ])
    return render_template('home.html', books=books, message=DEL_MSG)


@app.route('/delete', methods=['POST'])
def delete_book_in_view():
    isbn = request.form.get('bookId')
    item = db.session.query(Book.id, Book.title).filter(Book.isbn == isbn).one()
    book_id = item[0]
    title = item[1]
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
    return render_template('home.html', message=f"Deleted Book: {title}")


@app.route('/search', methods=['POST'])
def search():
    """
    Route to search books with POST and any search term containing title, author or year
    :return:
    """
    f_title=request.form.get('find_title')
    f_author=request.form.get('find_author')
    f_year=request.form.get('find_year')
    f_isbn=request.form.get('find_isbn')
    if f_author:
        author = db.session.query(Author).filter(Author.name.contains('f_author')) \
                                              .first()
        books = db.session.query(Book).filter(Book.author_id == author.id) \
                                              .all()
        if books:
            return render_template("home.html", books=books)

    elif f_title:
        books = db.session.query(Book).filter(Book.title.contains('%' + 'f_title' + '%')) \
                                              .all()
        if books:
            return render_template("home.html", books=books)
        elif f_year:
            range_chk = f_year.split('-')
            if range_chk[1]:
                books = db.session.query(Book).filter(Book.publication_year.between(range_chk[0], range_chk[1])) \
                                                     .all()
                if books:
                    return render_template("home.html", books=books)
            books = db.session.query(Book).filter(Book.publication_year == f_year).all()
            if books:
                return render_template("home.html", books=books)


def convert_date_string(datestring):
    return datestring[-2:] + '.' + datestring[-5:-3] + '.' + datestring[:4]


if __name__ == "__main__":
    db.init_app(app)
    #with app.app_context():
    # db.create_all()
    app.run(host="127.0.0.1", port=5000, debug=True)
