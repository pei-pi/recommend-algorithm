import numpy as np
from utils.database import connect_database, execute_query
from gensim.models import Word2Vec
from scipy.spatial.distance import cosine

def calculate_similarity_book(selected_book_id):
    # 连接数据库
    connection = connect_database()
    query = "select id,bookContent,bookTags,bookTitle,bookDetailCategory,bookSrc,bookAuthor from books"
    result = execute_query(connection, query)
    # 存储所有图书
    books = []
    for book_info in result:
        book_id = book_info['id']
        book_content = book_info['bookContent']
        book_tags = book_info['bookTags']
        book_title = book_info['bookTitle']
        book_category = book_info['bookDetailCategory']
        book_src = book_info['bookSrc']
        book_author = book_info['bookAuthor']

        # 创建一个包含图书信息的字典，并添加到books列表中
        book_info = {
            "id": str(book_id),
            "title": book_title,
            "content": book_content,
            "tag": book_tags,
            "category": book_category,
            "bookSrc":book_src,
            "bookAuthor":book_author
        }
        books.append(book_info)
    # 关闭数据库连接
    connection.close()

    selected_book_id = selected_book_id

    # 加载模型
    content_model = Word2Vec.load("model/word2vec_content_model.bin")
    tag_model = Word2Vec.load("model/word2vec_tag_model.bin")
    title_model = Word2Vec.load("model/word2vec_title_model.bin")
    category_model = Word2Vec.load("model/word2vec_category_model.bin")

    # 获取文本的表示
    def get_text_representation(content, tag, title, category, tag_weight=3.0, category_weight=2):
        content_vector = get_weighted_vector(content_model, content)
        tag_vector = get_weighted_vector(tag_model, tag)
        title_vector = get_weighted_vector(title_model, title)
        category_vector = get_weighted_vector(category_model, category)

        # 加权处理书本标签的词向量
        tag_vector_weighted = tag_vector * tag_weight
        category_vector_weighted = category_vector * category_weight
        # 合并词向量
        text_representation = np.concatenate(
            [content_vector, tag_vector_weighted, title_vector, category_vector_weighted])

        return text_representation

    def get_weighted_vector(model, words):
        word_vectors = [model.wv[word] for word in words if word in model.wv]
        if word_vectors:
            weighted_vector = np.average(word_vectors, axis=0)
        else:
            weighted_vector = np.zeros(model.vector_size)
        return weighted_vector

    def calculate_similarity(book1, book2):
        text_vector1 = get_text_representation(book1['content'], book1['tag'], book1['title'], book1['category'])
        text_vector2 = get_text_representation(book2['content'], book2['tag'], book2['title'], book2['category'])

        return 1 - cosine(text_vector1, text_vector2)

    # 根据用户选择的图书ID找到对应的图书简介
    selected_book = next((book for book in books if book["id"] == selected_book_id), None)

    if selected_book:
        # 计算选择图书与其他图书的相似度，并排序得到相似度最高的topn本图书
        topn = 8
        similar_books = sorted(books, key=lambda book: calculate_similarity(selected_book, book), reverse=True)[:topn]
        return similar_books
    else:
        print("未找到选择的图书ID对应的图书信息")
