from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, Book

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'wow'  

db.init_app(app)
jwt = JWTManager(app)

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "admin" or password != "admin_password":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Create a new book
@app.route('/books', methods=['POST'])
@jwt_required()  # Requires a valid JWT token
def add_book():
    data = request.get_json()
    new_book = Book(**data)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully'}), 201

# Retrieve all books
@app.route('/books', methods=['GET'])
def get_all_books():
    books = Book.query.all()
    return jsonify({'books': [{'title': book.title, 'author': book.author, 'isbn': book.isbn, 'price': book.price, 'quantity': book.quantity} for book in books]})

# Retrieve a specific book by ISBN
@app.route('/books/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        return jsonify({'book': {'title': book.title, 'author': book.author, 'isbn': book.isbn, 'price': book.price, 'quantity': book.quantity}})
    else:
        return jsonify({'message': 'Book not found'}), 404

# Update book details
@app.route('/books/<isbn>', methods=['PUT'])
@jwt_required()  # Requires a valid JWT token
def update_book(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        data = request.get_json()
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.price = data.get('price', book.price)
        book.quantity = data.get('quantity', book.quantity)
        db.session.commit()
        return jsonify({'message': 'Book updated successfully'})
    else:
        return jsonify({'message': 'Book not found'}), 404

# Delete a book
@app.route('/books/<isbn>', methods=['DELETE'])
@jwt_required()  # Requires a valid JWT token
def delete_book(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted successfully'})
    else:
        return jsonify({'message': 'Book not found'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
