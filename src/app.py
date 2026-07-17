import sys
import os
import time
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import (
    init_session_state,
    set_page_config,
    render_custom_css,
    render_title,
    render_yellow_page,
    render_role_selector,
    load_school_data,
    render_preset_questions,
    render_input,
    render_messages,
    render_history
)
from api import get_ai_stream
from prompts import get_system_prompt


def main():
    init_session_state()
    set_page_config()
    render_custom_css()
    render_title()
    render_yellow_page()
    render_role_selector()
    
    school_data = load_school_data()
    sys_prompt = get_system_prompt(st.session_state.user_role, school_data)
    
    render_preset_questions()
    final_input = render_input()
    render_messages()
    
    if not final_input.strip():
        st.warning("请输入问题后再提问~")
    else:
        st.session_state.messages.append({"role": "user", "content": final_input})
        with st.chat_message("user"):
            st.markdown(final_input)
        
        start_time = time.time()
        with st.chat_message("assistant"):
            with st.spinner("小航正在思考......"):
                answer_generator = get_ai_stream(
                    final_input,
                    sys_prompt,
                    st.session_state.messages[:-1]
                )
                answer_text = st.write_stream(answer_generator)
        end_time = time.time()
        st.session_state.messages.append({"role": "assistant", "content": answer_text})
        
        elapsed_time = round(end_time - start_time, 1)
        answer_length = len(answer_text)
        st.caption(f"回答字数：{answer_length} 字 · 耗时：{elapsed_time} 秒")
        
        st.session_state.history.append({
            "time": time.strftime("%H:%M:%S"),
            "role": st.session_state.user_role,
            "question": final_input,
            "answer": answer_text
        })
        
        if not st.session_state.conversations:
            st.session_state.conversations.append({
                "id": 1,
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "role": st.session_state.user_role,
                "records": [
                    {
                        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "question": final_input,
                        "answer": answer_text
                    }
                ]
            })
        else:
            st.session_state.conversations[-1]["records"].append({
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "question": final_input,
                "answer": answer_text
            })
    
    render_history()


if __name__ == "__main__":
    main()
