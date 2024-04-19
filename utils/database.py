import pymysql
from config import DB_HOST,DB_PORT,DB_NAME,DB_USER,DB_PASSWORD

def connect_database():
    # 连接数据库
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Database connected successfully!")
        return connection
    except pymysql.Error as e:
        print(f"Error connection to database:{e}")
        return None

def execute_query(connection,query):
    # 查询数据
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except pymysql.Error as e:
        print(f"Error executing query:{e}")
        return None

def insert_data(connection,table,data):
    # 插入数据
    try:
        with connection.cursor() as cursor:
            keys = ','.join(data.keys())
            values = ','.join(['%s']*len(data))
            query = f"INSERT INTO {table} ({keys}) VALUES ({values})"
            cursor.execute(query,tuple(data.values()))
            connection.commit()
            print("Data inserted successfully!")
    except pymysql.Error as e:
        print(f"Error inserting data:{e}")

# 猜你喜欢模块查询用户点击借阅书籍
def guess_like_borrow(connection,query):
    result = execute_query(connection, query)
    # 存储该用户历史借阅点击图书
    books = []
    for book_info in result:
        book_content = book_info['bookContent']
        book_tags = book_info['bookTags']
        book_title = book_info['bookTitle']
        book_category = book_info['bookDetailCategory']
        activity_type = book_info['activityType']
        book_author = book_info['bookAuthor']
        book_src = book_info['bookSrc']

        # 创建一个包含图书信息的字典，并添加到books列表中
        book_info = {
            "title": book_title,
            "content": book_content,
            "tag": book_tags,
            "category": book_category,
            "activity_type": activity_type,
            "author":book_author,
            "src":book_src
        }
        books.append(book_info)
    return books

# 猜你喜欢模块查询所有图书
def guess_like_query(connection,query):
    result = execute_query(connection, query)
    # 存储所有图书
    all_books = []
    for book_info in result:
        book_id = book_info['id']
        book_content = book_info['bookContent']
        book_tags = book_info['bookTags']
        book_title = book_info['bookTitle']
        book_category = book_info['bookDetailCategory']
        book_author = book_info['bookAuthor']
        book_src = book_info['bookSrc']


        # 创建一个包含图书信息的字典，并添加到books列表中
        book_info = {
            "id": str(book_id),
            "title": book_title,
            "content": book_content,
            "tag": book_tags,
            "category": book_category,
            "author": book_author,
            "src": book_src
        }
        all_books.append(book_info)
    return all_books