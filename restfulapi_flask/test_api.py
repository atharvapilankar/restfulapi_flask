import unittest
import json
from flask import Flask
from app import app, db, Book

class APITestCase(unittest.TestCase):
    def setUp(self):
        # Set up a test Flask app
        self.app = app.test_client()

        # Use the existing SQLAlchemy instance from the app module
        self.db = db
        self.db.create_all()

        # Create a test JWT token
        self.token = self.get_token() 

    def tearDown(self):
        with app.app_context():
            self.db.session.remove()
            self.db.drop_all()

    def get_token(self):
        # Helper function to get a test JWT token
        response = self.app.post('/login', json={'username': 'admin', 'password': 'admin_password'})
        data = json.loads(response.data.decode('utf-8'))
        return data['access_token']

    def test_add_book(self):
        # Test adding a new book
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1234567890',
            'price': 19.99,
            'quantity': 100
        }

        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.post('/books', json=data, headers=headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.data), {'message': 'Book added successfully'})

    def test_get_all_books(self):
        # Test retrieving all books
        response = self.app.get('/books')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {'books': []})  # Assuming no books initially

    def test_get_book_by_isbn(self):
        # Test retrieving a specific book by ISBN
        book = Book(title='Test Book', author='Test Author', isbn='1234567890', price=19.99, quantity=100)
        with app.app_context():
            db.session.add(book)
            db.session.commit()

        response = self.app.get('/books/1234567890')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['book']['title'], 'Test Book')

    def test_update_book(self):
        # Test updating book details
        book = Book(title='Test Book', author='Test Author', isbn='1234567890', price=19.99, quantity=100)
        with app.app_context():
            db.session.add(book)
            db.session.commit()

        updated_data = {
            'title': 'Updated Test Book',
            'author': 'Updated Test Author',
            'price': 29.99,
            'quantity': 50
        }

        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.put('/books/1234567890', json=updated_data, headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {'message': 'Book updated successfully'})

    def test_delete_book(self):
        # Test deleting a book
        book = Book(title='Test Book', author='Test Author', isbn='1234567890', price=19.99, quantity=100)
        with app.app_context():
            db.session.add(book)
            db.session.commit()

        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.app.delete('/books/1234567890', headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {'message': 'Book deleted successfully'})

if __name__ == "__main__":
    with app.app_context():
        unittest.main()
