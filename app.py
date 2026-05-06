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
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_vip BOOLEAN DEFAULT FALSE
                );
            """
            cursor.execute(create_user_table)

            create_vip_info_table = """
                CREATE TABLE IF NOT EXISTS vip_info (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT UNIQUE NOT NULL,
                    gender VARCHAR(10),
                    phone VARCHAR(20),
                    birthday DATE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            """
            cursor.execute(create_vip_info_table)

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
            
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN is_vip BOOLEAN DEFAULT FALSE")
                db_conn.commit()
                print('添加is_vip列成功')
            except Exception as e:
                print(f'is_vip列可能已存在: {e}')
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

                insert_query = "INSERT INTO users (username, password, is_vip) VALUES (%s, %s, %s)"
                print(f'执行插入: {insert_query}, 参数: ({username}, {hash_password(password)}, False)')
                cursor.execute(insert_query, (username, hash_password(password), False))
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
                query = "SELECT id, username, is_vip FROM users WHERE username = %s AND password = %s"
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

@app.route('/api/register_vip', methods=['POST'])
def register_vip():
    try:
        print('收到VIP注册请求')
        data = request.get_json()
        print(f'请求数据: {data}')

        if not data:
            print('请求数据为空')
            return jsonify({'error': '请求数据为空'}), 400

        user_id = data.get('user_id')
        gender = data.get('gender')
        phone = data.get('phone')
        birthday = data.get('birthday')
        agree = data.get('agree')

        print(f'用户ID: {user_id}, 性别: {gender}, 手机: {phone}, 生日: {birthday}, 同意: {agree}')

        if not user_id:
            print('用户ID为空')
            return jsonify({'error': '请先登录'}), 401

        if not gender:
            print('性别未选择')
            return jsonify({'error': '请选择性别'}), 400

        if not phone:
            print('手机号码为空')
            return jsonify({'error': '请填写手机号码'}), 400

        if not birthday:
            print('生日未选择')
            return jsonify({'error': '请选择生日'}), 400

        if not agree:
            print('未同意注册VIP')
            return jsonify({'error': '请勾选同意注册VIP'}), 400

        db = get_db_connection()
        if not db:
            print('数据库连接失败')
            return jsonify({'error': '数据库连接失败'}), 500

        try:
            create_tables_if_needed(db)

            with db.cursor() as cursor:
                check_query = "SELECT * FROM users WHERE id = %s"
                cursor.execute(check_query, (user_id,))
                user = cursor.fetchone()
                
                if not user:
                    print('用户不存在')
                    return jsonify({'error': '用户不存在'}), 401

                if user.get('is_vip'):
                    print('用户已是VIP')
                    return jsonify({'error': '您已经是VIP用户'}), 400

                update_query = "UPDATE users SET is_vip = TRUE WHERE id = %s"
                cursor.execute(update_query, (user_id,))

                insert_vip_query = """
                    INSERT INTO vip_info (user_id, gender, phone, birthday)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_vip_query, (user_id, gender, phone, birthday))
            
            db.commit()
            print('VIP注册成功')
            return jsonify({'message': 'VIP注册成功', 'is_vip': True})
        finally:
            db.close()
    except Exception as e:
        print(f'VIP注册失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'VIP注册失败: {str(e)}'}), 500

@app.route('/api/check_vip', methods=['POST'])
def check_vip():
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': '请先登录'}), 401

        db = get_db_connection()
        if not db:
            return jsonify({'error': '数据库连接失败'}), 500

        try:
            with db.cursor() as cursor:
                query = "SELECT is_vip FROM users WHERE id = %s"
                cursor.execute(query, (user_id,))
                user = cursor.fetchone()

                if not user:
                    return jsonify({'error': '用户不存在'}), 401

                return jsonify({'is_vip': user.get('is_vip', False)})
        finally:
            db.close()
    except Exception as e:
        print(f'检查VIP状态失败: {e}')
        return jsonify({'error': '检查VIP状态失败'}), 500

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

        if '*' in expression:
            if not user_id:
                print('乘法需要登录')
                return jsonify({'error': '乘法运算需要登录'}), 401

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

        elif '/' in expression:
            if not user_id:
                print('除法需要登录')
                return jsonify({'error': '除法运算需要登录'}), 401

            db = get_db_connection()
            if not db:
                print('数据库连接失败')
                return jsonify({'error': '数据库连接失败'}), 500

            try:
                with db.cursor() as cursor:
                    query = "SELECT id, is_vip FROM users WHERE id = %s"
                    cursor.execute(query, (user_id,))
                    user = cursor.fetchone()

                    if not user:
                        print('用户不存在')
                        return jsonify({'error': '用户不存在'}), 401

                    if not user.get('is_vip'):
                        print('除法需要VIP')
                        return jsonify({'error': '除法运算需要注册VIP'}), 401
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
