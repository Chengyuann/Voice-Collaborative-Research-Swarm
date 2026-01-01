import os
import dashscope
from http import HTTPStatus

def listen_to_audio(url: str) -> str:
    """
    Transcribes audio from a URL into text using Aliyun Qwen-ASR.
    Args:
        url (str): The public URL of the audio file (mp3/wav).
    """
    print(f"🎧 [TOOL] Transcribing audio from: {url}")

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        return "SYSTEM ERROR: DASHSCOPE_API_KEY is missing."

    try:
        # 调用通义千问 ASR 模型
        response = dashscope.MultiModalConversation.call(
            api_key=api_key,
            model="qwen3-asr-flash", 
            messages=[
                {'role': 'system', 'content': [{'text': 'You are a helper.'}]},
                {'role': 'user', 'content': [{'audio': url}]}
            ]
        )

        if response.status_code == HTTPStatus.OK:
            # 提取识别出的文本
            text = response.output.choices[0].message.content[0]['text']
            print(f"✅ [TOOL] Transcript: {text}")
            return text

        return f"ASR API Error: {response.message}"

    except Exception as e:
        return f"ASR Exception: {str(e)}"