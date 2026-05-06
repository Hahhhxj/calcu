from flask import Flask, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print('启动Flask应用...')
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
