# -*- coding: utf-8 -*-
import json
from http.server import BaseHTTPRequestHandler

# --- Vercel 的极简诊断 Handler ---

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 彻底忽略所有请求内容和业务逻辑
        try:
            # 总是返回一个固定的、写死的成功信息
            response_data = {'html': "<h1>诊断模式</h1><p>后端服务已成功响应！</p>"}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            # 如果连这个最简单的操作都失败了，就返回错误
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            error_response = {'html': f"<p style='color: red;'>服务器在诊断模式下出错: {e}</p>"}
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
        
        return