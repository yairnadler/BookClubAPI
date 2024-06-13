# books.py
import json
from flask import Flask, request, jsonify
import logging
from utils import *
from bson import json_util

app = Flask(__name__)

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/books', methods=['POST'])
def create_book():
    data = request.json

    # Validate the incoming data
    valid, error = validate_book_data(data)
    if not valid:
        return jsonify({"error": error}), 422

    # Check if the book already exists
    if get_books({"ISBN": data["ISBN"]}):
        return jsonify({"error": "Book with this ISBN already exists"}), 422

    try:
        # Create the book entry
        book_data = create_book_entry(data)
        app.logger.debug(f"Book created: {book_data}")

        # Create the corresponding rating entry
        create_rating_entry(book_data["id"])
    
        return jsonify(book_data), 201
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/books', methods=['GET'])
def get_books_route():
    query = request.args
    query_filter = {key: query[key] for key in query}
    try:
        books = get_books(query_filter)
        app.logger.debug(f"Books retrieved: {books}")
        return jsonify(books), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/books/<bookID>', methods=['GET'])
def get_book(bookID):
    try:
        book = get_book_by_id(bookID)
        app.logger.debug(f"Book retrieved: {book}")
        if book:
            return jsonify(book), 200
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/books/<bookID>', methods=['DELETE'])
def delete_book(bookID):
    try:
        delete_book_by_id(bookID)
        
        return jsonify({"id": bookID}), 200
    
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/books/<bookID>', methods=['PUT'])
def update_book(bookID):
    data = request.json

    # Validate the incoming data
    valid, error = validate_book_put_request_data(data)
    if not valid:
        return jsonify({"error": error}), 422

    try:
        # Update the book entry
        book = update_book_entry(bookID, data)
        app.logger.debug(f"Book updated: {book}")

        if book:
            return jsonify(book['id']), 200
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/ratings', methods=['GET'])
def get_ratings_route():
    try:
        ratings = get_ratings()
        app.logger.debug(f"Ratings retrieved: {ratings}")
        return jsonify(ratings), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/ratings/<bookID>/values', methods=['POST'])
def rate_book(bookID):
    data = request.json
    rating = data.get("value")
    
    if rating is None or not (1 <= rating <= 5):
        return jsonify({"error": "Invalid rating. It must be an integer between 1 and 5"}), 422

    try:
        average_rating = add_rating(bookID, rating)
        if average_rating is None:
            return jsonify({"error": "Book not found"}), 404

        return jsonify({"new_average": average_rating}), 201
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/ratings/<bookID>', methods=['GET'])
def get_book_ratings(bookID):
    try:
        ratings = get_ratings_by_book_id(bookID)
        app.logger.debug(f"Ratings retrieved: {ratings}")
        if ratings:
            return jsonify(ratings), 200
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/top', methods=['GET'])
def get_top_books_route():
    try:
        top_books = get_top_books()
        app.logger.debug(f"Top books retrieved: {top_books}")
        return jsonify(top_books), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
