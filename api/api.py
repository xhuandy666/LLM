from flask import Flask
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import the CORS module
import markdown
from ESpeed import *
from Optimize import *

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


@app.route('/api/optimize', methods=['POST'])
def post_optimize():
    data = request.get_json()

    response = get_reply(data['message'])

    return jsonify(response)


@app.route('/api/data', methods=['POST'])
def post_data():

    data = request.get_json()

    response = get_response(data['message'],data['model'])

  
    return jsonify(response)

@app.route('/api/clear', methods=['GET'])
def clear_history():
    clear_message()
    return jsonify({'message': 'History cleared'})
@app.route('/markdown-to-table', methods=['GET'])
def markdown_to_table():
  
    data = request.get_json()
    markdown_text =get_response(data['message'])

    # 将markdown转换为HTML
    html_table = markdown2.markdown(markdown_text)

    # 返回HTML形式的表格数据给前端页面
    return jsonify({'html_table': html_table})


if __name__ == '__main__':
    app.run()