# -*- coding: utf-8 -*-
import sys
import json
from pypinyin import pinyin, Style
import jieba

def get_pinyin(text):
    """获取汉字的拼音"""
    return ' '.join([item[0] for item in pinyin(text, style=Style.TONE)])

def get_related_words(text):
    """获取相关词组"""
    # 使用jieba进行分词
    words = jieba.lcut(text)
    # 这里只是一个简单的示例，返回分词结果
    # 在实际应用中，你可能需要一个更复杂的词典或API来查找相关词
    return words

def main():
    if len(sys.argv) > 1:
        text = sys.argv[1]
        # 第二个参数是翻译结果
        translation = sys.argv[2] if len(sys.argv) > 2 else ""
        
        pinyin_result = get_pinyin(text)
        related_words_result = get_related_words(text)

        result = {
            "text": text,
            "pinyin": pinyin_result,
            "related_words": related_words_result,
            "translation": translation
        }
        print(json.dumps(result, ensure_ascii=False))
    else:
        error_result = {
            "error": "No input text provided."
        }
        print(json.dumps(error_result, ensure_ascii=False))

if __name__ == "__main__":
    main()