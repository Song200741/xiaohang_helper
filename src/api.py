import json
import requests
from config import SILICONFLOW_API_KEY, API_URL, MODEL_NAME, REQUEST_TIMEOUT


def get_ai_stream(question, sys_prompt, messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}"
    }
    chat_messages = [{"role": "system", "content": sys_prompt}]
    chat_messages.extend(messages)
    chat_messages.append({"role": "user", "content": question})

    payload = {
        "model": MODEL_NAME,
        "messages": chat_messages,
        "temperature": 0.7,
        "stream": True
    }
    try:
        res = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            stream=True,
            timeout=REQUEST_TIMEOUT
        )
        if res.status_code == 401:
            yield "❌ API Key失效"
            return
        if res.status_code != 200:
            yield f"❌ 接口异常，状态码：{res.status_code}"
            return
        res.raise_for_status()
        for chunk in res.iter_lines():
            if not chunk:
                continue
            chunk_text = chunk.decode("utf-8").strip()
            if chunk_text.startswith("data: "):
                chunk_text = chunk_text[6:]
            if chunk_text == "[DONE]":
                break
            try:
                chunk_json = json.loads(chunk_text)
                delta = chunk_json["choices"][0]["delta"]
                content = delta.get("content")
                if content is None:
                    continue
                yield content
            except (json.JSONDecodeError, KeyError, IndexError):
                yield "\n⚠️ AI返回数据解析失败，部分内容丢失"
    except requests.exceptions.Timeout:
        yield "❌ AI响应超时，请稍后重新提问"
    except requests.exceptions.ConnectionError:
        yield "❌ 网络连接失败，请检查网络后重试"
    except Exception as e:
        yield f"❌ 请求发生未知错误：{str(e)}"