from flask import Flask
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import the CORS module
from ESpeed import *

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for all routes

# Rest of your code...


@app.route('/')
def hello():
    return 'World!'

@app.route('/api/message', methods=['GET'])
def get_data():
    # Handle GET request from Vue frontend
    # Retrieve data from your data source
    data = request.get_json()
    
    return jsonify(data)

@app.route('/api/data', methods=['POST'])
def post_data():

    data = request.get_json()

    response = get_response(data['message'])

    # response = {'message': 'Data received'}
   
    return jsonify(response)

if __name__ == '__main__':
    app.run()