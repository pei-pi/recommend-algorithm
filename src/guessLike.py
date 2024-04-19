import gensim
import numpy as np
from utils.database import connect_database,guess_like_query,guess_like_borrow
from utils.processtext import preprocess_text
from gensim.models import Word2Vec

def calculate_user_like_book(userId):
    # 连接数据库
    connection = connect_database()
    query = "select activityType, bookContent,bookTags,bookTitle,bookDetailCategory,bookAuthor,bookSrc from books,useractivities where userId={userId} and books.id=useractivities.bookId"
    formatted_query = query.format(userId=userId)
    books = guess_like_borrow(connection,formatted_query)
    if books==[]:
        return []

    # 关闭数据库连接
    connection.close()

    borrowed_books = []  # 列表包含用户借阅的书的信息
    collected_books = []  # 列表包含用户收藏的书的信息
    for book in books:
        if(book['activity_type']==2):
            # 2收藏，3借阅
            collected_books.append(book)
        else:
            borrowed_books.append(book)

    # 加载Word2Vec模型
    word2vec_category_model = gensim.models.Word2Vec.load("model/word2vec_category_model.bin")
    word2vec_content_model = gensim.models.Word2Vec.load("model/word2vec_content_model.bin")
    word2vec_tag_model = gensim.models.Word2Vec.load("model/word2vec_tag_model.bin")
    word2vec_title_model = gensim.models.Word2Vec.load("model/word2vec_title_model.bin")

    def calculate_text_representation(book_list, weight,tag_vector_weight,category_vector_weight):
        representations = []  # 存储每本书的文本表示
        for book in book_list:
            contents = preprocess_text(book['content'], "", "", "")
            tags = preprocess_text("", book['tag'], "", "")
            titles = preprocess_text("", "", book['title'], "")
            categories = preprocess_text("", "", "", book['category'])

            # 计算每本书的文本表示
            content_vector = np.mean([word2vec_content_model.wv[word] for word in contents if word in word2vec_content_model.wv], axis=0)
            tag_vector = np.mean([word2vec_tag_model.wv[word] for word in tags if word in word2vec_tag_model.wv],axis=0)
            title_vector = np.mean([word2vec_title_model.wv[word] for word in titles if word in word2vec_title_model.wv], axis=0)
            category_vector = np.mean([word2vec_category_model.wv[word] for word in categories if word in word2vec_category_model.wv], axis=0)

            tag_vector = tag_vector * tag_vector_weight;
            category_vector = category_vector * category_vector_weight;

            # 合并词向量
            representation = np.concatenate([content_vector, tag_vector, title_vector, category_vector])
            representations.append(representation)

        # 计算用户的词向量表示，可以简单地取平均值或根据权重加权
        user_vector = np.mean(representations, axis=0)
        return user_vector

    def find_top_n_books(user_vector, all_books, n):
        # 计算用户向量与所有图书向量的相似度
        similarity_scores = []
        for book in all_books:
            book_vector = calculate_text_representation([book], 1.0,2,3)
            similarity_score = np.dot(user_vector, book_vector) / (np.linalg.norm(user_vector) * np.linalg.norm(book_vector))
            similarity_scores.append((book, similarity_score))

        # 按照相似度从高到低对图书进行排序
        sorted_books = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

        # 提取用户最喜欢的Top N本书
        top_n_books = [book for book, _ in sorted_books[:n]]

        return top_n_books



    # 设置权重
    borrowed_books_weight = 2.0  # 借阅的书权重
    collected_books_weight = 1.0  # 点击的书权重

    # 计算用户的词向量表示
    borrowed_books_representation = calculate_text_representation(borrowed_books, borrowed_books_weight,2,3)
    clicked_books_representation = calculate_text_representation(collected_books, collected_books_weight,2,3)

    # 最终用户的词向量表示
    user_vector = borrowed_books_representation + clicked_books_representation

    # 连接数据库
    connection = connect_database()
    query = "select id,bookContent,bookTags,bookTitle,bookDetailCategory,bookSrc,bookAuthor from books"
    all_books = guess_like_query(connection,query)
    # 关闭数据库连接
    connection.close()

    # 找到用户最喜欢的Top N本书
    top_n_books = find_top_n_books(user_vector, all_books, n=10)  # 假设找到Top 10本书

    return(top_n_books)

