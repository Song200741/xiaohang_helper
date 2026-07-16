import sys
import os
import streamlit as st
import requests
import json
from pathlib import Path

# 自动适配导入路径，消除爆红
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import load_school_info, get_system_prompt, PRESET_QUESTIONS

# -------------------------- 配置区 --------------------------
SILICONFLOW_API_KEY = "sk-iwtaefofkkeztoxoqrbzehnujtqzrnbcavzmlwrjkmyrdzvc"
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL_NAME = "deepseek-ai/DeepSeek-V4-Pro"
REQUEST_TIMEOUT = 30
# -----------------------------------------------------------

# 页面基础设置
st.set_page_config(page_title="小航 - 郑州航院校园AI助手", layout="wide")

# 自定义CSS样式
st.markdown("""
<style>
/* 隐藏右上角Deploy按钮和主菜单 */
.stAppDeployButton,
[data-testid="stAppDeployButton"],
.stMainMenu,
[data-testid="stMainMenu"],
.stToolbarActions,
[data-testid="stToolbarActions"] {
    display: none !important;
}

/* 隐藏顶部工具栏 */
.stAppToolbar {
    display: none !important;
}

/* 页面整体美化 */
body {
    font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

/* 标题样式 */
.stTitle {
    color: #1e3a5f !important;
    font-weight: 700;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

/* 选择框样式 */
.stSelectbox .react-aria-ComboBox {
    border-radius: 10px;
    border: 2px solid #e0e7ff;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stSelectbox .react-aria-ComboBox:hover {
    border-color: #6366f1;
    box-shadow: 0 4px 12px rgba(99,102,241,0.15);
}
.stSelectbox [role="combobox"] {
    border-radius: 10px;
    border: none !important;
    background: transparent !important;
}

/* 按钮样式 */
.stButton > button {
    border-radius: 10px !important;
    border: none !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 14px rgba(0,0,0,0.15) !important;
}

/* 推荐问题按钮 - 主色调 */
.stButton > button:nth-child(-n+4) {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important;
}
.stButton > button:nth-child(-n+4):hover {
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
}

/* 文本输入框样式 */
.stTextInput [data-rac] {
    border-radius: 10px !important;
    border: 2px solid #e0e7ff !important;
    padding: 14px 16px !important;
    background: white !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
.stTextInput [data-rac]:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

/* 聊天消息样式 */
.stChatMessage {
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.stChatMessage[data-role="user"] {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    color: white;
}
.stChatMessage[data-role="assistant"] {
    background: white;
    border: 1px solid #e0e7ff;
}

/* 分割线样式 */
.stDivider {
    border-top: 2px solid #e0e7ff;
    margin: 30px 0;
}

/* 表格样式 */
table {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
th {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important;
    font-weight: 600;
}
td {
    background: white !important;
}

/* 警告框样式 */
.stWarning {
    border-radius: 10px;
    border-left: 4px solid #f59e0b;
    background: #fffbeb;
}

/* 错误框样式 */
.stError {
    border-radius: 10px;
    border-left: 4px solid #ef4444;
    background: #fef2f2;
}

/* 成功框样式 */
.stSuccess {
    border-radius: 10px;
    border-left: 4px solid #10b981;
    background: #ecfdf5;
}

/* 副标题样式 */
.stMarkdown h3 {
    color: #374151;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.title("✈️ 小航 · 郑州航院校园信息助手")

with st.expander("📞 电话黄页", expanded=False):
    yellow_page_markdown = """
| 部门 | 联系电话 |
|------|----------|
| 校园110保卫处(24h) | 0371-61916110 ⚠以官方为准 |
| 学校总值班室 | 0371-61911000 ⚠以官方为准 |
| 后勤管理处 | 0371-61912800 ⚠以官方为准 |
| 后勤物业报修热线 | 0371-61913110 ⚠以官方为准 |
| 校医院急诊(24h) | 0371-61912730 ⚠以官方为准 |
| 招生办公室 | 0371-61916161 ⚠以官方为准 |
| 网信信息管理中心 | 0371-61912718 ⚠以官方为准 |
"""
    st.markdown(yellow_page_markdown)

# 会话状态初始化
if "user_role" not in st.session_state:
    st.session_state.user_role = "新生"
if "last_role" not in st.session_state:
    st.session_state.last_role = "新生"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "temp_question" not in st.session_state:
    st.session_state.temp_question = ""

# 1. 身份选择（课件标准：新生/在校生/教师）
user_role = st.selectbox(
    "你是？",
    ["新生", "在校生", "教师"],
    key="user_role"
)

# 切换身份清空对话，刷新prompt
if st.session_state.user_role != st.session_state.last_role:
    st.session_state.messages = []
    st.session_state.last_role = st.session_state.user_role

# 2. 加载校园md资料，从data目录读取四个指定文件
school_data = ""
required_files = ["办事流程.md", "应急防骗.md", "新生入学.md", "电话黄页.md"]
data_dir = Path("data")
missing_files = []
content_list = []

for filename in required_files:
    file_path = data_dir / filename
    if not file_path.exists():
        missing_files.append(filename)
        continue
    try:
        file_text = file_path.read_text(encoding="utf-8")
        content_list.append(f"=== {filename} ===\n{file_text}")
    except Exception as e:
        missing_files.append(f"{filename} (读取失败)")

if missing_files:
    st.warning(f"⚠️ 资料读取失败：缺失或无法读取的文件：{', '.join(missing_files)}")
    school_data = "未读取成功"
else:
    school_data = "\n\n".join(content_list)

# 拼接身份+资料+防幻觉完整系统提示词
sys_prompt = get_system_prompt(st.session_state.user_role, school_data)

# 3. 12个身份分组推荐问题按钮（课件标准）
st.markdown("#### 💡 试试这些推荐问题：")
cols = st.columns(4)
current_questions = PRESET_QUESTIONS.get(st.session_state.user_role, [])
for idx, q in enumerate(current_questions):
    with cols[idx % 4]:
        if st.button(q, key=f"q_btn_{idx}"):
            st.session_state.temp_question = q

# 主输入框
user_input = st.text_input("有啥想问的？", value=st.session_state.temp_question)
# 点击按钮后清空临时存储
if st.session_state.temp_question != "":
    st.session_state.temp_question = ""

final_input = user_input.strip()

# 展示历史对话
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# AI流式请求函数，细分各类报错提示
def get_ai_stream(question):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}"
    }
    chat_messages = [{"role": "system", "content": sys_prompt}]
    chat_messages.extend(st.session_state.messages)
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
        # 密钥失效鉴权错误
        if res.status_code == 401:
            yield "❌ API Key失效"
            return
        # 其他接口异常
        if res.status_code != 200:
            yield f"❌ 接口异常，状态码：{res.status_code}"
            return
        # 流式解析返回内容
        res.raise_for_status()
        full_text = ""
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
                    content = ""
                full_text += content
                yield content
            except (json.JSONDecodeError, KeyError, IndexError):
                yield "\n⚠️ AI返回数据解析失败，部分内容丢失"
    except requests.exceptions.Timeout:
        yield "❌ AI响应超时，请稍后重新提问"
    except requests.exceptions.ConnectionError:
        yield "❌ 网络连接失败，请检查网络后重试"
    except Exception as e:
        yield f"❌ 请求发生未知错误：{str(e)}"

# 处理提问逻辑
if final_input:
    # 存入对话历史并展示用户消息
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    # 流式输出AI回答
    with st.chat_message("assistant"):
        answer_generator = get_ai_stream(final_input)
        answer_text = st.write_stream(answer_generator)
    st.session_state.messages.append({"role": "assistant", "content": answer_text})

