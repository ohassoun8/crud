from flask import Flask, request, send_from_directory
from flask_restful import Api, Resource
import json

app = Flask(__name__)
api = Api(app)

books = []

# Book model
class Book:
    def __init__(self, id, book_name, author, publisher):
        self.id = id
        self.book_name = book_name
        self.author = author
        self.publisher = publisher

    def serialize(self):
        return {
            "id": self.id,
            "book_name": self.book_name,
            "author": self.author,
            "publisher": self.publisher
        }

# Get data from JSON file
def load_books_from_file():
    global books
    try:
        with open("books.json", "r") as file:
            initial_books = json.load(file)
            books = [Book(book["id"], book["book_name"], book["author"], book["publisher"]) for book in initial_books]
    except FileNotFoundError:
        print("No books.json file found. Starting with an empty list of books.")

# Save books
def save_books_to_file():
    with open("books.json", "w") as file:
        json.dump([book.serialize() for book in books], file, indent=4)

# Load books 
load_books_from_file()

# Managing books
class BookResource(Resource):
    # Get a single book by ID
    def get(self, book_id):
        book = next((book for book in books if book.id == book_id), None)
        if book:
            return book.serialize(), 200
        return {"message": "Book not found"}, 404

    # Create
    def post(self):
        data = request.get_json()
        new_book = Book(
            id=len(books) + 1,  # Auto-increment ID
            book_name=data["book_name"],
            author=data["author"],
            publisher=data["publisher"]
        )
        books.append(new_book)
        save_books_to_file()  # Save changes to the JSON file
        return new_book.serialize(), 201

    # Update
    def put(self, book_id):
        data = request.get_json()
        book = next((book for book in books if book.id == book_id), None)
        if book:
            book.book_name = data["book_name"]
            book.author = data["author"]
            book.publisher = data["publisher"]
            save_books_to_file()  # Save changes to the JSON file
            return book.serialize(), 200
        return {"message": "Book not found"}, 404

    # Delete
    def delete(self, book_id):
        global books
        books = [book for book in books if book.id != book_id]
        save_books_to_file()  # Save changes to the JSON file
        return {"message": "Book deleted"}, 200

# Listing all books
class BookListResource(Resource):
    def get(self):
        return [book.serialize() for book in books], 200

# Route for the root URL
@app.route("/")
def home():
    return {"message": "Welcome to the Book API! Use /books to list all books or /book/<id> to manage a specific book."}, 200

# Static JSON file
@app.route("/static/data")
def serve_json():
    return send_from_directory("static", "data.json")

# Insert resources to the API
api.add_resource(BookResource, "/book/<int:book_id>")
api.add_resource(BookListResource, "/books")

# Run the program
if __name__ == "__main__":
    app.run(debug=True)