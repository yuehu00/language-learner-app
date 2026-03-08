# -*- coding: utf-8 -*-
import os
import json
import hashlib
import random
import time
import requests
from flask import Flask, request, jsonify
from pypinyin import pinyin, Style
import jieba
import eng_to_ipa as ipa

# --- 配置 ---
BAIDU_APP_ID = '20260307002567838'
BAIDU_APP_KEY = '710hzHTUaVxae7gAuMc1'
# ------------

# 初始化 Flask 应用
# Vercel 会自动处理静态文件的服务，我们不需要在这里特别指定 static_folder
app = Flask(__name__)

# --- 核心功能函数 ---

def get_pinyin(text):
    """获取汉字的拼音"""
    return ' '.join([item[0] for item in pinyin(text, style=Style.TONE)])

def get_related_words(text):
    """获取相关词组"""
    return jieba.lcut(text)

def get_phonetic_transcription(text):
    """获取英文单词的IPA音标"""
    words = text.split()
    transcriptions = [ipa.convert(word) for word in words]
    return ' '.join(transcriptions)

def is_chinese(text):
    """判断字符串是否包含中文字符"""
    return any('\u4e00' <= char <= '\u9fff' for char in text)

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
    payload = {'q': query, 'from': from_lang, 'to': to_lang, 'appid': BAIDU_APP_ID, 'salt': salt, 'sign': sign}
    try:
        response = requests.post(url, params=payload, headers=headers, timeout=5)
        result = response.json()
        if 'trans_result' in result:
            return result['trans_result'][0]['dst']
        elif 'error_msg' in result:
            return f"翻译失败: {result['error_msg']}"
        else:
            return "翻译失败: 未知错误"
    except Exception as e:
        return f"网络或翻译请求失败: {e}"

def generate_html_output(data, lang):
    """根据处理结果生成HTML"""
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

# --- API 路由 ---

@app.route('/api/process', methods=['POST'])
def process_text_endpoint():
    """主 API 端点，接收文本并返回处理后的 HTML"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    input_text = data.get('text')
    if not input_text:
        return jsonify({'html': "<p>好像没听到声音，请再试一次。</p>"})

    try:
        if is_chinese(input_text):
            lang = "chinese"
            translation = get_baidu_translation(input_text, to_lang='en')
            pinyin_result = get_pinyin(input_text)
            related_words = get_related_words(input_text)
            tool_result = {
                "text": input_text,
                "translation": translation,
                "pinyin": pinyin_result,
                "related_words": related_words
            }
        else:
            lang = "english"
            translation = get_baidu_translation(input_text, to_lang='zh')
            ipa_result = get_phonetic_transcription(input_text)
            tool_result = {
                "text": input_text,
                "translation": translation,
                "ipa": ipa_result
            }
        
        html_content = generate_html_output(tool_result, lang)
        return jsonify({'html': html_content})

    except Exception as e:
        error_html = f"<p style='color: red;'>服务器处理出错: {e}</p>"
        return jsonify({'html': error_html}), 500

# Vercel 会自动处理根路由指向 public/index.html，我们不需要 Flask 来处理
# @app.route('/')
# def index():
#     return "Welcome to the API. Please use the /api/process endpoint."