# -*- coding: utf-8 -*-
"""
DSE/高考数学提分潜力诊断工具
陈老师专属 - AI驱动的数学诊断系统
"""

import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance
import fitz  # PyMuPDF
import io
import re
import json
import time
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_LINE_SPACING

# ==================== 0. 核心配置 ====================
# 你的Gemini API密钥
GEMINI_API_KEY = "AIzaSyBcvLsNA4ZeLbxHjcWmx_Fy1OcXYS5z9J0"

# 你的微信号
WECHAT_ID = "xiaobo20230512"

# ==================== 1. UI 深度美化 ====================
st.set_page_config(
    page_title="陈老师数学诊断",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 全局深色动态背景 */
    @keyframes gradient-bg {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background: linear-gradient(-45deg, #0b0f19, #1b2735, #243b55, #141e30);
        background-size: 400% 400%;
        animation: gradient-bg 15s ease infinite;
        color: #e0e0e0;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Tab 按钮样式 */
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        border: 1px solid rgba(255,255,255,0.1);
        color: #aaa;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00C9FF, #92FE9D);
        color: #000 !important;
        font-weight: 700;
    }

    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] label {
        color: #E0E0E0 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="input"] > div,
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #111 !important;
        border: 1px solid #444 !important;
        color: #FFFFFF !important;
        border-radius: 4px !important;
    }

    /* 上传框样式 */
    [data-testid='stFileUploader'] * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    [data-testid='stUploadedFileItem'] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid #00C9FF !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    [data-testid='stFileUploader'] button {
        background: linear-gradient(90deg, #00C9FF, #5EE7DF) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: 800 !important;
    }
    [data-testid='stFileUploader'] section {
        background-color: rgba(30, 34, 45, 0.6);
        border: 1px dashed rgba(0, 201, 255, 0.5) !important;
        border-radius: 10px;
        padding: 25px 20px !important;
    }

    /* 全局按钮样式 */
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(90deg, #00C9FF, #92FE9D) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
    }

    /* 标题样式 */
    h1 {
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.2rem;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* 提示框样式 */
    [data-testid="stAlert"] > div, [data-testid="stAlert"] p {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 2. 辅助函数 ====================
def call_ai_with_retry(model, prompt, content_list=None):
    """带重试的AI调用"""
    max_retries = 3
    retry_delay = 30

    for attempt in range(max_retries):
        try:
            if content_list:
                return model.generate_content([prompt] + content_list)
            else:
                return model.generate_content(prompt)
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                placeholder = st.empty()
                progress_text = f"⚠️ API正忙，自动排队中... (尝试 {attempt+1}/{max_retries})"
                my_bar = placeholder.progress(0, text=progress_text)
                for i in range(retry_delay):
                    time.sleep(1)
                    my_bar.progress((i+1)/retry_delay, text=f"⏳ 剩余 {retry_delay-i}s")
                placeholder.empty()
                continue
            else:
                raise e

def enhance_image_for_ocr(pil_image):
    """增强图像用于OCR识别"""
    enhancer = ImageEnhance.Contrast(pil_image)
    img = enhancer.enhance(1.5)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    return img

def process_pdf_bytes(file_bytes, start_page, end_page):
    """处理PDF文件，提取图像"""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    total_pages = len(doc)
    start = max(0, start_page - 1)
    end = min(total_pages, end_page)

    images = []
    enhanced_images = []

    for i in range(start, end):
        try:
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=200)
            img_data = pix.tobytes("png")
            original = Image.open(io.BytesIO(img_data))

            # 缩放过大的图片
            if original.width > 2000:
                ratio = 2000 / original.width
                new_size = (2000, int(original.height * ratio))
                original = original.resize(new_size, Image.Resampling.LANCZOS)

            images.append(original)
            enhanced_images.append(enhance_image_for_ocr(original))
            del pix, img_data
        except Exception as e:
            st.error(f"页码 {i+1} 处理错误: {e}")

    doc.close()
    return images, enhanced_images

def create_radar_chart_image(scores):
    """创建雷达图"""
    labels = list(scores.keys())
    values = list(scores.values())
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.grid(color='#E9E9E9', linestyle='-', linewidth=1.0)
    ax.spines['polar'].set_visible(False)

    ax.plot(angles, values, color='#0066CC', linewidth=2.5, linestyle='-', zorder=10)
    ax.fill(angles, values, color='#0066CC', alpha=0.15)
    ax.scatter(angles, values, color='#0066CC', s=80, edgecolors='white', linewidth=2, zorder=11)
    ax.set_ylim(0, 100)

    try:
        font_prop = FontProperties(fname=r"C:\Windows\Fonts\msyh.ttc", size=14)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontproperties=font_prop, color='black', weight='bold')
    except:
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, color='black', weight='bold')

    ax.tick_params(pad=30)
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight', dpi=300, facecolor='white')
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

