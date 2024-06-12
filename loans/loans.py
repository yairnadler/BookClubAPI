# loans.py
from flask import Flask, request, jsonify
import logging
from utils import *

app = Flask(__name__)

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/loans', methods=['POST'])
def create_loan():
    data = request.json

    # Validate the incoming data
    if not validate_loan_data(data):
        return jsonify({"error": "Invalid data"}), 422

    try:
        # Create the loan entry
        loan_data = create_loan_entry(data)
        if loan_data[0]:
            return jsonify(loan_data[1]), 201
        else:
            return jsonify({"error": loan_data[1]}), 400
    except Exception as e:
        return jsonify({f"Error occurred: {str(e)}"}), 500

@app.route('/loans', methods=['GET'])
def get_loans_route():
    query = request.args
    query_filter = {key: query[key] for key in query}
    try:
        loans = get_loans(query_filter)
        app.logger.debug(f"Loans retrieved: {loans}")
        return jsonify(loans), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/loans/<loanID>', methods=['GET'])
def get_loan(loanID):
    try:
        loan = get_loan_by_id(loanID)
        app.logger.debug(f"Loan retrieved: {loan}")
        if loan:
            return jsonify(loan), 200
        else:
            return jsonify({"error": "Loan not found"}), 404
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/loans/<loanID>', methods=['DELETE'])
def delete_loan(loanID):
    try:
        result = delete_loan_by_id(loanID)
        if result.deleted_count > 0:
            return jsonify({"loanID": loanID}), 200
        else:
            return jsonify({"error": "Loan not found"}), 404
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/loans/<loanID>/return', methods=['POST'])
def return_loan(loanID):
    try:
        loan = update_loan_return_date(loanID)
        if loan:
            return jsonify(loan), 200
        else:
            return jsonify({"error": "Loan not found"}), 404
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)