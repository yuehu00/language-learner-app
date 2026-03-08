# -*- coding: utf-8 -*-
import json
import hashlib
import random
import time
import requests
from pypinyin import pinyin, Style
import jieba
import eng_to_ipa as ipa

# --- 配置 ---
BAIDU_APP_ID = '20260307002567838'
BAIDU_APP_KEY = '710hzHTUaVxae7gAuMc1'
# ------------

# --- 核心功能函数 ---

def get_pinyin(text):
    return ' '.join([item[0] for item in pinyin(text, style=Style.TONE)])

def get_related_words(text):
    return jieba.lcut(text)

def get_phonetic_transcription(text):
    words = text.split()
    return ' '.join([ipa.convert(word) for word in words])

def is_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)

def get_baidu_translation(query, to_lang='en'):
    # (百度翻译函数保持不变)
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
        else:
            return f"翻译失败: {result.get('error_msg', '未知错误')}"
    except Exception as e:
        return f"网络或翻译请求失败: {e}"

def generate_html_output(data, lang):
    # (HTML生成函数保持不变)
    if "error" in data:
        return f"<p>处理出错: {data['error']}</p>"
    if lang == "chinese":
        return f"""<h2>{data['text']}</h2><p><strong>英文:</strong> {data['translation']}</p><p><strong>拼音:</strong> {data['pinyin']}</p><p><strong>相关词组:</strong> {' / '.join(data['related_words'])}</p>"""
    elif lang == "english":
        return f"""<h2>{data['text']}</h2><p><strong>中文:</strong> {data['translation']}</p><p><strong>IPA 音标:</strong> {data['ipa']}</p>"""
    return ""

# --- Vercel 的 WSGI 应用入口 ---

def app(environ, start_response):
    # 只处理对 /api/process 的 POST 请求
    if environ['PATH_INFO'] == '/api/process' and environ['REQUEST_METHOD'] == 'POST':
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(content_length)
            data = json.loads(request_body)
            input_text = data.get('text')

            if not input_text:
                response_data = {'html': "<p>好像没听到声音，请再试一次。</p>"}
            else:
                if is_chinese(input_text):
                    lang = "chinese"
                    tool_result = {
                        "text": input_text,
                        "translation": get_baidu_translation(input_text, to_lang='en'),
                        "pinyin": get_pinyin(input_text),
                        "related_words": get_related_words(input_text)
                    }
                else:
                    lang = "english"
                    tool_result = {
                        "text": input_text,
                        "translation": get_baidu_translation(input_text, to_lang='zh'),
                        "ipa": get_phonetic_transcription(input_text)
                    }
                html_content = generate_html_output(tool_result, lang)
                response__data = {'html': html_content}

            status = '200 OK'
            headers = [('Content-type', 'application/json; charset=utf-8')]
            start_response(status, headers)
            return [json.dumps(response_data, ensure_ascii=False).encode('utf-8')]

        except Exception as e:
            status = '500 Internal Server Error'
            headers = [('Content-type', 'application/json; charset=utf-8')]
            start_response(status, headers)
            error_response = {'html': f"<p style='color: red;'>服务器处理出错: {e}</p>"}
            return [json.dumps(error_response, ensure_ascii=False).encode('utf-8')]
    
    # 对于所有其他请求，返回 404
    status = '404 Not Found'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b'Not Found']