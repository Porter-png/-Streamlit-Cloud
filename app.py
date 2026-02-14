# -*- coding: utf-8 -*-
import streamlit as st
from config import APP_TITLE, APP_ICON

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="target",
    layout="centered"
)

st.title(f"{APP_ICON} {APP_TITLE}")
st.caption("AI驱动的数学提分诊断 - DSE/高考数学专家")

# 侧边栏
with st.sidebar:
    st.header("关于")
    st.info("""
    这是Porter开发的AI诊断工具，
    帮助找出孩子提分最快的知识点。

    [诊断] 预览版 (30%)
    [完整版] 添加微信领取

    PorterTeacher
    """)

# 主界面
tab1, tab2 = st.tabs(["开始诊断", "关于工具"])

with tab1:
    st.header("数学提分潜力诊断")

    # 输入表单
    with st.form("diagnosis_form"):
        name = st.text_input("学生姓名")
        grade = st.selectbox("年级", ["高二", "高三", "DSE中六", "DSE中七"])

        col1, col2 = st.columns(2)
        with col1:
            score = st.number_input("最近一次数学成绩", 0, 160, value=80)
        with col2:
            total = st.number_input("试卷满分", 100, 160, value=150)

        st.subheader("常错题型（多选）")
        wrong_topics = st.multiselect(
            "选择孩子常错的题型",
            ["函数与导数", "三角函数", "数列", "解析几何", "概率统计", "立体几何"],
            default=[]
        )

        submitted = st.form_submit_button("开始AI诊断", type="primary")

        if submitted:
            if not wrong_topics:
                st.error("请至少选择一个错题类型")
            else:
                # 显示进度
                with st.spinner("AI正在分析中..."):
                    import time
                    time.sleep(2)

                # 显示结果（预览版）
                st.success("诊断完成！")

                st.subheader("诊断结果（预览版）")

                score_pct = score / total * 100
                st.markdown(f"""
                **学生：** {name}

                **当前水平：** {score}/{total} ({score_pct:.1f}%)

                **主要问题：**
                - {wrong_topics[0] if wrong_topics else '无明显问题'}
                - {wrong_topics[1] if len(wrong_topics) > 1 else ''}

                **提分建议：**
                1. 优先突破 {wrong_topics[0] if wrong_topics else '基础概念'}
                2. 每天练习30分钟
                3. 两周后复诊

                ---

                [完整版] 包含：
                - 详细知识漏洞分析
                - 个性化学习计划
                - 专属练习题库
                - 提分时间预测

                **添加张老师微信免费领取完整报告**
                """)

                st.code("xiaobo20230512", language="text")

with tab2:
    st.header("关于本工具")

    st.markdown("""
    ### 工具说明

    本工具由Porter（11年教学经验）开发，结合AI技术，
    帮助家长快速了解孩子的数学问题。

    ### 诊断原理

    1. 收集成绩和错题信息
    2. AI分析知识漏洞
    3. 生成个性化建议
    4. 推荐针对性练习

    ### 免费领取

    添加微信，Porter亲自为您解读报告。
    """)
