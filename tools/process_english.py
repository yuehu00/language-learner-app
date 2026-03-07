# -*- coding: utf-8 -*-
import sys
import json
import eng_to_ipa as ipa

def get_phonetic_transcription(text):
    """获取英文单词的IPA音标"""
    # eng_to_ipa对于多词短语可能效果不佳，最好是单个词
    # 这里我们假设输入是一个或多个由空格分隔的单词
    words = text.split()
    transcriptions = [ipa.convert(word) for word in words]
    return ' '.join(transcriptions)

def main():
    if len(sys.argv) > 1:
        text = sys.argv[1]
        # 第二个参数是翻译结果
        translation = sys.argv[2] if len(sys.argv) > 2 else ""
        
        ipa_result = get_phonetic_transcription(text)

        result = {
            "text": text,
            "ipa": ipa_result,
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