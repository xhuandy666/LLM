from flask import Flask
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import the CORS module

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
    # Handle POST request from Vue frontend
    # Retrieve data from the request body
    data = request.get_json()
    # Process the data
    # ...
    # Return a response
    response = {'message': 'Data received'}
   
    return jsonify(data)

if __name__ == '__main__':
    app.run()