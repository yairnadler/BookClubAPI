# utils.py
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import logging

# MongoDB client setup
try:
    client = MongoClient('mongodb://mongo:27017/')
    db = client.library
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {str(e)}")
    raise

def validate_loan_data(data):
    required_fields = ['memberName', 'ISBN', 'loanDate']
    return all(field in data for field in required_fields)

def create_loan_entry(data):
    book = db.books.find_one({"ISBN": data["ISBN"]})
    if not book:
        return False, "Book not found"

    book_id = str(book["id"])

    # Check if the member has already loaned 2 books
    active_loans = db.loans.count_documents({"memberName": data["memberName"], "returnDate": None})
    if active_loans >= 2:
        return False, "Member has already loaned 2 books"

    loan_data = {
        "memberName": data["memberName"],
        "ISBN": data["ISBN"],
        "loanDate": data["loanDate"],
        "returnDate": None,
        "loanID": str(ObjectId()),
        "bookID": book_id
    }

    db_loan_data = loan_data.copy()
    db.loans.insert_one(db_loan_data)

    return True, loan_data

def get_loans(query_filter):
    loans = list(db.loans.find(query_filter, {'_id': False}))
    for loan in loans:
        loan['loanID'] = str(loan['loanID'])
        loan['bookID'] = str(loan['bookID'])
    return loans

def get_loan_by_id(loan_id):
    loan = db.loans.find_one({"loanID": loan_id}, {'_id': False})
    if loan:
        loan['loanID'] = str(loan['loanID'])
        loan['bookID'] = str(loan['bookID'])
    return loan

def delete_loan_by_id(loan_id):
    return db.loans.delete_one({"loanID": loan_id})

def get_loans_by_book_id(book_id):
    loans = list(db.loans.find({"bookID": book_id}, {'_id': False}))
    for loan in loans:
        loan['loanID'] = str(loan['loanID'])
        loan['bookID'] = str(loan['bookID'])
    return loans

def update_loan_return_date(loan_id):
    result = db.loans.update_one(
        {"loanID": loan_id},
        {"$set": {"returnDate": datetime.now().strftime("%Y-%m-%d")}}
    )
    if result.matched_count > 0:
        loan = db.loans.find_one({"loanID": loan_id}, {'_id': False})
        loan['loanID'] = str(loan['loanID'])
        loan['bookID'] = str(loan['bookID'])
        return loan
    return None
