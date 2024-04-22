from flask import Flask
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import the CORS module
import markdown
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
    #markdown格式转化成html
    # markdown_table =get_response(data['message'])
    # html_table = markdown.markdown(markdown_table, extensions=['tables'])
    
    # return jsonify(response)
    # return jsonify({'html_table': html_table})
    return jsonify(response)

@app.route('/api/clear', methods=['GET'])
def clear_history():
    clear_message()
    return jsonify({'message': 'History cleared'})
# @app.route('/markdown-to-table', methods=['GET'])
# def markdown_to_table():
#     # 这里假设你已经有了markdown格式的表格数据，假设为markdown_text
#     data = request.get_json()
#     markdown_text =get_response(data['message'])

#     # 将markdown转换为HTML
#     html_table = markdown2.markdown(markdown_text)

#     # 返回HTML形式的表格数据给前端页面
#     return jsonify({'html_table': html_table})


if __name__ == '__main__':
    app.run()