def set_font(run, font_name_cn, font_name_en='Times New Roman', size_pt=10.5, bold=False, color=None):
    """设置Word字体"""
    run.font.name = font_name_en
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name_cn)
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color

def create_word_docx_simple(report_text, student_name, radar_img_stream=None):
    """创建简化的Word文档（Linux兼容版本）"""
    doc = Document()

    # 添加标题
    title = doc.add_heading(level=1)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = title.add_run(f"{student_name} 数学诊断报告")
    run.font.size = Pt(18)
    run.bold = True

    # 添加雷达图
    if radar_img_stream:
        try:
            radar_img_stream.seek(0)
            doc.add_picture(radar_img_stream, width=Inches(4.5))
        except:
            pass

    # 添加内容
    lines = report_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith("```"):
            continue

        if line.startswith('# '):
            p = doc.add_heading(level=1)
            run = p.add_run(line.replace('# ', ''))
            run.font.size = Pt(18)
            run.bold = True
        elif line.startswith('## '):
            p = doc.add_heading(level=2)
            run = p.add_run(line.replace('## ', ''))
            run.font.size = Pt(15)
            run.bold = True
        elif line.startswith('### '):
            p = doc.add_heading(level=3)
            run = p.add_run(line.replace('### ', ''))
            run.font.size = Pt(12)
            run.bold = True
        else:
            p = doc.add_paragraph()
            p.add_run(line)

    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    return doc_io

# ==================== 3. AI Prompts ====================
def get_quick_diagnosis_prompt(student_info):
    """快速诊断Prompt（预览版）"""
    return f"""
你是陈老师，一位有11年经验的DSE/高考数学专家。

根据以下学生信息，进行快速数学诊断：

【学生信息】
{student_info}

【任务】
请生成一份简明的数学诊断报告（预览版），包含：

1. **当前水平评估**（1-2句话）
2. **主要问题识别**（3个要点）
3. **提分建议**（3条具体建议）
4. **能力雷达图评分**（JSON格式，6个维度各0-100分）

【输出格式】
# {student_info.get('name', '同学')} 数学诊断报告（预览版）

## 一、当前水平评估
[评估内容]

## 二、主要问题识别
1. [问题1]
2. [问题2]
3. [问题3]

## 三、提分建议
1. [建议1]
2. [建议2]
3. [建议3]

## 四、完整报告
⚠️ 这是预览版（30%内容）。完整版包含：
- 详细知识漏洞分析
- 个性化学习计划
- 专属练习题库
- 提分时间预测

**添加陈老师微信免费领取完整报告：{WECHAT_ID}**

---JSON_START---
{{"代数运算": 70, "几何直观": 60, "逻辑推理": 65, "数据分析": 55, "数学建模": 50, "创新意识": 60}}
"""

def get_full_diagnosis_prompt(student_info, verified_data=None):
    """完整诊断Prompt"""
    data_str = json.dumps(verified_data, ensure_ascii=False) if verified_data else "无详细数据"

    return f"""
你是陈老师，一位有11年经验的DSE/高考数学专家。

【学生信息】
{student_info}

【题目数据】
{data_str}

【任务】
请生成一份**完整的数学诊断报告**，包含：

1. **总体表现概览**
   - 试卷得分/正确率
   - 总体评价

2. **逐题深度分析**（如果有题目数据）
   - 每道题的核心考点
   - 诊断分析
   - 复习建议

3. **能力薄弱点诊断**

4. **巩固知识与优势识别**

5. **阶段性复习建议与行动方案**
   - 基础夯实阶段（2-3周）
   - 能力提升阶段（3-4周）
   - 应试与策略优化

6. **总结与展望**

【输出格式】
使用Markdown格式，最后附上能力雷达图的JSON数据。
"""

