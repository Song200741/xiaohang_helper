import streamlit as st
import time
from pathlib import Path
from prompts import PRESET_QUESTIONS


def init_session_state():
    if "user_role" not in st.session_state:
        st.session_state.user_role = "新生"
    if "last_role" not in st.session_state:
        st.session_state.last_role = "新生"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "temp_question" not in st.session_state:
        st.session_state.temp_question = ""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "conversations" not in st.session_state:
        st.session_state.conversations = []


def set_page_config():
    st.set_page_config(page_title="小航 - 郑州航院校园AI助手", layout="wide")


def render_custom_css():
    st.markdown("""
<style>
.stAppDeployButton,
[data-testid="stAppDeployButton"],
.stMainMenu,
[data-testid="stMainMenu"],
.stToolbarActions,
[data-testid="stToolbarActions"] {
    display: none !important;
}
.stAppToolbar {
    display: none !important;
}
body {
    font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}
.stTitle {
    color: #1e3a5f !important;
    font-weight: 700;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
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
.stButton > button:nth-child(-n+4) {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important;
}
.stButton > button:nth-child(-n+4):hover {
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
}
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
.stDivider {
    border-top: 2px solid #e0e7ff;
    margin: 30px 0;
}
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
.stWarning {
    border-radius: 10px;
    border-left: 4px solid #f59e0b;
    background: #fffbeb;
}
.stError {
    border-radius: 10px;
    border-left: 4px solid #ef4444;
    background: #fef2f2;
}
.stSuccess {
    border-radius: 10px;
    border-left: 4px solid #10b981;
    background: #ecfdf5;
}
.stMarkdown h3 {
    color: #374151;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


def render_title():
    st.title("✈️ 小航 · 郑州航院校园信息助手")


def render_yellow_page():
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


def render_role_selector():
    user_role = st.selectbox(
        "你是？",
        ["新生", "在校生", "教师"],
        key="user_role"
    )
    if st.session_state.user_role != st.session_state.last_role:
        st.session_state.messages = []
        st.session_state.last_role = st.session_state.user_role
    return user_role


def load_school_data():
    school_data = ""
    data_dir = Path(__file__).parent.parent / "data"
    content_list = []

    md_files = sorted(data_dir.glob("*.md"))
    if not md_files:
        st.warning("⚠️ data目录下无md文件，请添加资料文件")
        school_data = "未读取成功"
    else:
        for file_path in md_files:
            try:
                file_text = file_path.read_text(encoding="utf-8")
                content_list.append(f"=== {file_path.name} ===\n{file_text}")
            except Exception as e:
                st.warning(f"⚠️ 读取文件 {file_path.name} 失败：{str(e)}")
        school_data = "\n\n".join(content_list)
    
    return school_data


def render_preset_questions():
    st.markdown("#### 💡 试试这些推荐问题：")
    tab1, tab2, tab3 = st.tabs(["新生指南", "办事流程", "应急防骗"])

    with tab1:
        cols_new = st.columns(2)
        for idx, q in enumerate(PRESET_QUESTIONS["新生指南"]):
            with cols_new[idx % 2]:
                if st.button(q, key=f"q_btn_new_{idx}"):
                    st.session_state.temp_question = q

    with tab2:
        cols_flow = st.columns(2)
        for idx, q in enumerate(PRESET_QUESTIONS["办事流程"]):
            with cols_flow[idx % 2]:
                if st.button(q, key=f"q_btn_flow_{idx}"):
                    st.session_state.temp_question = q

    with tab3:
        cols_anti = st.columns(2)
        for idx, q in enumerate(PRESET_QUESTIONS["应急防骗"]):
            with cols_anti[idx % 2]:
                if st.button(q, key=f"q_btn_anti_{idx}"):
                    st.session_state.temp_question = q


def render_input():
    user_input = st.text_input("有啥想问的？", value=st.session_state.temp_question)
    if st.session_state.temp_question != "":
        st.session_state.temp_question = ""
    return user_input.strip()


def render_messages():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            content = msg["content"] or ""
            st.markdown(content)


def render_history():
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 新对话", key="new_conversation"):
            new_id = len(st.session_state.conversations) + 1
            st.session_state.conversations.append({
                "id": new_id,
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "role": st.session_state.user_role,
                "records": []
            })
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.session_state.conversations:
            text = ""
            for conv in st.session_state.conversations:
                text += f"=== 第{conv['id']}次对话 · {conv['time']} · {conv['role']} ===\n"
                for record in conv['records']:
                    text += f"【{record['time']}】\n"
                    text += f"问：{record['question']}\n"
                    text += f"答：{record['answer']}\n"
                    text += "---\n"
                text += "\n"
            st.download_button(
                label="📥 导出对话",
                data=text,
                file_name=f"小航对话记录_{time.strftime('%Y%m%d')}.txt",
                mime="text/plain",
            )
    with col3:
        if st.button("清空历史"):
            st.session_state.history = []
            st.session_state.messages = []
            st.session_state.conversations = []
            st.rerun()

    with st.expander(f"📝 对话历史", expanded=False):
        if st.session_state.conversations:
            for conv in reversed(st.session_state.conversations):
                with st.expander(f"第{conv['id']}次对话 · {conv['time']}", expanded=False):
                    if conv['records']:
                        for record in reversed(conv['records']):
                            st.markdown(f"""
<div style="border-radius: 12px; padding: 16px; margin-bottom: 12px; border-left: 4px solid #6366f1;">
    <div style="font-weight: 600; color: #6366f1; margin-bottom: 8px;">[{record['time']}]</div>
    <div style="font-weight: 600; color: #334155; margin-bottom: 4px;">问：{record['question']}</div>
    <div style="color: #475569; line-height: 1.6;">答：{record['answer']}</div>
</div>
""", unsafe_allow_html=True)
                    else:
                        st.info("该对话暂无问答记录")
        else:
            st.info("暂无对话记录，开始提问吧！")