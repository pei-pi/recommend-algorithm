from database import connect_database, execute_query
from processtext import preprocess_text
from gensim.models import Word2Vec

def main():
    # 连接数据库
    connection = connect_database()
    query = "select id,bookContent,bookTags,bookTitle,bookDetailedCategory from books"
    result = execute_query(connection, query)
    books = []
    for book_info in result:
        book_id = book_info['id']
        book_content = book_info['bookContent']
        book_tags = book_info['bookTags']
        book_title = book_info['bookTitle']
        book_category = book_info['bookDetailedCategory']

        # 创建一个包含图书信息的字典，并添加到books列表中
        book_info = {
            "id": str(book_id),
            "title": book_title,
            "content": book_content,
            "tag": book_tags,
            "category": book_category
        }
        books.append(book_info)
    # 关闭数据库连接
    connection.close()
    trainModel(books)

def trainModel(books):
    # 分别处理不同字段的文本
    contents = [preprocess_text(book_info['content'], "", "", "") for book_info in books]
    tags = [preprocess_text("", book_info['tag'], "", "") for book_info in books]
    titles = [preprocess_text("", "", book_info['title'], "") for book_info in books]
    categories = [preprocess_text("", "", "", book_info['category']) for book_info in books]

    # 训练不同的Word2Vec模型
    content_model = Word2Vec(sentences=contents, vector_size=100, window=10, min_count=7, workers=12)
    tag_model = Word2Vec(sentences=tags, vector_size=100, window=10, min_count=5, workers=12)
    title_model = Word2Vec(sentences=titles, vector_size=100, window=10, min_count=2, workers=12)
    category_model = Word2Vec(sentences=categories, vector_size=100, window=10, min_count=5, workers=12)

    # 保存模型
    content_model.save("../model/word2vec_content_model.bin")
    tag_model.save("../model/word2vec_tag_model.bin")
    title_model.save("../model/word2vec_title_model.bin")
    category_model.save("../model/word2vec_category_model.bin")

if __name__ == "__main__":
    main()
