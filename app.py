from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        import pymysql
        conn = pymysql.connect(
            host='localhost',
            port=13306,
            user='calc',
            password='123456',
            database='calc',
            cursorclass=pymysql.cursors.DictCursor
        )
        print('数据库连接成功')
        return conn
    except Exception as e:
        print(f'数据库连接失败: {e}')
        return None

def create_tables_if_needed(db_conn):
    if not db_conn:
        return
    try:
        with db_conn.cursor() as cursor:
            create_user_table = """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """
            cursor.execute(create_user_table)

            create_log_table = """
                CREATE TABLE IF NOT EXISTS operation_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expression VARCHAR(255),
                    result VARCHAR(255),
                    user_id INT
                );
            """
            cursor.execute(create_log_table)

            try:
                cursor.execute("ALTER TABLE operation_log ADD COLUMN user_id INT")
                db_conn.commit()
                print('添加user_id列成功')
            except Exception as e:
                print(f'user_id列可能已存在: {e}')
        db_conn.commit()
        print('表创建成功或已存在')
    except Exception as e:
        print(f'创建表失败: {e}')

def hash_password(password):
    return password

@app.route('/api/register', methods=['POST'])
def register():
    try:
        print('收到注册请求')
        data = request.get_json()
        print(f'请求数据: {data}')

        if not data:
            print('请求数据为空')
            return jsonify({'error': '请求数据为空'}), 400

        username = data.get('username')
        password = data.get('password')

        print(f'用户名: {username}, 密码: {password}')

        if not username or not password:
            print('用户名或密码为空')
            return jsonify({'error': '用户名和密码不能为空'}), 400

        db = get_db_connection()
        if not db:
            print('数据库连接失败')
            return jsonify({'error': '数据库连接失败'}), 500

        try:
            create_tables_if_needed(db)

            with db.cursor() as cursor:
                check_query = "SELECT * FROM users WHERE username = %s"
                cursor.execute(check_query, (username,))
                if cursor.fetchone():
                    print('用户名已存在')
                    return jsonify({'error': '用户名已存在'}), 400

                insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
                print(f'执行插入: {insert_query}, 参数: ({username}, {hash_password(password)})')
                cursor.execute(insert_query, (username, hash_password(password)))
            db.commit()
            print('注册成功')
            return jsonify({'message': '注册成功'})
        finally:
            db.close()
    except Exception as e:
        print(f'注册失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        print('收到登录请求')
        data = request.get_json()
        print(f'请求数据: {data}')

        if not data:
            print('请求数据为空')
            return jsonify({'error': '请求数据为空'}), 400

        username = data.get('username')
        password = data.get('password')

        print(f'用户名: {username}, 密码: {password}')

        if not username or not password:
            print('用户名或密码为空')
            return jsonify({'error': '用户名和密码不能为空'}), 400

        db = get_db_connection()
        if not db:
            print('数据库连接失败')
            return jsonify({'error': '数据库连接失败'}), 500

        try:
            with db.cursor() as cursor:
                check_query = "SELECT * FROM users WHERE username = %s"
                cursor.execute(check_query, (username,))
                user_record = cursor.fetchone()
                print(f'用户记录: {user_record}')

                if user_record:
                    print(f'数据库中的密码: {user_record.get("password")}')
                    print(f'输入的密码: {password}')

                query = "SELECT id, username FROM users WHERE username = %s AND password = %s"
                print(f'执行查询: {query}, 参数: ({username}, {hash_password(password)})')
                cursor.execute(query, (username, hash_password(password)))
                user = cursor.fetchone()
                print(f'查询结果: {user}')

            if user:
                print('登录成功')
                return jsonify({'message': '登录成功', 'user': user})
            else:
                print('登录失败: 用户名或密码错误')
                return jsonify({'error': '用户名或密码错误'}), 401
        finally:
            db.close()
    except Exception as e:
        print(f'登录失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': '登录失败'}), 500

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        print('收到计算请求')
        data = request.get_json()
        print(f'请求数据: {data}')

        if not data:
            print('请求数据为空')
            return jsonify({'error': '请求数据为空'}), 400

        expression = data.get('expression')
        user_id = data.get('user_id')

        print(f'表达式: {expression}, 用户ID: {user_id}')

        if not expression:
            print('表达式为空')
            return jsonify({'error': '表达式不能为空'}), 400

        if '*' in expression or '/' in expression:
            if not user_id:
                print('乘法/除法需要登录')
                return jsonify({'error': '乘法和除法运算需要登录'}), 401

            db = get_db_connection()
            if not db:
                print('数据库连接失败')
                return jsonify({'error': '数据库连接失败'}), 500

            try:
                with db.cursor() as cursor:
                    check_query = "SELECT id FROM users WHERE id = %s"
                    cursor.execute(check_query, (user_id,))
                    if not cursor.fetchone():
                        print('用户不存在')
                        return jsonify({'error': '用户不存在'}), 401
            finally:
                db.close()

        print('执行计算')
        result = eval(expression)
        print(f'计算结果: {result}')

        db_status = 'success'
        db_error = None

        if user_id:
            db = get_db_connection()
            if db:
                try:
                    print('记录到数据库')
                    create_tables_if_needed(db)

                    with db.cursor() as cursor:
                        insert_query = "INSERT INTO operation_log (expression, result, user_id) VALUES (%s, %s, %s)"
                        print(f'执行插入: {insert_query}, 参数: ({expression}, {str(result)}, {user_id})')
                        cursor.execute(insert_query, (expression, str(result), user_id))
                        last_id = cursor.lastrowid
                        print(f'插入的记录ID: {last_id}')

                    db.commit()
                    print('事务提交成功')
                    print('记录成功')
                except Exception as e:
                    db_status = 'failed'
                    db_error = str(e)
                    print(f'记录日志失败: {e}')
                finally:
                    db.close()
            else:
                db_status = 'failed'
                db_error = '数据库连接失败'
                print('数据库连接失败，无法记录')

        return jsonify({'result': result, 'db_status': db_status, 'db_error': db_error})
    except Exception as e:
        print(f'计算错误: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'计算错误: {str(e)}'}), 400

@app.route('/api/history', methods=['POST'])
def get_history():
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': '获取历史记录需要登录'}), 401

        db = get_db_connection()
        if not db:
            return jsonify({'error': '数据库连接失败'}), 500

        try:
            with db.cursor() as cursor:
                check_query = "SELECT id FROM users WHERE id = %s"
                cursor.execute(check_query, (user_id,))
                if not cursor.fetchone():
                    return jsonify({'error': '用户不存在'}), 401

                query = """
                    SELECT id, created_at, expression, result
                    FROM operation_log
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 10
                """
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()
            return jsonify(results)
        finally:
            db.close()
    except Exception as e:
        print(f'获取历史记录失败: {e}')
        return jsonify({'error': '获取历史记录失败'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print('启动Flask应用...')
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
