# Vercel 会将这个文件作为一个 Serverless Function 来运行
# 我们需要将 server.py 的内容适配到这里

from flask import Flask, request, jsonify, send_from_directory
import os
import sys

# --- 将项目根目录添加到 Python 路径中 ---
# Vercel 的工作目录是 /var/task/，我们的代码在 /var/task/api/
# 需要将 /var/task/ 添加到路径，以便能导入 main 和 tools
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
# -----------------------------------------

# 导入我们的核心逻辑
from main import main as process_text_logic

# 将 Flask 的静态文件目录指向项目的根目录
# Vercel 会将 public/ 或根目录下的文件作为静态资源
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'public'), static_url_path='')

# Vercel 平台不需要 CORS，因为它通常处理同源或配置好的来源
# from flask_cors import CORS
# CORS(app)

@app.route('/')
def index():
    # Vercel 会自动服务 public 目录下的 index.html
    # 这个路由主要是为了本地测试和作为备用
    return send_from_directory(os.path.join(BASE_DIR, 'public'), 'index.html')

@app.route('/api/process', methods=['POST'])
def process_text_endpoint():
    # 这是我们的核心 API 端点
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    input_text = data['text']
    
    # 调用 main.py 中的逻辑
    html_content = process_text_logic(input_text)
    
    return jsonify({'html': html_content})

# 在 Vercel 环境下，我们不需要自己运行 app.run()
# Vercel 会自动处理应用的启动
# if __name__ == '__main__':
#     app.run(...)