import streamlit as st

# 页面标题
st.title("小航AI助手 - 基础测试Demo")

# 分栏布局
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("请输入你的名字", placeholder="")
with col2:
    grade = st.selectbox("请选择你的年级", ["大一", "大二", "大三", "大四", "研究生"])

# 打招呼按钮
if st.button("点我打招呼👋"):
    if name:
        st.success(f"你好呀，{grade}的{name}同学！欢迎使用小航AI助手😊")
    else:
        st.warning("请先输入你的名字哦~")

# 折叠面板展示额外信息
with st.expander("查看更多测试功能"):
    st.markdown("""
    ✅ 文本输入框
    ✅ 下拉选择框
    ✅ 按钮交互
    ✅ 分栏布局
    ✅ 折叠面板
    ✅ 成功/警告提示框
    """)