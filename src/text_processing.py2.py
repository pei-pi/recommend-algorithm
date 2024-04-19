import numpy as np

from database import connect_database, execute_query,insert_data
from sklearn.feature_extraction.text import TfidfVectorizer
import jieba.analyse
import jieba
from gensim.models import Word2Vec
from gensim.utils import tokenize
from scipy.spatial.distance import cosine

def main():
    # 连接数据库
    connection = connect_database()
    query = "select id,bookContent,bookTags,bookTitle,bookDetailCategory from books"
    result = execute_query(connection,query)
    # 存储预处理后的文本数据
    preprocessed_texts = []
    #存储所有图书
    books = []
    for book_info in result:
        book_id = book_info['id']
        book_content = book_info['bookContent']
        book_tags = book_info['bookTags']
        book_title = book_info['bookTitle']
        book_category = book_info['bookDetailCategory']
        preprocessed_text = preprocess_text(book_content, book_tags, book_title ,book_category)
        preprocessed_texts.append(preprocessed_text)
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

    # 输出预处理后的文本数据
    # for idx, text in enumerate(preprocessed_texts, start=1):
    #     print(f"Preprocessed text for book {idx}: {text}")

    # 分割文本为单词列表
    corpus = [text.split() for text in preprocessed_texts]
    #
    # 训练Word2Vec模型
    # model = Word2Vec(sentences=corpus, vector_size=100, window=8, min_count=3, workers=10)
    # #
    # # 保存模型
    # model.save("word2vec_model.bin")
    #
    # # 加载模型
    model = Word2Vec.load("word2vec_model.bin")
    selected_book_id = "5905"

    def calculate_similarity(book1, book2):

        content1_tokens = preprocess_text(book1['content'], book1['tag'], book1['title'],book1['category'])
        word_vectors1 = [model.wv[word] for word in content1_tokens if word in model.wv]

        # 计算整个文本的词向量表示（这里采用平均值）
        if word_vectors1:
            text_vector1 = np.mean(word_vectors1, axis=0)
        else:
            text_vector1 = np.zeros(model.vector_size)

        content2_tokens = preprocess_text(book2['content'], book2['tag'], book2['title'],book2['category'])

        word_vectors2 = [model.wv[word] for word in content2_tokens if word in model.wv]

        # 计算整个文本的词向量表示（这里采用平均值）
        if word_vectors2:
            text_vector2 = np.mean(word_vectors2, axis=0)
        else:
            text_vector2 = np.zeros(model.vector_size)

        return 1 - cosine(text_vector1, text_vector2)

    # 根据用户选择的图书ID找到对应的图书简介
    selected_book = next((book for book in books if book["id"] == selected_book_id), None)


    if selected_book:
        # 计算选择图书与其他图书的相似度，并排序得到相似度最高的topn本图书
        topn = 10
        similar_books = sorted(books, key=lambda book: calculate_similarity(selected_book, book), reverse=True)[:topn]
        print(similar_books)

        # 输出相似度最高的topn本图书
        for idx, book in enumerate(similar_books, start=1):
            print(f"相似图书 {idx}: {book['title']}")
    else:
        print("未找到选择的图书ID对应的图书信息")
    # # 使用词向量
    # word_vector = model.wv['面纱']
    # print("Vector representation of '狂人':", word_vector)



def preprocess_text(text, tag, book_title, book_category):
    # 读取停用词
    stopwords = set()
    with open("../file/hit_stopwords.txt", 'r', encoding='utf-8') as file:
        for line in file:
            stopwords.add(line.strip())

    # 分词并去除停用词
    # words = list(str(id))
    # words.extend(list(jieba.cut(text)))
    words = list(jieba.cut(text + " " + tag + " " + book_title + " " + book_category))
    words = [word for word in words if word not in stopwords]

    # 返回预处理后的文本
    return ' '.join(words)



if __name__ == "__main__":
    main()
