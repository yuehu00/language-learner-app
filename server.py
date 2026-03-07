from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os

# 将 Flask 的静态文件目录指向当前目录
app = Flask(__name__, static_folder='.', static_url_path='')

# 获取 server.py 脚本所在的目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    # 当访问根 URL 时，发送 index.html
    return send_from_directory('.', 'index.html')

@app.route('/process', methods=['POST'])
def process_text():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    input_text = data['text']
    
    # 构建到 main.py 的绝对路径 (修正)
    # server.py 和 main.py 在同一个目录下
    skill_main_path = os.path.join(BASE_DIR, 'main.py')

    try:
        # 使用 python3 执行 skill 的主脚本
        result = subprocess.run(
            ['python3', skill_main_path, input_text],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        # 返回由 main.py 生成的 HTML
        return jsonify({'html': result.stdout})
        
    except subprocess.CalledProcessError as e:
        # 如果脚本执行出错，返回错误信息
        error_message = f"Skill execution failed: {e.stderr}"
        return jsonify({'error': error_message}), 500
    except FileNotFoundError:
        return jsonify({'error': f"Skill script not found at {skill_main_path}"}), 500

if __name__ == '__main__':
    # 允许来自任何源的请求，方便本地开发
    from flask_cors import CORS
    CORS(app)
    # 使用我们生成的SSL证书来启用HTTPS
    # 这样浏览器就会信任我们的本地服务器，并记住麦克风权限
    cert_path = os.path.join(BASE_DIR, 'cert.pem')
    key_path = os.path.join(BASE_DIR, 'key.pem')
    app.run(debug=True, port=5002, ssl_context=(cert_path, key_path), use_reloader=False)
