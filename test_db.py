import pymysql

try:
    print('正在连接数据库...')
    db = pymysql.connect(
        host='localhost',
        port=13306,
        user='calc',
        password='123456',
        database='calc',
        cursorclass=pymysql.cursors.DictCursor
    )
    print('数据库连接成功!')

    with db.cursor() as cursor:
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f'查询结果: {result}')

    db.close()
    print('数据库连接已关闭')
except Exception as e:
    print(f'数据库连接失败: {e}')
    import traceback
    traceback.print_exc()