# ==================== 4. 主界面 ====================
with st.sidebar:
    st.markdown("### ⚙️ 诊断设置")

    exam_type = st.selectbox(
        "考试类型",
        ("DSE - 必修数学", "DSE - 延伸M1", "DSE - 延伸M2", "高考 - 数学")
    )

    student_name = st.text_input("学生姓名", value="同学")

    st.markdown("---")
    st.info(f"""
    ### 👨‍🏫 关于陈老师

    - 11年数学教学经验
    - 3年DSE国际教育经验
    - 专业：DSE延伸数学

    微信：**{WECHAT_ID}**
    """)

# ==================== 主内容区 ====================
st.title("🧬 DSE/高考数学提分潜力诊断")

# 两种诊断模式
mode = st.radio(
    "选择诊断模式",
    ["📝 快速诊断（免费）", "📄 深度诊断（上传试卷）"],
    horizontal=True,
    label_visibility="collapsed"
)

# ==================== 模式1：快速诊断 ====================
if mode == "📝 快速诊断（免费）":
    st.markdown("""
    <div class="glass-card">
        <h3>🚀 快速诊断 - 免费体验</h3>
        <p>填写基本信息，AI快速分析提分潜力</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        recent_score = st.number_input("最近一次数学成绩", 0, 160, value=80, step=1)
    with col2:
        total_score = st.number_input("试卷满分", 60, 160, value=150, step=1)

    wrong_topics = st.multiselect(
        "常错题型（可多选）",
        ["函数与导数", "三角函数", "数列", "解析几何", "概率统计", "立体几何", "延伸数学-微积分", "延伸数学-代数"],
        default=[]
    )

    learning_goal = st.selectbox(
        "学习目标",
        ["夯实基础", "提升成绩", "冲刺高分", "DSE延伸数学入门"]
    )

    if st.button("🚀 开始免费诊断", type="primary"):
        if not wrong_topics:
            st.error("请至少选择一个错题类型")
        else:
            student_info = {
                "name": student_name,
                "score": recent_score,
                "total": total_score,
                "wrong_topics": wrong_topics,
                "goal": learning_goal,
                "exam_type": exam_type
            }

            with st.status("🤖 AI正在分析...", expanded=True) as status:
                st.write("1. 分析成绩数据...")
                time.sleep(0.5)
                st.write("2. 识别薄弱环节...")
                time.sleep(0.5)
                st.write("3. 生成诊断报告...")

                try:
                    genai.configure(api_key=GEMINI_API_KEY)
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    prompt = get_quick_diagnosis_prompt(student_info)
                    response = call_ai_with_retry(model, prompt)
                    full_text = response.text

                    # 提取JSON部分
                    if "---JSON_START---" in full_text:
                        parts = full_text.split("---JSON_START---")
                        body = parts[0].strip()
                        json_str = parts[1].strip().replace("```json", "").replace("```", "").strip()
                    else:
                        body = full_text
                        json_str = '{"代数运算": 60, "几何直观": 60, "逻辑推理": 60, "数据分析": 60, "数学建模": 60, "创新意识": 60}'

                    # 解析雷达图数据
                    try:
                        radar_data = json.loads(json_str)
                    except:
                        radar_data = {"代数运算": 60, "几何直观": 60, "逻辑推理": 60, "数据分析": 60, "数学建模": 60, "创新意识": 60}

                    st.session_state['report_text'] = body
                    st.session_state['radar_img'] = create_radar_chart_image(radar_data)
                    st.session_state['student_name'] = student_name

                    st.toast("✅ 诊断完成！", icon="🎉")
                    status.update(label="✅ 诊断完成！", state="complete")
                    st.rerun()

                except Exception as e:
                    st.error(f"诊断失败: {e}")

    # 显示报告
    if 'report_text' in st.session_state:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"<div class='glass-card'>{st.session_state['report_text']}</div>", unsafe_allow_html=True)
        with c2:
            if 'radar_img' in st.session_state:
                st.image(st.session_state['radar_img'], caption="能力维度分析")

        # 下载按钮（预览版）
        docx_file = create_word_docx_simple(
            st.session_state['report_text'],
            st.session_state.get('student_name', '同学'),
            st.session_state.get('radar_img')
        )
        st.download_button(
            label="📥 下载预览报告",
            data=docx_file,
            file_name=f"{st.session_state.get('student_name', '同学')}_诊断报告_预览版.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # 完整版引导
        st.markdown("""
        <div style='background: linear-gradient(90deg, rgba(0,201,255,0.2), rgba(146,254,157,0.2));
                   padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px;'>
            <h3>🔥 想要完整报告？</h3>
            <p>完整版包含详细知识漏洞分析、个性化学习计划、专属练习题库</p>
            <p style='font-size: 1.2rem; font-weight: bold; margin: 15px 0;'>
                添加陈老师微信：<span style='color: #00C9FF;'>{WECHAT_ID}</span>
            </p>
            <p>备注【提分】免费领取完整报告</p>
        </div>
        """.format(WECHAT_ID=WECHAT_ID), unsafe_allow_html=True)

# ==================== 模式2：深度诊断 ====================
else:
    st.markdown("""
    <div class="glass-card">
        <h3>📄 深度诊断 - 上传试卷</h3>
        <p>上传试卷图片/PDF，AI逐题分析</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "📂 上传试卷图片或PDF",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        help="支持PDF、PNG、JPG格式"
    )

    if uploaded_file:
        file_bytes = uploaded_file.getvalue()

        # 检测文件类型
        if uploaded_file.type == "application/pdf":
            doc_temp = fitz.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc_temp)
            doc_temp.close()

            st.info(f"📄 检测到PDF文件，共 {total_pages} 页")

            page_range = st.slider("选择页面", 1, total_pages, (1, min(3, total_pages)))

            if st.button("🚀 开始深度分析", type="primary"):
                with st.status("🔍 正在分析试卷...", expanded=True) as status:
                    st.write("1. 处理图像...")
                    images, enhanced = process_pdf_bytes(file_bytes, page_range[0], page_range[1])

                    st.write("2. AI识别题目...")
                    try:
                        genai.configure(api_key=GEMINI_API_KEY)
                        model = genai.GenerativeModel('gemini-2.0-flash')

                        # 构建诊断Prompt
                        student_info = {
                            "name": student_name,
                            "exam_type": exam_type,
                            "pages": f"{page_range[0]}-{page_range[1]}"
                        }
                        prompt = get_full_diagnosis_prompt(student_info)

                        response = call_ai_with_retry(model, prompt, enhanced)
                        full_text = response.text

                        st.session_state['report_text'] = full_text
                        st.session_state['student_name'] = student_name

                        st.toast("✅ 分析完成！", icon="🎉")
                        status.update(label="✅ 分析完成！", state="complete")
                        st.rerun()

                    except Exception as e:
                        st.error(f"分析失败: {e}")

        else:
            # 图片文件
            st.info(f"📷 检测到图片文件")
            st.image(uploaded_file, caption="上传的试卷", use_container_width=True)

            if st.button("🚀 开始分析", type="primary"):
                with st.status("🔍 正在分析..."):
                    try:
                        genai.configure(api_key=GEMINI_API_KEY)
                        model = genai.GenerativeModel('gemini-2.0-flash')

                        # 处理图片
                        image = Image.open(io.BytesIO(file_bytes))
                        enhanced = enhance_image_for_ocr(image)

                        student_info = {"name": student_name, "exam_type": exam_type}
                        prompt = get_full_diagnosis_prompt(student_info)

                        response = call_ai_with_retry(model, prompt, [enhanced])
                        full_text = response.text

                        st.session_state['report_text'] = full_text
                        st.session_state['student_name'] = student_name

                        st.toast("✅ 分析完成！", icon="🎉")
                        st.rerun()

                    except Exception as e:
                        st.error(f"分析失败: {e}")

    # 显示深度报告
    if 'report_text' in st.session_state:
        st.markdown(f"<div class='glass-card'>{st.session_state['report_text']}</div>", unsafe_allow_html=True)

        docx_file = create_word_docx_simple(
            st.session_state['report_text'],
            st.session_state.get('student_name', '同学')
        )

        st.download_button(
            label="📥 下载完整报告",
            data=docx_file,
            file_name=f"{st.session_state.get('student_name', '同学')}_深度诊断报告.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary"
        )

# ==================== 底部信息 ====================
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.8rem; margin-top: 50px; padding: 20px;'>
    <p>🧬 DSE/高考数学诊断工具 | 陈老师开发</p>
    <p>微信：{WECHAT_ID} | 备注【提分】领取完整报告</p>
</div>
""".format(WECHAT_ID=WECHAT_ID), unsafe_allow_html=True)
