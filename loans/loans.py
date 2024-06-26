# loans.py
from flask import Flask, request, jsonify
import logging
from utils import *

app = Flask(__name__)

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/loans', methods=['POST'])
def create_loan():
    if request.content_type != 'application/json':
        return jsonify('error: Content-Type should be application/json'), 415
    
    data = request.json

    if not validate_loan_data(data):
        return jsonify({"error": "Invalid data"}), 422

    try:
        book_data = get_book_data(data["ISBN"])
        loan_data = create_loan_entry(data, book_data)
        
        if loan_data[0]:
            loanID = loan_data[1]["loanID"]
            
            return jsonify({"loan ID": loanID}), 201
        else:
            return jsonify({"error": loan_data[1]}), 400
        
    except Exception as e:
        return jsonify({f"Internal server error: {str(e)}"}), 500

@app.route('/loans', methods=['GET'])
def get_loans_route():
    query = request.args
    query_filter = {key: query[key] for key in query}
    
    try:
        loans = get_loans(query_filter)

        return jsonify(loans), 200
    except Exception as e:
        return jsonify({f"Internal server error: {str(e)}"}), 500

@app.route('/loans/<loanID>', methods=['GET'])
def get_loan(loanID):
    try:
        loan = get_loan_by_id(loanID)

        if loan:
            return jsonify(loan), 200
        else:
            return jsonify({"error": "Loan not found"}), 404
        
    except Exception as e:
        return jsonify({f"Internal server error: {str(e)}"}), 500

@app.route('/loans/<loanID>', methods=['DELETE'])
def delete_loan(loanID):
    try:
        result = delete_loan_by_id(loanID)
        
        if result.deleted_count > 0:
            return jsonify({"loan ID": loanID}), 200
        else:
            return jsonify({"error": "Loan not found"}), 404
        
    except Exception as e:
        return jsonify({f"Internal server error: {str(e)}"}), 500

@app.route('/loans/<loanID>/return', methods=['POST'])
def return_loan(loanID):
    try:
        loan = update_loan_return_date(loanID)
        
        if loan:
            return jsonify({"loan ID": loanID}), 201
        else:
            return jsonify({"error": "Loan not found"}), 404
        
    except Exception as e:
        return jsonify({f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
