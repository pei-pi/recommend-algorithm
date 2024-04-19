from flask import Flask, request, jsonify
from flask_cors import CORS
from src.similarBook import calculate_similarity_book
from src.guessLike import calculate_user_like_book

app = Flask(__name__)
CORS(app)

@app.route('/calculate-similarity', methods=['POST'])
def calculate_similarity_endpoint():
    if request.is_json:
        data = request.json
        selected_book_id = data.get('book_id')
        if selected_book_id:
            similar_books =  calculate_similarity_book(selected_book_id)
            return jsonify(similar_books)
        else:
            return jsonify({'error': '未提供图书ID'})
    else:
        return jsonify({'error': '请求内容类型不是JSON'})

@app.route('/guess-like',methods=['POST'])
def calculate_user_like_book_endpoint():
    if request.is_json:
        data = request.json
        userId = data.get('userId')
        print(data)
        if userId:
            books = calculate_user_like_book(userId)
            print(books)
            return jsonify(books)
        else:
            return jsonify({'error': '未提供用户ID'})
    else:
        return jsonify({'error': '请求内容类型不是JSON'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)