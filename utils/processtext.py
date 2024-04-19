# 定义函数进行文本预处理和计算文本表示
import jieba


def preprocess_text(text, tag, title, category):
    # 读取停用词
    stopwords = set()
    with open("file/hit_stopwords.txt", 'r', encoding='utf-8') as file:
        for line in file:
            stopwords.add(line.strip())

    words = list(jieba.cut(text + " " + tag + " " + title + " " + category))
    words = [word for word in words if word not in stopwords]

    # 返回预处理后的文本
    return words