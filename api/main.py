# -*- coding: utf-8 -*-
import sys
import subprocess
import json
import re
import os
import requests
import time
import random
import hashlib

# 获取 main.py 脚本所在的目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- 百度翻译配置 ---
BAIDU_APP_ID = '20260307002567838'
BAIDU_APP_KEY = '710hzHTUaVxae7gAuMc1'
# --------------------

def is_chinese(text):
    """判断字符串是否包含中文字符"""
    return any('\u4e00' <= char <= '\u9fff' for char in text)

def run_tool(script_path, text, translation=None):
    """运行工具脚本并获取输出"""
    try:
        command = ['python3', script_path, text]
        if translation:
            command.append(translation)
            
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        return {"error": f"Tool execution failed: {e.stderr}"}
    except json.JSONDecodeError:
        return {"error": "Failed to decode tool output as JSON."}

def get_baidu_translation(query, to_lang='en'):
    """使用官方百度翻译 API"""
    from_lang = 'auto'
    
    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    salt = random.randint(32768, 65536)
    sign_str = BAIDU_APP_ID + query + str(salt) + BAIDU_APP_KEY
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'q': query,
        'from': from_lang,
        'to': to_lang,
        'appid': BAIDU_APP_ID,
        'salt': salt,
        'sign': sign
    }

    try:
        response = requests.post(url, params=payload, headers=headers, timeout=5)
        result = response.json()

        if 'trans_result' in result:
            return result['trans_result'][0]['dst']
        elif 'error_msg' in result:
            return f"翻译失败: {result['error_msg']}"
        else:
            return "翻译失败: 未知错误"
            
    except requests.exceptions.RequestException as e:
        return f"网络请求失败: {e}"
    except Exception as e:
        return f"解析失败: {e}"


def generate_html_output(data, lang):
    """生成用于 canvas.push 的 HTML"""
    if "error" in data:
        return f"<p>处理出错: {data['error']}</p>"

    if lang == "chinese":
        return f"""
        <h2>{data['text']}</h2>
        <p><strong>英文:</strong> {data['translation']}</p>
        <p><strong>拼音:</strong> {data['pinyin']}</p>
        <p><strong>相关词组:</strong> {' / '.join(data['related_words'])}</p>
        """
    elif lang == "english":
        return f"""
        <h2>{data['text']}</h2>
        <p><strong>中文:</strong> {data['translation']}</p>
        <p><strong>IPA 音标:</strong> {data['ipa']}</p>
        """
    return ""

def main(input_text):
    """接收文本输入，返回处理后的HTML内容。"""
    if not input_text:
        return "<p>请输入要分析的文本。</p>"

    # 注意：为了让 Vercel 能找到 tools 目录，我们需要使用相对于 SCRIPT_DIR 的路径
    if is_chinese(input_text):
        lang = "chinese"
        tool_path = os.path.join(SCRIPT_DIR, 'tools', 'process_chinese.py')
        english_translation = get_baidu_translation(input_text)
        tool_result = run_tool(tool_path, input_text, english_translation)
    else:
        lang = "english"
        tool_path = os.path.join(SCRIPT_DIR, 'tools', 'process_english.py')
        chinese_translation = get_baidu_translation(input_text, to_lang='zh')
        tool_result = run_tool(tool_path, input_text, chinese_translation)
        
    html_content = generate_html_output(tool_result, lang)
    return html_content

if __name__ == "__main__":
    # 这部分保留，以便我们仍然可以从命令行独立测试 main.py
    if len(sys.argv) > 1:
        test_text = sys.argv[1]
        result_html = main(test_text)
        print(result_html)