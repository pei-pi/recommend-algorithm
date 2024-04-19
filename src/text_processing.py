from database import connect_database, execute_query,insert_data
from sklearn.feature_extraction.text import TfidfVectorizer
import jieba.analyse
import jieba
from gensim.models import Word2Vec

def main():
    # 连接数据库
    connection = connect_database()
    query = "select bookContent,bookTags from books limit 10"
    result = execute_query(connection,query)
    book_tag = list()
    book=list()
    for i in result:
        book.append(i['bookContent'])
        book_tag.append(i['bookTags'])
    # 关闭数据库连接
    connection.close()

    preprocessed_texts = [preprocess_text(text,tag) for text,tag in zip(book,book_tag)]

    # 创建TF-IDF向量化器
    vectorizer = TfidfVectorizer()

    # 计算TF-IDF权重
    tfidf_matrix = vectorizer.fit_transform(preprocessed_texts)

    # 获取关键词
    feature_names = vectorizer.get_feature_names_out()
    top_keywords = []
    for doc in tfidf_matrix.toarray():
        sorted_indices = doc.argsort()[::-1]  # 获取按TF-IDF值降序排序的索引
        top_keywords.append([feature_names[idx] for idx in sorted_indices[:10]])  # 获取前5个关键词

    # 打印关键词
    for i, keywords in enumerate(top_keywords):
        print(f"Top keywords for document {i + 1}: {keywords}")

# 文本预处理函数
def preprocess_text(text,tag):

    stopwords = set()
    with open("../file/hit_stopwords.txt", 'r', encoding='utf-8') as file:
        for line in file:
            stopwords.add(line.strip())

    tag_Words = list(jieba.cut(tag))
    words = list(jieba.cut(text))
    words.extend(tag_Words)
    words = [word for word in words if word not in stopwords]
    print(' '.join(words))
    return ' '.join(words)   # 转换为字符串

if __name__ == "__main__":
    main()
