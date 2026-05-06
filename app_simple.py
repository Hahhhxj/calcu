from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    print('健康检查')
    return jsonify({'status': 'ok'})

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        expression = data.get('expression')
        if expression:
            result = eval(expression)
            return jsonify({'result': result, 'db_status': 'success', 'db_error': None})
        else:
            return jsonify({'error': '表达式不能为空'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/register', methods=['POST'])
def register():
    return jsonify({'message': '注册成功'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') and data.get('password'):
        return jsonify({'message': '登录成功', 'user': {'id': 1, 'username': data.get('username')}})
    else:
        return jsonify({'error': '用户名或密码错误'}), 401

if __name__ == '__main__':
    print('启动Flask应用...')
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
