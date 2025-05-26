from flask import Flask,render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload

from data_models import db, Author, Book
import os
import handle_csv

storage_path = f"""{os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 'data', 'library.db'))}"""


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{storage_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/books')
def get_books():
    books = db.session.query(Book).join(Author).all()
    return jsonify([
        {
            "title": book.title,
            "author": book.author.name,
            "publication_year": book.publication_year,
            "isbn": book.isbn,
            "img": f"static/images/{book.id}.png"
        } for book in books
    ])



@app.route('/add_author', methods=['GET', 'POST'])
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


@app.route('/sort',methods=['POST'])
def sort():
    books = db.session.query(Book).join(Author).all()
    pass


@app.route('/delete_book')
def delete_book():
    pass


@app.route('/add_bulk', methods=['POST'])
def bulk_add_books():
    booklist = request.form.get('booklist')
    return booklist



def convert_date_string(datestring):
    return datestring[-2:] + '.' + datestring[-5:-3] + '.' + datestring[:4]


if __name__ == "__main__":
    db.init_app(app)
    #with app.app_context():
    # db.create_all()
    app.run(host="127.0.0.1", port=5000, debug=True)
